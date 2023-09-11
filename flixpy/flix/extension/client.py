from types import TracebackType

from typing import TypeVar, cast

import httpx

from ..lib import errors

from . import extension_api
from .extension_api import models, types as api_types

from . import types

__all__ = [
    "Extension",
]

BASE_URL = "http://localhost:3000"

T = TypeVar("T")
U = TypeVar("U")


def _assert_ok(resp: api_types.Response[U]) -> None:
    if resp.status_code < 200 or resp.status_code >= 300:
        raise errors.FlixHTTPError(resp.status_code, resp.content.decode())


def _assert_response(expect: type[T], resp: api_types.Response[U]) -> T:
    _assert_ok(resp)

    if resp.parsed is not None:
        return cast(T, resp.parsed)

    raise errors.FlixError("expected response type {}, got: {!r}".format(expect, resp.content))


class Extension:
    """This class provides functions for interacting with the Flix Client, useful for implementing extensions that
    communicate with Flix.

    The class is best used as an extension manager in a with statement::

        with Extension("My Extension", client_uid="97c8fd5d-c1f8-4561-9268-8701b5fa48d4") as extension:
            await extension.import_panels(["/path/to/image.png"])

    If you need a long-lived object, however, you can use the object as-is, as long as you remember to
    call close when you're done::

        extension = Extension("My Extension", client_uid="97c8fd5d-c1f8-4561-9268-8701b5fa48d4")
        await extension.import_panels(["/path/to/image.png"])
        await extension.close()

    :param name: The name of the extension
    :param client_uid: A unique ID for the extension; should remain unchanged for a given extension
    :param version: An optional version string for the extension
    :param base_url: The URL to use to connect to the Flix Client, if something other than
        the standard Flix Client port on localhost
    """

    def __init__(
        self,
        name: str,
        client_uid: str,
        version: str | None = None,
        base_url: str = BASE_URL,
    ) -> None:
        self.name = name
        self.client_uid = client_uid
        self.version = version
        self.base_url = base_url
        self._client = extension_api.Client(base_url=self.base_url)
        self._registered_client: extension_api.AuthenticatedClient | None = None

    async def register(self) -> None:
        """Registers the extension with the Flix Client.

        This method does not need to be called manually, as the extension will be automatically registered
        when attempting to use a method that requires authorisation, but it can be useful if you want to ensure
        that the registration succeeded before continuing with further initialisation of your extension.
        """
        await self._get_registered_client()

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
                ),
            ),
        )

        self._registered_client = extension_api.AuthenticatedClient(self.base_url, resp.token)
        return self._registered_client

    async def health_check(self) -> None:
        """Checks if the Flix Client is currently running and accepting remote API requests.

        :raises errors.FlixError: If the client is not running
        """
        from .extension_api.api.health_check import health_check_controller_health_check

        try:
            resp = await health_check_controller_health_check.asyncio_detailed(client=self._client)
            if resp.status_code != 200:
                raise errors.FlixHTTPError(resp.status_code, resp.content.decode())
        except httpx.HTTPError as e:
            raise errors.FlixError("error when attempting to connect to the Flix Client") from e

    async def get_registered_extensions(self) -> list[models.RegistrationDetails]:
        """Returns a list of extensions currently registered with the Flix Client."""
        from .extension_api.api.api_registration import registration_controller_get_all

        return _assert_response(
            list[models.RegistrationDetails],
            await registration_controller_get_all.asyncio_detailed(client=await self._get_registered_client()),
        )

    async def get_project_details(self) -> types.ProjectDetails:
        """Returns details about the currently open show, episode, sequence and/or sequence revision.

        :return: An object containing information about the currently open project.
        """
        from .extension_api.api.project_details import project_controller_get

        resp = _assert_response(
            models.ProjectDetailsDto,
            await project_controller_get.asyncio_detailed(client=await self._get_registered_client()),
        )

        return types.ProjectDetails.from_model(resp)

    async def import_panels(
        self,
        paths: list[str],
        source_file: types.SourceFile | None = None,
        start_index: int | None = None,
        replace_panels: bool = False,
    ) -> None:
        """Instructs the Flix Client to import the given files as panel revisions.

        :param paths: A list of absolute paths to files to import
        :param source_file: The file to use as the source file for the imported panels
        :param start_index: If specified, panels will be inserted at the given index
            instead of the currently selected panel index
        :param replace_panels: If True, version up existing panels instead of inserting new ones
        """
        from .extension_api.api.panel_management import panel_controller_create, panel_controller_update

        json_body = models.PanelRequest(
            paths=paths,
            source_file=models.PanelRequestSourceFile(
                id=source_file.id,
                path=source_file.path,
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

    async def download(self, asset_id: int, asset_type: models.DownloadRequestAssetType, target_folder: str) -> None:
        """Instructs the Flix Client to download an asset to a local directory.

        :param asset_id: The ID of the asset to download
        :param asset_type: The type of asset (media object) to download
        :param target_folder: The directory to download the asset to
        """
        from .extension_api.api.media_object_download import download_controller_download_media_object

        _assert_ok(
            await download_controller_download_media_object.asyncio_detailed(
                client=await self._get_registered_client(),
                json_body=models.DownloadRequest(
                    asset_id=asset_id,
                    asset_type=asset_type,
                    target_folder=target_folder,
                ),
            ),
        )

    async def close(self) -> None:
        """Closes the underlying HTTP clients."""
        await self._client.get_async_httpx_client().aclose()
        if self._registered_client is not None:
            await self._registered_client.get_async_httpx_client().aclose()

    async def __aenter__(self) -> "Extension":
        await self._client.__aenter__()
        await self.register()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
        if self._registered_client is not None:
            await self._registered_client.__aexit__(exc_type, exc_val, exc_tb)
