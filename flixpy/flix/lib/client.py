"""Utilities for connecting to and authenticating with the Flix Server."""

from __future__ import annotations

import asyncio
import base64
import contextlib
import dataclasses
import datetime
import json
import logging
import urllib.parse
import warnings
from collections.abc import AsyncIterator, Mapping
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar, cast

import aiohttp
import dateutil.parser

from . import _utils, errors, forms, models, signing, types, websocket

if TYPE_CHECKING:
    from types import TracebackType

__all__ = ["Client", "AccessKey"]

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AccessKey:
    """Holds information about a user session."""

    def __init__(self, access_key: dict[str, Any]) -> None:
        """Constructs a new AccessKey object.

        Args:
            access_key: The deserialised response from authenticating with a Flix server.
        """
        self.id: str = access_key["id"]
        """The ID used to identify the access key."""
        self.secret_access_key: str = access_key["secret_access_key"]
        """The secret used to sign requests."""
        self.created_date = dateutil.parser.parse(access_key["created_date"])
        """When the access key was created."""
        self.expiry_date = dateutil.parser.parse(access_key["expiry_date"])
        """When the access key expires."""

    @property
    def has_expired(self) -> bool:
        """Whether this access key has expired."""
        now = datetime.datetime.now(datetime.timezone.utc)
        return self.expiry_date < now

    def to_json(self) -> dict[str, Any]:
        """Returns a JSON-serialisable representation of this access key.

        The output of this can be passed to the constructor to construct
        an AccessKey object from JSON.
        """
        return {
            "id": self.id,
            "secret_access_key": self.secret_access_key,
            "created_date": self.created_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
        }


ClientSelf = TypeVar("ClientSelf", bound="BaseClient")


class BaseClient:
    """Base class for [flix.Client][].

    A thin wrapper around aiohttp.ClientSession that provides
    automatic signing of Flix requests and a helper function for authenticating..
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        ssl: bool = False,
        disable_ssl_validation: bool = False,
        *,
        username: str | None = None,
        password: str | None = None,
        auto_extend_session: bool = True,
        access_key: AccessKey | None = None,
    ) -> None:
        """Instantiate a new Flix client.

        Args:
            hostname: The hostname of the Flix server.
            port: The port the server is running on.
            ssl: Whether to use HTTPS to communicate with the server.
            disable_ssl_validation: Whether to disable validation of SSL certificates.
                Enables MITM attacks.
            username: The user to authenticate as. If provided, the client will automatically
                authenticate whenever we don't have a valid session.
            password: The password for the user to authenticate as. Must be provided
                if ``username`` is provided.
            auto_extend_session: Automatically keep the session alive by periodically extending
                the access key validity time following a successful authentication.
            access_key: The access key of an already authenticated user.
        """
        self._hostname = hostname
        self._port = port
        self._ssl = ssl
        self._disable_ssl_validation = disable_ssl_validation
        self._username = username
        self._password = password
        self._auto_extend_session = auto_extend_session
        self._access_key = access_key

        self._session = aiohttp.ClientSession()
        self._refresh_token_task: asyncio.Task[None] | None = None

    @property
    def access_key(self) -> AccessKey | None:
        """The access key if authenticated; ``None`` otherwise."""
        return self._access_key

    @property
    def hostname(self) -> str:
        """The Flix Server hostname."""
        return self._hostname

    @property
    def port(self) -> int:
        """The Flix Server port."""
        return self._port

    @property
    def ssl(self) -> bool:
        """Whether to use HTTPS for requests."""
        return self._ssl

    async def _request(
        self,
        method: str,
        path: str,
        body: Any | None = None,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        data = json.dumps(body) if body is not None else None
        flix_headers = {"Content-Type": "application/json", **(headers or {})}
        split = urllib.parse.urlsplit(path)
        if self._access_key is not None:
            flix_headers.update(
                signing.sign_request(
                    self._access_key.id,
                    self._access_key.secret_access_key,
                    method,
                    split.path,
                    data,
                    "application/json",
                )
            )

        url = urllib.parse.urlunsplit(
            (
                "https" if self._ssl else "http",
                f"{self._hostname}:{self._port}",
                split.path,
                split.query,
                split.fragment,
            )
        )
        response = await self._session.request(
            method,
            url,
            data=data,
            headers=flix_headers,
            ssl=False if self._disable_ssl_validation else None,
            **kwargs,
        )
        if response.status >= HTTPStatus.BAD_REQUEST:
            if response.content_type == "application/json":
                error = await response.json()
                if isinstance(error, Mapping) and "message" in error:
                    error_message = error["message"]
                else:
                    error_message = str(error)
            else:
                error_message = await response.text()
            if response.status == HTTPStatus.UNAUTHORIZED:
                self._access_key = None
                raise errors.FlixNotVerifiedError(response.status, error_message)
            else:
                raise errors.FlixHTTPError(response.status, error_message)

        return response

    async def request(
        self, method: str, path: str, body: Any | None = None, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """Perform an HTTP request against the Flix server.

        This method may be safely overridden in a subclass to modify the request behaviour.
        Do not call functions such as get or post from an implementation of request
        to avoid infinite recursion.

        Args:
            method: The HTTP method.
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The HTTP response.
        """
        # authenticate if auto auth is enabled and we don't have a valid access key
        await self._ensure_authenticated()
        try:
            return await self._request(method, path, body, **kwargs)
        except errors.FlixNotVerifiedError:
            # if our access key was rejected it will be cleared by _request, so try again
            if not await self._ensure_authenticated():
                raise
            return await self._request(method, path, body, **kwargs)

    async def request_json(
        self, method: str, path: str, body: Any | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Perform an HTTP request against the Flix server and parse the result as JSON.

        Args:
            method: The HTTP method
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response parsed as JSON.
        """
        response = await self.request(method, path, body, **kwargs)
        return cast(dict[str, Any], await response.json())

    async def get(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a GET request against the Flix server.

        Args:
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response parsed as JSON.
        """
        return await self.request_json("GET", path, body, **kwargs)

    async def post(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a POST request against the Flix server.

        Args:
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response parsed as JSON.
        """
        return await self.request_json("POST", path, body, **kwargs)

    async def patch(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a PATCH request against the Flix server.

        Args:
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response parsed as JSON.
        """
        return await self.request_json("PATCH", path, body, **kwargs)

    async def put(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a PUT request against the Flix server.

        Args:
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response parsed as JSON.
        """
        return await self.request_json("PUT", path, body, **kwargs)

    async def delete(
        self, path: str, body: Any | None = None, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """Perform a DELETE request against the Flix server.

        Args:
            path: The path to request; should not include the server hostname.
            body: A JSON-serialisable object to be used as the payload.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The HTTP response.
        """
        return await self.request("DELETE", path, body, **kwargs)

    async def text(self, path: str, *, method: str = "GET", **kwargs: Any) -> str:
        """Perform a request against the Flix server and parse the result as text.

        Args:
            path: The path to request; should not include the server hostname.
            method: The HTTP method.
            kwargs: Additional arguments passed to aiohttp.ClientSession.request.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            The response payload as text.
        """
        response = await self.request(method, path, **kwargs)
        return await response.text()

    async def form(self, path: str) -> forms.Form:
        """Fetch the appropriate creation form for the given path.

        Args:
            path: The path to return the creation form for; should not include /form.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            A object representing the creation form for the path.
        """
        resp = await self.get(f"{path}/form")
        return forms.Form(cast(forms.FormSectionModel, resp))

    async def authenticate(self, user: str, password: str) -> AccessKey:
        """Authenticate as a Flix user.

        On a successful authentication, this will set access_key.

        Args:
            user: The username of the user to authenticate as.
            password: The password of the user to authenticate as.

        Raises:
            errors.FlixNotVerifiedError: If the client failed to authenticate.
            errors.FlixError: If the server returned an error.

        Returns:
            A new access key for the user.
        """
        self._access_key = None
        # call _request directly to avoid recursion when automatically authenticating
        response = await self._request(
            "POST", "/authenticate", auth=aiohttp.BasicAuth(user, password)
        )
        self._access_key = AccessKey(await response.json())

        if self._refresh_token_task is None and self._auto_extend_session:
            self._refresh_token_task = asyncio.create_task(self._periodically_refresh_token())

        return self._access_key

    async def _ensure_authenticated(self) -> bool:
        """Authenticate with the Flix Server if we have no valid access key.

        Returns:
            ``True`` if a successful authentication attempt was performed;
                ``False`` if no attempt was made because the access key is still valid
                or automatic authentication is disabled.
        """
        if (
            (self._access_key is None or self._access_key.has_expired)
            and self._username is not None
            and self._password is not None
        ):
            await self.authenticate(self._username, self._password)
            return True
        return False

    async def extend_session(self) -> None:
        """Extend the current login session to 24 hours from now.

        If the current access key is not valid, this method does nothing.
        """
        if self._access_key is None:
            return

        # a FlixNotVerifiedError means the access key has expired,
        # in which case we'll reauthenticate before the next request
        with contextlib.suppress(errors.FlixNotVerifiedError):
            self._access_key = AccessKey(await self.post("/authenticate/extend"))

    async def _periodically_refresh_token(self) -> None:
        """Try to extend the session once an hour."""
        refresh_frequency_seconds = 60 * 60
        while True:
            await asyncio.sleep(refresh_frequency_seconds)

            if self._access_key is not None:
                try:
                    await self.extend_session()
                except Exception:
                    logger.exception(
                        "error while trying to extend the current session, "
                        "will try again in %s seconds",
                        refresh_frequency_seconds,
                    )

    async def aclose(self) -> None:
        """Close the underlying HTTP session.

        Does not need to be called when using the client as a context manager.
        """
        if self._refresh_token_task is not None:
            self._refresh_token_task.cancel()

        await self._session.close()

    async def close(self) -> None:
        """Deprecated. Use [aclose][flix.Client.aclose]."""
        warnings.warn("Use Client.aclose()", DeprecationWarning, stacklevel=1)
        await self.aclose()

    async def __aenter__(self: ClientSelf) -> ClientSelf:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()


class Client(BaseClient):
    """An HTTP client for communicating with the Flix Server.

    Provides various helper functions for interacting with Flix's
    HTTP API and translating the responses to more Pythonic types.

    Example:
        ```python
        async with Client("localhost", 8080) as client:
            await client.authenticate("admin", "admin")

            # print the tracking code of all shows
            shows = await client.get_all_shows()
            for show in shows:
                print(show.tracking_code)
        ```
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        ssl: bool = False,
        disable_ssl_validation: bool = False,
        *,
        username: str | None = None,
        password: str | None = None,
        auto_extend_session: bool = True,
        access_key: AccessKey | None = None,
    ) -> None:
        """Instantiate a new Flix client.

        Args:
            hostname: The hostname of the Flix server.
            port: The port the server is running on.
            ssl: Whether to use HTTPS to communicate with the server.
            disable_ssl_validation: Whether to disable validation of SSL certificates.
                Enables MITM attacks.
            username: The user to authenticate as. If provided, the client will automatically
                authenticate whenever we don't have a valid session.
            password: The password for the user to authenticate as. Must be provided
                if ``username`` is provided.
            auto_extend_session: Automatically keep the session alive by periodically extending
                the access key validity time following a successful authentication.
            access_key: The access key of an already authenticated user.
        """
        super().__init__(
            hostname=hostname,
            port=port,
            ssl=ssl,
            disable_ssl_validation=disable_ssl_validation,
            username=username,
            password=password,
            auto_extend_session=auto_extend_session,
            access_key=access_key,
        )

    @contextlib.asynccontextmanager
    async def websocket(self) -> AsyncIterator[websocket.Websocket]:
        """Open a new websocket connection to listen for server events.

        Returns:
            A websocket object from which you can asynchronously read events.
        """
        await self._ensure_authenticated()
        async with websocket.Websocket(self._session, self) as ws:
            yield ws

    async def get_all_shows(self, include_hidden: bool = False) -> list[types.Show]:
        """Get all shows visible to the user.

        Args:
            include_hidden: Include shows marked as hidden.

        Returns:
            A list of shows.
        """

        class _AllShows(TypedDict):
            shows: list[models.Show]

        params = {"display_hidden": "true" if include_hidden else "falsae"}
        shows = cast(_AllShows, await self.get("/shows", params=params))
        return [types.Show.from_dict(show, _client=self) for show in shows["shows"]]

    async def get_show(self, show_id: int) -> types.Show:
        """Get a show by ID.

        Args:
            show_id: The ID of the show to fetch.

        Returns:
            The show matching the given ID.
        """
        show = cast(models.Show, await self.get(f"/show/{show_id}"))
        return types.Show.from_dict(show, _client=self)

    async def get_asset(self, asset_id: int) -> types.Asset:
        """Get an asset by ID.

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            The asset matching the given ID.
        """
        asset = cast(models.Asset, await self.get(f"/asset/{asset_id}"))
        return types.Asset.from_dict(asset, _client=self)

    async def get_media_object(self, media_object_id: int) -> types.MediaObject:
        """Get a media object by ID.

        Args:
            media_object_id: The ID of the media object to fetch.

        Returns:
            The media object with the given ID.
        """
        media_object = cast(models.MediaObject, await self.get(f"/file/{media_object_id}"))
        return types.MediaObject.from_dict(media_object, _client=self)

    def new_show(
        self,
        tracking_code: str,
        aspect_ratio: float = 1.77,
        frame_rate: float = 24,
        title: str = "",
        description: str = "",
        episodic: bool = False,
    ) -> types.Show:
        """Create a new show.

        This method will not automatically save the new show.

        Args:
            tracking_code: The tracking code of the show.
            aspect_ratio: The aspect ratio of the show.
            frame_rate: The frame rate of the show.
            title: The title of the show.
            description: A description.
            episodic: Whether the show is episodic.

        Returns:
            A new, unsaved [Show][flix.Show] object.
        """
        return types.Show(
            tracking_code=tracking_code,
            aspect_ratio=aspect_ratio,
            frame_rate=frame_rate,
            title=title or tracking_code,
            description=description,
            episodic=episodic,
            _client=self,
        )

    async def restore_archive(self, archive_path: str) -> types.Show:
        """Restore an archive as a new show.

        Args:
            archive_path: The path to the archive on the Flix Server.

        Returns:
            The restored show.
        """
        path = "/show/restore"
        async with self.websocket() as ws:
            await self.post(
                path,
                headers={"Flix-Client-Id": ws.client_id},
                body={"archive_path": archive_path},
            )
            complete_msg: websocket.MessageArchiveRestored = await ws.wait_on_chain(
                websocket.MessageArchiveRestored
            )

        return await self.get_show(complete_msg.show_id)

    async def get_all_users(self) -> list[types.User]:
        """Get all users visible to the authenticated user.

        Returns:
            A list of users.
        """

        class _AllUsers(TypedDict):
            users: list[models.User]

        users = cast(_AllUsers, await self.get("/users"))
        return [types.User.from_dict(user, _client=self) for user in users["users"]]

    def new_user(
        self,
        username: str,
        password: str,
        email: str = "",
        is_admin: bool = False,
        groups: list[types.GroupRolePair] | None = None,
    ) -> types.User:
        return types.User(
            username=username,
            password=password,
            email=email,
            is_admin=is_admin,
            groups=groups,
            _client=self,
        )

    async def get_all_groups(
        self, with_permission: types.Permission | None = None
    ) -> list[types.Group]:
        class _AllGroups(TypedDict):
            groups: list[models.Group]

        params = None
        if with_permission is not None:
            perm = json.dumps(with_permission.to_dict())
            params = {"permissions": base64.b64encode(perm.encode()).decode()}
        groups = cast(_AllGroups, await self.get("/groups", params=params))
        return [types.Group.from_dict(group) for group in groups["groups"]]

    @_utils.cache(30)
    async def servers(self) -> list[types.Server]:
        class _Servers(TypedDict):
            servers: list[models.Server]

        path = "/servers"
        servers = cast(_Servers, await self.get(path))
        return [types.Server.from_dict(server) for server in servers["servers"]]
