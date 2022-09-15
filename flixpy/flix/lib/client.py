from collections.abc import Mapping
import dataclasses
import json
from typing import Any, cast

import aiohttp
import dateutil.parser

from . import signing, errors, forms


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


class Client:
    """A thin wrapper around aiohttp.ClientSession, providing automatic signing of requests
    and a helper function for authenticating."""

    def __init__(
        self,
        hostname: str,
        port: int,
        ssl: bool = False,
        *,
        access_key: AccessKey | None = None,
    ):
        """
        Instantiate a new Flix client.
        :param hostname: The hostname of the Flix server
        :param port: The port the server is running on
        :param ssl: Whether to use HTTPS to communicate with the server
        :param access_key: The access key of an already authenticated user.
        """
        self._hostname = hostname
        self._port = port
        self._ssl = ssl
        self._access_key = access_key
        self._session = aiohttp.ClientSession()

    @property
    def access_key(self) -> AccessKey | None:
        """The access key if authenticated; None otherwise."""
        return self._access_key

    async def _request(self, method: str, path: str, body: Any | None = None, **kwargs) -> aiohttp.ClientResponse:
        data = json.dumps(body) if body is not None else None
        headers = {"Content-Type": "application/json"}
        if self._access_key is not None:
            headers.update(
                signing.sign_request(
                    self._access_key.id,
                    self._access_key.secret_access_key,
                    method,
                    path,
                    data,
                    "application/json",
                )
            )

        url = "{}://{}:{}{}".format("https" if self._ssl else "http", self._hostname, self._port, path)
        response = await self._session.request(method, url, data=data, headers=headers, **kwargs)
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
                raise errors.FlixError(response.status, error_message)

        return response

    async def request(self, method: str, path: str, body: Any | None = None, **kwargs) -> aiohttp.ClientResponse:
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

    async def request_json(self, method: str, path: str, body: Any | None = None, **kwargs) -> dict[str, Any]:
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
        return await response.json()

    async def get(self, path: str, body: Any | None = None, **kwargs) -> dict[str, Any]:
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

    async def post(self, path: str, body: Any | None = None, **kwargs) -> dict[str, Any]:
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

    async def patch(self, path: str, body: Any | None = None, **kwargs) -> dict[str, Any]:
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

    async def put(self, path: str, body: Any | None = None, **kwargs) -> dict[str, Any]:
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

    async def delete(self, path: str, body: Any | None = None, **kwargs) -> aiohttp.ClientResponse:
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

    async def text(self, path: str, *, method: str = "GET", **kwargs) -> str:
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

    async def form(self, path) -> forms.Form:
        """
        Fetch the appropriate creation form for the given path.

        :param path: The path to return the creation form for; should not include /form
        :raises errors.FlixNotVerifiedError: If the client failed to authenticate
        :raises errors.FlixError: If the server returned an error
        :return: A object representing the creation form for the path
        """
        resp = await self.get(f"{path}/form")
        return forms.Form(cast(dict[str, Any], resp))

    async def authenticate(self, user, password):
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
        response = await self._request(
            "POST", "/authenticate", auth=aiohttp.BasicAuth(user, password)
        )
        self._access_key = AccessKey(response)

    async def close(self):
        """Closes the underlying HTTP session. Does not need to be called when using the client as a context manager."""
        await self._session.close()

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
