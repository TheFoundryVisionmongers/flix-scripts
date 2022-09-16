import asyncio
import json
import pathlib
import ssl
import urllib.parse
from typing import Any, cast, TypedDict

import aiohttp.web
import appdirs
import asyncclick as click

from . import interactive_client
from ..lib import client, errors, forms, webhooks, models

_CONFIG_DIR = pathlib.Path(appdirs.user_config_dir("flix-cli", "foundry"))
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def read_config() -> dict[str, Any]:
    try:
        with _CONFIG_FILE.open("r") as f:
            return cast(dict[str, Any], json.load(f))
    except FileNotFoundError:
        return {}


def write_config(cfg: dict[str, Any]) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with _CONFIG_FILE.open("w") as f:
        json.dump(cfg, f, indent=2)


async def get_client(ctx: click.Context, server: str | None = None) -> client.Client:
    server = server or ctx.obj["server"]
    if server is None:
        raise click.UsageError("server not specified in config or as an option")

    parsed = urllib.parse.urlparse(server)
    if not parsed.hostname:
        raise click.UsageError(f"missing hostname in server URL: {server}")

    return interactive_client.InteractiveClient(
        hostname=parsed.hostname,
        port=parsed.port or 80,
        ssl=parsed.scheme == "https",
        config=ctx.obj["config"],
        username=ctx.obj.get("username"),
        password=ctx.obj.get("password"),
    )


@click.group()
@click.option("-s", "--server", type=str, help="The URL of the Flix server.")
@click.option("-u", "--username", type=str, help="The username to authenticate with.")
@click.option("-p", "--password", type=str, help="The password to authenticate with.")
@click.pass_context
async def flix_cli(ctx: click.Context, server: str | None, username: str | None, password: str | None) -> None:
    cfg = read_config()
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg
    ctx.obj["server"] = server or cfg.get("server")
    ctx.obj["username"] = username or cfg.get("username")
    ctx.obj["password"] = password or cfg.get("password")


@flix_cli.result_callback()
@click.pass_context
def save_config(ctx: click.Context, *args: Any, **kwargs: Any) -> None:
    write_config(ctx.obj["config"])
    pass


@flix_cli.command("config", help="Set default configuration values.")
@click.option("-s", "--server", type=str, help="The default server URL.")
@click.option("-u", "--username", type=str, help="The default username.")
@click.option("-p", "--password", type=str, help="The default password.")
@click.option("--clear", is_flag=True, help="Clear the config.")
@click.pass_context
def config(
    ctx: click.Context,
    server: str | None,
    username: str | None,
    password: str | None,
    clear: bool,
) -> None:
    cfg = ctx.obj["config"]
    if server:
        cfg["server"] = server
    if username:
        cfg["username"] = username
    if password:
        cfg["password"] = password
    if clear:
        cfg = {}
    ctx.obj["config"] = cfg


@flix_cli.command(help="Perform cURL-like requests to a Flix server.")
@click.argument("url")
@click.option(
    "-d",
    "--data",
    type=json.loads,
    help="A JSON object to use as the body of the request.",
)
@click.option(
    "-X",
    "--request",
    type=click.Choice(["GET", "POST", "PATCH", "PUT", "DELETE"]),
    help="The HTTP method. By default GET for requests with no payload, and POST for requests with a payload.",
)
@click.pass_context
async def curl(ctx: click.Context, url: str, data: Any | None, request: str | None) -> None:
    if request is None:
        request = "GET" if data is None else "POST"

    url_parse = urllib.parse.urlparse(url)
    server = url if url_parse.hostname else None
    path = url_parse.path

    async with await get_client(ctx, server=server) as flix_client:
        resp = await flix_client.request(request, path, body=data, parse_body=False)
        print(cast(bytes, resp).decode())


@flix_cli.group(help="Manage webhooks.")
def webhook() -> None:
    pass


@webhook.command("add", help="Add a new webhook.")
@click.pass_context
async def webhook_add(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        webhook_form = await flix_client.form("/webhook")
        data = webhook_form.prompt()
        click.echo(err=True)
        webhook_form.print(data, err=True)
        if click.confirm("Save webhook?", True, err=True):
            wh = await flix_client.post("/webhook", data)
            click.echo(f"New webhook secret: {wh['secret']}", err=True)
            click.echo(
                "Ensure that you have noted down the secret, as you will not be able to view it again.", err=True
            )


@webhook.command("list", help="List all webhooks.")
@click.pass_context
async def webhook_list(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        webhooks = await flix_client.get("/webhooks")
        webhook_form = await flix_client.form("/webhook")

        for i, wh in enumerate(webhooks["webhooks"]):
            click.echo("ID: {}".format(wh["id"]))
            webhook_form.print(wh)
            if i < len(webhooks["webhooks"]) - 1:
                click.echo()


_WebhookResponse = TypedDict("_WebhookResponse", {"webhooks": list[models.Webhook]})


@webhook.command("delete", help="Delete a webhook.")
@click.pass_context
async def webhook_delete(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        webhooks: _WebhookResponse = cast(_WebhookResponse, await flix_client.get("/webhooks"))
        if len(webhooks["webhooks"]) == 0:
            raise click.ClickException("No webhooks added.")
        webhook_form = await flix_client.form("/webhook")

        j = forms.prompt_enum(
            [forms.Choice(i, wh["name"]) for i, wh in enumerate(webhooks["webhooks"])],
            prompt="Which webhook do you want to delete?",
            prompt_suffix=" ",
        )
        wh = webhooks["webhooks"][j]
        webhook_form.print(wh, err=True)

        if click.confirm("Delete this webhook?", False, err=True):
            await flix_client.delete("/webhook/{}".format(webhooks["webhooks"][j]["id"]))
            click.echo("Deleted successfully. It may take a few seconds for your changes to be reflected.", err=True)


@webhook.command("edit", help="Edit a webhook.")
@click.pass_context
async def webhook_edit(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        webhooks: _WebhookResponse = cast(_WebhookResponse, await flix_client.get("/webhooks"))
        if len(webhooks["webhooks"]) == 0:
            raise click.ClickException("No webhooks added.")
        webhook_form = await flix_client.form("/webhook")

        j = forms.prompt_enum(
            [forms.Choice(i, wh["name"]) for i, wh in enumerate(webhooks["webhooks"])],
            prompt="Which webhook do you want to edit?",
            prompt_suffix=" ",
        )
        wh = webhooks["webhooks"][j]
        wh = webhook_form.prompt_edit(wh)
        await flix_client.put(f"/webhook/{wh['id']}", wh)
        click.echo("Saved successfully. It may take a few seconds for your changes to be reflected.", err=True)


@webhook.command("ping", help="Ping a webhook.")
@click.pass_context
async def webhook_ping(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        webhooks = cast(_WebhookResponse, await flix_client.get("/webhooks"))
        if len(webhooks["webhooks"]) == 0:
            raise click.ClickException("No webhooks added.")

        j = forms.prompt_enum(
            [forms.Choice(i, wh["name"]) for i, wh in enumerate(webhooks["webhooks"])],
            prompt="Which webhook do you want to ping?",
            prompt_suffix=" ",
        )
        wh = webhooks["webhooks"][j]
        print(await flix_client.post(f"/webhook/{wh['id']}", wh))


@webhook.command("run_server", help="")
@click.argument("path", type=str)
@click.option("-p", "--port", type=int, default=8080)
@click.option("--address", type=str, default="0.0.0.0")
@click.option("--secret", type=str, required=True)
@click.option("--certfile", type=str)
@click.option("--keyfile", type=str)
async def webhook_server(
    path: str, port: int, address: str, secret: str, certfile: str | None, keyfile: str | None
) -> None:
    @webhooks.webhook(secret=secret)
    async def _handler(event: webhooks.WebhookEvent) -> None:
        click.echo(event.event_payload)

    ssl_context = None
    if certfile is not None:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile, keyfile)

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post(path, _handler)])
    # run application on current loop
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, address, port, ssl_context=ssl_context)
    await site.start()

    click.echo(f"Listening for events on {address}:{port} (press CTRL+C to abort)...", err=True)
    while True:
        await asyncio.sleep(3600)


def main() -> Any:
    try:
        return flix_cli(auto_envvar_prefix="FLIX", _anyio_backend="asyncio")
    except errors.FlixError as e:
        click.echo(str(e), err=True)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
