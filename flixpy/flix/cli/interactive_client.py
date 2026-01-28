"""A client that supports interactive authentication."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import asyncclick as click

from ..lib import client, errors, models

if TYPE_CHECKING:
    import aiohttp

__all__ = ["InteractiveClient"]


class InteractiveClient(client.Client):
    """An interactive Flix client that will automatically handle authentication.

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
        access_key: models.AccessKey | None = None,
    ) -> None:
        super().__init__(
            hostname,
            port,
            ssl=ssl,
            access_key=client.AccessKey(access_key) if access_key else None,
            disable_ssl_validation=config.get("disable_ssl_validation", False),
        )
        self.__config = config
        self.__username = username
        self.__password = password

    async def _sign_in(self) -> None:
        click.echo("Not signed in, attempting to authenticate...", err=True)
        self.__config.pop("access_key", None)

        username = self.__username or click.prompt("Username", type=str, err=True)
        password = self.__password or click.prompt("Password", type=str, hide_input=True, err=True)
        access_key = await self.authenticate(username, password)
        self.__config["access_key"] = access_key.to_json()

    async def request(self, *args: Any, **kwargs: Any) -> aiohttp.ClientResponse:
        try:
            return await super().request(*args, **kwargs)
        except errors.FlixNotVerifiedError:
            await self._sign_in()
            return await super().request(*args, **kwargs)
