"""The implementation of a General Remote Client API client."""

from __future__ import annotations

import asyncio
import logging
import warnings
import weakref
from collections.abc import AsyncIterable, AsyncIterator, Coroutine
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar, cast

import httpx
import socketio
from typing_extensions import Self

from ..lib import errors
from . import extension_api, types
from .extension_api import models
from .extension_api import types as api_types

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)

__all__ = [
    "Extension",
]

BASE_URL = "http://localhost:3000"

T = TypeVar("T")
U = TypeVar("U")


def _assert_ok(resp: api_types.Response[U]) -> None:
    if resp.status_code < HTTPStatus.OK or resp.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        raise errors.FlixHTTPError(resp.status_code, resp.content.decode())


def _assert_response(expect: type[T], resp: api_types.Response[U]) -> T:
    _assert_ok(resp)

    if resp.parsed is not None:
        return cast(T, resp.parsed)

    raise errors.FlixError(f"expected response type {expect}, got: {resp.content!r}")


_ET_co = TypeVar("_ET_co", bound=types.Event, covariant=True)


class EventQueue(AsyncIterable[_ET_co]):
    """An EventQueue listens for events of one or more given types.

    Events can be read from a queue by iterating over the object using async for.
    If you need to ensure that the queue has started listening for events before
    performing some action, you can use it as a context manager using the async with statement::

        async with extension.events(
            ActionEvent
        ) as events:
            # now we are already listening for events,
            # so we won't miss any action events from the import
            await extension.import_panels(
                ["/path/to/image.png"]
            )

            async for action_event in events:
                print("Got event:", action_event)
    """

    def __init__(self, ext: Extension, *event_types: type[_ET_co]) -> None:
        self._ext = ext
        self._queue: asyncio.Queue[types.Event] | None = asyncio.Queue()
        self._event_types = event_types

        self._done = asyncio.Future[None]()
        self._ext.register_queue(self)

    def put(self, event: types.Event) -> None:
        if self._queue is not None:
            self._queue.put_nowait(event)

    def close(self) -> None:
        self._ext.unregister_queue(self)
        self._done.cancel()
        self._queue = None

    async def __aenter__(self) -> EventQueue[_ET_co]:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    async def _until_cancelled(self, cor: Coroutine[Any, Any, T]) -> T:
        """Cancel a coroutine if this EventQueue is closed."""
        task = asyncio.create_task(cor)

        def _cancel(_: asyncio.Future[None]) -> None:
            task.cancel()

        self._done.add_done_callback(_cancel)
        try:
            return await task
        finally:
            self._done.remove_done_callback(_cancel)

    async def __aiter__(self) -> AsyncIterator[_ET_co]:
        while self._queue is not None:
            try:
                event = await self._until_cancelled(self._queue.get())
            except asyncio.CancelledError:
                break

            if isinstance(event, self._event_types):
                yield event

            if self._queue is not None:
                self._queue.task_done()


class Extension:
    """Provides functions for communicating with the Flix Client from remote extensions.

    The class is best used as a context manager in a with statement:

    ```py
    with Extension(
        name="My Extension",
        client_uid="97c8fd5d-c1f8-4561-9268-8701b5fa48d4",
    ) as extension:
        await extension.import_panels(
            ["/path/to/image.png"]
        )
    ```

    If you need a long-lived object, however, you can use the object as-is,
    as long as you remember to call close when you're done:

    ```python
    extension = Extension(
        name="My Extension",
        client_uid="97c8fd5d-c1f8-4561-9268-8701b5fa48d4",
    )
    await extension.import_panels(
        ["/path/to/image.png"]
    )
    await extension.close()
    ```
    """

    def __init__(
        self,
        name: str,
        client_uid: str,
        log_paths: list[str] | None = None,
        version: str | None = None,
        base_url: str = BASE_URL,
    ) -> None:
        """Initialise an Extension.

        Args:
            name: The name of the extension
            client_uid: A unique ID for the extension; should remain unchanged for a given extension
            log_paths: List of paths to the extension's log files
            version: An optional version string for the extension
            base_url: The URL to use to connect to the Flix Client, if something other than
                the standard Flix Client port on localhost

        """
        self.name = name
        self.client_uid = client_uid
        self.version = version
        self.base_url = base_url
        self.log_paths = log_paths
        self.panel_browser_status = types.PanelBrowserStatus()
        self.project = types.ProjectDetails()
        self._online = False

        self._client = extension_api.Client(base_url=self.base_url)
        self._registered_client: extension_api.AuthenticatedClient | None = None
        self.sio = socketio.AsyncClient()
        self._register_events()
        self._queues = weakref.WeakSet[EventQueue[types.Event]]()
        self._connection_task: asyncio.Task[None] | None = None

    def _reset_status(self) -> None:
        self.online = False
        self.panel_browser_status = types.PanelBrowserStatus()
        self.project = types.ProjectDetails()

    async def _update_status(self) -> None:
        try:
            self.panel_browser_status = await self.get_status()
            self.project = await self.get_project_details()
        except (errors.FlixError, httpx.HTTPError) as e:
            logger.warning("couldn't update Flix Client status on connect: %s", e)

    def _register_events(self) -> None:
        self.sio.on("message", self._on_message)
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("unauthorised", self._on_unauthorized)

    @property
    def online(self) -> bool:
        return self._online

    @online.setter
    def online(self, value: bool) -> None:
        if value != self._online:
            self._online = value
            self._broadcast_event(types.ConnectionEvent(self._online))

    @property
    def status(self) -> types.Status:
        status = types.Status(0)

        if self.online:
            status |= types.Status.ONLINE
        if self.project.sequence_revision is None:
            status |= types.Status.NO_REVISION
        if not self.panel_browser_status.can_create:
            status |= types.Status.NO_PERMISSION
        if len(self.panel_browser_status.revision_status.selected_panels) > 1:
            status |= types.Status.MULTIPLE_PANELS_SELECTED

        ready = types.Status.ONLINE
        not_ready = types.Status.NO_PERMISSION | types.Status.NO_REVISION
        if (status & ready) > 0 and (status & not_ready) == 0:
            status |= types.Status.READY_TO_SEND

        return status

    async def _on_connect(self) -> None:
        logger.info("connected to Flix Client, subscribing to events")
        events = models.SubscribeRequest(
            event_types=[
                types.ClientEventType.STATUS,
                types.ClientEventType.PROJECT,
                types.ClientEventType.ACTION,
                types.ClientEventType.OPEN,
            ],
        )
        await self.sio.emit("subscribe", data=events.to_dict())

    async def _on_disconnect(self) -> None:
        logger.warning("disconnected from Flix Client")
        self._reset_status()

    async def _on_unauthorized(self) -> None:
        logger.warning("extension is unauthorised, attempting to re-register")
        self._reset_status()
        # connect in background
        self.register()

    async def _on_message(self, event_data: dict[str, Any]) -> None:
        if not self.online:
            # set online here rather than in _on_connect,
            # since we still get a connect event if unauthorised
            self.online = True
            await self._update_status()

        try:
            event = types.ClientEvent.parse_event(event_data)
        except ValueError as e:
            logger.warning("dropping unsupported event: %s (%s)", event_data, e)
            return

        logger.debug("got %s event: %s", type(event).__name__, event)

        if isinstance(event, types.StatusEvent):
            self.panel_browser_status = event
        elif isinstance(event, types.ProjectEvent):
            self.project = event

        self._broadcast_event(event)

    def _broadcast_event(self, event: types.Event) -> None:
        for queue in self._queues:
            queue.put(event)

    def events(self, *event_types: type[_ET_co]) -> EventQueue[_ET_co]:
        """Create an EventQueue that listens to events of the given type(s)."""
        return EventQueue(self, *event_types)

    def register_queue(self, queue: EventQueue[types.Event]) -> None:
        """Instruct this Extension instance to forward events to the given queue.

        This method should not generally be called manually.
        """
        self._queues.add(queue)

    def unregister_queue(self, queue: EventQueue[types.Event]) -> None:
        """Instruct this Extension instance to stop forwarding events to the given queue.

        This method should not generally be called manually.
        """
        self._queues.discard(queue)

    async def _try_connect(self) -> None:
        if self.online:
            return

        await self.sio.disconnect()
        self._registered_client = None
        while True:
            try:
                registered_client = await self._get_registered_client()
            except (errors.FlixError, httpx.HTTPError):
                logger.debug("could not connect to client, waiting 10 seconds before retrying...")
                await asyncio.sleep(10)
                continue

            break

        await self._update_status()
        await self.sio.connect(self.base_url, auth={"token": registered_client.token})

    def register(self) -> asyncio.Task[None]:
        """Establish a connection to the Flix Client.

        This method will register the extension with the Flix Client and start listening
        for websocket events. When using the Extension instance as a context method
        (using the with statement), this method does not need to be called explicitly.

        If already connected to the Flix Client, this method is a no-op.

        This method will return immediately and attempt to connect to the Flix Client
        in the background.

        Returns:
            A [Task][asyncio.Task] object that completes when a successful connection
                has been established. It can be awaited to ensure that the registration
                succeeded before proceeding.
        """
        if self._connection_task:
            return self._connection_task

        def _clear_task(_: asyncio.Task[None]) -> None:
            self._connection_task = None

        self._connection_task = asyncio.create_task(self._try_connect())
        self._connection_task.add_done_callback(_clear_task)
        return self._connection_task

    async def _get_registered_client(self) -> extension_api.AuthenticatedClient:
        if self._registered_client is not None:
            return self._registered_client

        from .extension_api.api.api_registration import registration_controller_register_client

        resp = _assert_response(
            models.RegistrationResponse,
            await registration_controller_register_client.asyncio_detailed(
                client=self._client,
                json_body=models.RegistrationRequest(
                    name=self.name,
                    client_uid=self.client_uid,
                    version=self.version or api_types.UNSET,
                    log_paths=self.log_paths or api_types.UNSET,
                ),
            ),
        )

        self._registered_client = extension_api.AuthenticatedClient(self.base_url, resp.token)
        return self._registered_client

    async def health_check(self) -> None:
        """Check if the Flix Client is currently running and accepting remote API requests.

        Raises:
            errors.FlixError: If the client is not running
        """
        from .extension_api.api.health_check import health_check_controller_health_check

        try:
            resp = await health_check_controller_health_check.asyncio_detailed(client=self._client)
            if resp.status_code != HTTPStatus.OK:
                raise errors.FlixHTTPError(resp.status_code, resp.content.decode())
        except httpx.HTTPError as e:
            raise errors.FlixError("error when attempting to connect to the Flix Client") from e

    async def get_registered_extensions(self) -> list[models.RegistrationDetails]:
        """Get a list of extensions currently registered with the Flix Client."""
        from .extension_api.api.api_registration import registration_controller_get_all

        return _assert_response(
            list[models.RegistrationDetails],
            await registration_controller_get_all.asyncio_detailed(
                client=await self._get_registered_client()
            ),
        )

    async def get_project_details(self) -> types.ProjectDetails:
        """Get details about the currently open show, episode, sequence and/or sequence revision.

        Returns:
            An object containing information about the currently open project.
        """
        from .extension_api.api.project_details import project_controller_get

        resp = _assert_response(
            models.ProjectDetailsDto,
            await project_controller_get.asyncio_detailed(
                client=await self._get_registered_client()
            ),
        )

        return types.ProjectDetails.from_model(resp)

    async def get_status(self) -> types.PanelBrowserStatus:
        """Get details about the current status of the Flix Client.

        Returns:
            An object containing information about the current Flix Client status.
        """
        from .extension_api.api.status import status_controller_get

        resp = _assert_response(
            models.StatusResponse,
            await status_controller_get.asyncio_detailed(
                client=await self._get_registered_client()
            ),
        )

        return types.PanelBrowserStatus.from_model(resp)

    async def import_panels(
        self,
        paths: list[str],
        origin: str,
        source_file: types.SourceFile | None = None,
        start_index: int | None = None,
        replace_panels: bool = False,
    ) -> None:
        """Instructs the Flix Client to import the given files as panel revisions.

        Args:
            paths: A list of absolute paths to files to import.
            origin: The name of the application that the panels originate from.
            source_file: The file to use as the source file for the imported panels.
            start_index: If specified, panels will be inserted at the given index.
                instead of the currently selected panel index.
            replace_panels: If True, version up existing panels instead of inserting new ones.
        """
        from .extension_api.api.panel_management import (
            panel_controller_create,
            panel_controller_update,
        )

        json_body = models.BulkPanelRequest(
            paths=paths,
            origin=origin,
            source_file=models.PanelRequestSourceFile(
                path=source_file.path,
                preview_mode=source_file.preview_mode,
                source_file_type=source_file.source_file_type,
            )
            if source_file is not None
            else api_types.UNSET,
            start_index=start_index if start_index is not None else api_types.UNSET,
        )

        if not replace_panels:
            _assert_ok(
                await panel_controller_create.asyncio_detailed(
                    client=await self._get_registered_client(), json_body=json_body
                )
            )
        else:
            _assert_ok(
                await panel_controller_update.asyncio_detailed(
                    client=await self._get_registered_client(), json_body=json_body
                )
            )

    async def download(
        self,
        asset_id: int,
        asset_type: types.AssetType,
        target_folder: str,
    ) -> types.DownloadResponse:
        """Instruct the Flix Client to download an asset to a local directory.

        Args:
            asset_id: The ID of the asset to download.
            asset_type: The type of asset (media object) to download.
            target_folder: The directory to download the asset to.

        Returns:
            Information about the downloaded file.
        """
        from .extension_api.api.media_object_download import (
            download_controller_download_media_object,
        )

        resp = _assert_response(
            models.DownloadResponse,
            await download_controller_download_media_object.asyncio_detailed(
                client=await self._get_registered_client(),
                json_body=models.DownloadRequest(
                    asset_id=asset_id,
                    asset_type=asset_type,
                    target_folder=target_folder,
                ),
            ),
        )

        return types.DownloadResponse.from_dict(resp)

    async def _aclose(self) -> None:
        # convert set to list to avoid modifying set while iterating over it
        for queue in list(self._queues):
            queue.close()
        await self.sio.disconnect()

    async def aclose(self) -> None:
        """Closes the underlying HTTP and websocket clients."""
        await self._aclose()
        await self._client.get_async_httpx_client().aclose()
        if self._registered_client is not None:
            await self._registered_client.get_async_httpx_client().aclose()

    async def close(self) -> None:
        """Deprecated. Use [aclose][flix.Extension.aclose]."""
        warnings.warn("Use Extension.aclose()", DeprecationWarning, stacklevel=1)
        await self.aclose()

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        await self.register()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._aclose()
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
        if self._registered_client is not None:
            await self._registered_client.__aexit__(exc_type, exc_val, exc_tb)
