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

from . import errors, forms, models, signing, types, utils, websocket

if TYPE_CHECKING:
    from types import TracebackType

__all__ = ["Client", "AccessKey"]

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AccessKey:
    """Holds information about a user session."""

    def __init__(self, access_key: dict[str, Any]) -> None:
        """Constructs a new AccessKey object.

        :param access_key: The deserialised response from authenticating with a Flix server
        """
        self.id: str = access_key["id"]
        self.secret_access_key: str = access_key["secret_access_key"]
        self.created_date = dateutil.parser.parse(access_key["created_date"])
        self.expiry_date = dateutil.parser.parse(access_key["expiry_date"])

    @property
    def has_expired(self) -> bool:
        """Whether this access key has expired."""
        now = datetime.datetime.now(datetime.timezone.utc)
        return self.expiry_date < now

    def to_json(self) -> dict[str, Any]:
        """Returns a JSON-serialisable representation of this access key.
        The output of this can be passed to the constructor to construct an AccessKey object from JSON."""
        return {
            "id": self.id,
            "secret_access_key": self.secret_access_key,
            "created_date": self.created_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
        }


ClientSelf = TypeVar("ClientSelf", bound="BaseClient")


class BaseClient:
    """A thin wrapper around aiohttp.ClientSession, providing automatic signing of requests
    and a helper function for authenticating."""

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

        :param hostname: The hostname of the Flix server
        :param port: The port the server is running on
        :param ssl: Whether to use HTTPS to communicate with the server
        :param disable_ssl_validation: Whether to disable validation of SSL certificates; enables MITM attacks
        :param username: The user to authenticate as. If provided, the client will automatically
            authenticate whenever we don't have a valid session.
        :param password: The password for the user to authenticate as. Must be provided if ``username`` is provided.
        :param auto_extend_session: Automatically keep the session alive by periodically extending
            the access key validity time following a successful authentication.
        :param access_key: The access key of an already authenticated user.
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
        """The access key if authenticated; None otherwise."""
        return self._access_key

    @property
    def hostname(self) -> str:
        return self._hostname

    @property
    def port(self) -> int:
        return self._port

    @property
    def ssl(self) -> bool:
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
                "{}:{}".format(self._hostname, self._port),
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
        if response.status >= 400:
            if response.content_type == "application/json":
                error = await response.json()
                if isinstance(error, Mapping) and "message" in error:
                    error_message = error["message"]
                else:
                    error_message = str(error)
            else:
                error_message = await response.text()
            if response.status == 401:
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
        Do not call functions such as get or post from an implementation of request to avoid infinite recursion.

        :param method: The HTTP method
        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The HTTP response
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

        :param method: The HTTP method
        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        response = await self.request(method, path, body, **kwargs)
        return cast(dict[str, Any], await response.json())

    async def get(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a GET request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("GET", path, body, **kwargs)

    async def post(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a POST request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("POST", path, body, **kwargs)

    async def patch(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a PATCH request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("PATCH", path, body, **kwargs)

    async def put(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Perform a PUT request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("PUT", path, body, **kwargs)

    async def delete(
        self, path: str, body: Any | None = None, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """Perform a DELETE request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The HTTP response
        """
        return await self.request("DELETE", path, body, **kwargs)

    async def text(self, path: str, *, method: str = "GET", **kwargs: Any) -> str:
        """Perform a request against the Flix server and parse the result as text.

        :param path: The path to request; should not include the server hostname
        :param method: The HTTP method
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response payload as text
        """
        response = await self.request(method, path, **kwargs)
        return await response.text()

    async def form(self, path: str) -> forms.Form:
        """Fetch the appropriate creation form for the given path.

        :param path: The path to return the creation form for; should not include /form
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: A object representing the creation form for the path
        """
        resp = await self.get(f"{path}/form")
        return forms.Form(cast(forms.FormSectionModel, resp))

    async def authenticate(self, user: str, password: str) -> AccessKey:
        """Authenticate as a Flix user.

        On a successful authentication, this will set access_key.

        :param user: The username of the user to authenticate as
        :param password: The password of the user to authenticate as
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
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

        try:
            self._access_key = AccessKey(await self.post("/authenticate/extend"))
        except errors.FlixNotVerifiedError:
            # the access key has expired; we'll reauthenticate before the next request
            pass

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
        """Deprecated. Use ``aclose()``."""
        warnings.warn("Use Client.aclose()", DeprecationWarning)
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
    """An extension of BaseClient, providing helper functions for interacting with the Flix API."""

    @contextlib.asynccontextmanager
    async def websocket(self) -> AsyncIterator[websocket.Websocket]:
        await self._ensure_authenticated()
        async with websocket.Websocket(self._session, self) as ws:
            yield ws

    async def get_all_shows(self, include_hidden: bool = False) -> list[types.Show]:
        params = {"display_hidden": "true" if include_hidden else "falsae"}
        all_shows_model = TypedDict("all_shows_model", {"shows": list[models.Show]})
        shows = cast(all_shows_model, await self.get("/shows", params=params))
        return [types.Show.from_dict(show, _client=self) for show in shows["shows"]]

    async def get_show(self, show_id: int) -> types.Show:
        show = cast(models.Show, await self.get(f"/show/{show_id}"))
        return types.Show.from_dict(show, _client=self)

    async def get_asset(self, asset_id: int) -> types.Asset:
        asset = cast(models.Asset, await self.get(f"/asset/{asset_id}"))
        return types.Asset.from_dict(asset, _client=self)

    async def get_media_object(self, media_object_id: int) -> types.MediaObject:
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
        return types.Show(
            tracking_code=tracking_code,
            aspect_ratio=aspect_ratio,
            frame_rate=frame_rate,
            title=title or tracking_code,
            description=description,
            episodic=episodic,
            _client=self,
        )

    async def get_all_users(self) -> list[types.User]:
        all_users_model = TypedDict("all_users_model", {"users": list[models.User]})
        users = cast(all_users_model, await self.get("/users"))
        return [types.User.from_dict(user, _client=self) for user in users["users"]]

    async def new_user(
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
        params = None
        if with_permission is not None:
            perm = json.dumps(with_permission.to_dict())
            params = {"permissions": base64.b64encode(perm.encode()).decode()}
        all_groups_model = TypedDict("all_groups_model", {"groups": list[models.Group]})
        groups = cast(all_groups_model, await self.get("/groups", params=params))
        return [types.Group.from_dict(group) for group in groups["groups"]]

    @utils.cache(30)
    async def servers(self) -> list[types.Server]:
        path = "/servers"
        servers_model = TypedDict("servers_model", {"servers": list[models.Server]})
        servers = cast(servers_model, await self.get(path))
        return [types.Server.from_dict(server) for server in servers["servers"]]
