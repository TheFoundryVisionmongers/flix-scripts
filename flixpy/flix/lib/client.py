import base64
import urllib.parse

from collections.abc import Mapping
import dataclasses
import json
from types import TracebackType
from typing import Any, cast, Type, TypedDict, TypeVar

import aiohttp
import dateutil.parser

from . import signing, errors, forms, types, models, utils, websocket

__all__ = ["Client", "AccessKey"]


@dataclasses.dataclass
class AccessKey:
    """Holds information about a user session."""

    def __init__(self, access_key: dict[str, Any]):
        """
        Constructs a new AccessKey object.
        :param access_key: The deserialised response from authenticating with a Flix server
        """
        self.id: str = access_key["id"]
        self.secret_access_key: str = access_key["secret_access_key"]
        self.created_date = dateutil.parser.parse(access_key["created_date"])
        self.expiry_date = dateutil.parser.parse(access_key["expiry_date"])

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
        access_key: AccessKey | None = None,
    ):
        """
        Instantiate a new Flix client.
        :param hostname: The hostname of the Flix server
        :param port: The port the server is running on
        :param ssl: Whether to use HTTPS to communicate with the server
        :param disable_ssl_validation: Whether to disable validation of SSL certificates; enables MITM attacks
        :param access_key: The access key of an already authenticated user.
        """
        self._hostname = hostname
        self._port = port
        self._ssl = ssl
        self._access_key = access_key
        self._session = aiohttp.ClientSession()
        self._disable_ssl_validation = disable_ssl_validation

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

    async def _request(self, method: str, path: str, body: Any | None = None, **kwargs: Any) -> aiohttp.ClientResponse:
        data = json.dumps(body) if body is not None else None
        headers = {"Content-Type": "application/json"}
        split = urllib.parse.urlsplit(path)
        if self._access_key is not None:
            headers.update(
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
            headers=headers,
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

    async def request(self, method: str, path: str, body: Any | None = None, **kwargs: Any) -> aiohttp.ClientResponse:
        """
        Perform an HTTP request against the Flix server.

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
        return await self._request(method, path, body, **kwargs)

    async def request_json(self, method: str, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """
        Perform an HTTP request against the Flix server and parse the result as JSON.

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
        """
        Perform a GET request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("GET", path, body, **kwargs)

    async def post(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """
        Perform a POST request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("POST", path, body, **kwargs)

    async def patch(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """
        Perform a PATCH request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("PATCH", path, body, **kwargs)

    async def put(self, path: str, body: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """
        Perform a PUT request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The response parsed as JSON
        """
        return await self.request_json("PUT", path, body, **kwargs)

    async def delete(self, path: str, body: Any | None = None, **kwargs: Any) -> aiohttp.ClientResponse:
        """
        Perform a DELETE request against the Flix server.

        :param path: The path to request; should not include the server hostname
        :param body: A JSON-serialisable object to be used as the payload
        :param kwargs: Additional arguments passed to aiohttp.ClientSession.request
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: The HTTP response
        """
        return await self.request("DELETE", path, body, **kwargs)

    async def text(self, path: str, *, method: str = "GET", **kwargs: Any) -> str:
        """
        Perform a request against the Flix server and parse the result as text.

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
        """
        Fetch the appropriate creation form for the given path.

        :param path: The path to return the creation form for; should not include /form
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: A object representing the creation form for the path
        """
        resp = await self.get(f"{path}/form")
        return forms.Form(cast(forms.FormSectionModel, resp))

    async def authenticate(self, user: str, password: str) -> AccessKey:
        """
        Authenticate as a Flix user.

        On a successful authentication, this will set access_key.

        :param user: The username of the user to authenticate as
        :param password: The password of the user to authenticate as
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        """
        self._access_key = None
        # call _request directly to avoid recursion during interactive sessions
        response = await self._request("POST", "/authenticate", auth=aiohttp.BasicAuth(user, password))
        self._access_key = AccessKey(await response.json())
        return self._access_key

    async def close(self) -> None:
        """Closes the underlying HTTP session. Does not need to be called when using the client as a context manager."""
        await self._session.close()

    async def __aenter__(self: ClientSelf) -> ClientSelf:
        return self

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        await self.close()


class Client(BaseClient):
    """An extension of BaseClient, providing helper functions for interacting with the Flix API."""

    def __init__(
        self,
        hostname: str,
        port: int,
        ssl: bool = False,
        disable_ssl_validation: bool = False,
        *,
        access_key: AccessKey | None = None,
    ):
        """
        Instantiate a new Flix client.
        :param hostname: The hostname of the Flix server
        :param port: The port the server is running on
        :param ssl: Whether to use HTTPS to communicate with the server
        :param disable_ssl_validation: Whether to disable validation of SSL certificates; enables MITM attacks
        :param access_key: The access key of an already authenticated user.
        """
        super().__init__(hostname, port, ssl, disable_ssl_validation=disable_ssl_validation, access_key=access_key)

    def websocket(self) -> websocket.Websocket:
        return websocket.Websocket(self._session, self)

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

    async def get_all_groups(self, with_permission: types.Permission | None = None) -> list[types.Group]:
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
