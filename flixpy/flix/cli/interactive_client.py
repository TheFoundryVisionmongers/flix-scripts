from typing import Any

import aiohttp
import asyncclick as click

from ..lib import client, errors


__all__ = ["InteractiveClient"]


class InteractiveClient(client.Client):
    """
    An interactive Flix client that will automatically handle authentication.

    The user will be prompted for authentication details if not specified elsewhere.
    The access key will be read from the configuration if available on initialisation,
    and saved to the configuration when closing the Flix session.
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        ssl: bool,
        config: dict[str, Any],
        username: str | None = None,
        password: str | None = None,
    ):
        try:
            access_key = client.AccessKey(config["access_key"])
        except KeyError:
            access_key = None

        super().__init__(
            hostname,
            port,
            ssl=ssl,
            access_key=access_key,
            disable_ssl_validation=config.get("disable_ssl_validation", False),
        )
        self._config = config
        self._username = username
        self._password = password

    async def _sign_in(self) -> None:
        click.echo("Not signed in, attempting to authenticate...", err=True)

        try:
            del self._config["access_key"]
        except KeyError:
            pass

        username = self._username or click.prompt("Username", type=str, err=True)
        password = self._password or click.prompt("Password", type=str, hide_input=True, err=True)
        access_key = await self.authenticate(username, password)
        self._config["access_key"] = access_key.to_json()

    async def request(self, *args: Any, **kwargs: Any) -> aiohttp.ClientResponse:
        try:
            return await super().request(*args, **kwargs)
        except errors.FlixNotVerifiedError:
            await self._sign_in()
            return await super().request(*args, **kwargs)
