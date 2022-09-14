import json
import pathlib
import urllib.parse
from typing import Any

import appdirs
import asyncclick as click

from . import interactive_client
from ..lib import client, errors, forms

_CONFIG_DIR = pathlib.Path(appdirs.user_config_dir("flix-cli", "foundry"))
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def read_config():
    try:
        with _CONFIG_FILE.open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_config(cfg):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with _CONFIG_FILE.open("w") as f:
        json.dump(cfg, f, indent=2)


def parse_url(server: str | None) -> tuple[str, int, bool]:
    if server is None:
        raise click.UsageError("server not specified in config or as an option")

    parsed = urllib.parse.urlparse(server)
    return parsed.hostname, parsed.port or 80, parsed.scheme == "https"


async def get_client(ctx: click.Context, server=None) -> client.Client:
    server = server or ctx.obj["server"]
    hostname, port, ssl = parse_url(server)

    return interactive_client.InteractiveClient(
        hostname,
        port,
        ssl=ssl,
        config=ctx.obj["config"],
        username=ctx.obj.get("username"),
        password=ctx.obj.get("password"),
    )


@click.group()
@click.option("-s", "--server", type=str, help="The URL of the Flix server.")
@click.option("-u", "--username", type=str, help="The username to authenticate with.")
@click.option("-p", "--password", type=str, help="The password to authenticate with.")
@click.pass_context
async def flix_cli(
    ctx: click.Context, server: str | None, username: str | None, password: str | None
):
    cfg = read_config()
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg
    ctx.obj["server"] = server or cfg.get("server")
    ctx.obj["username"] = username or cfg.get("username")
    ctx.obj["password"] = password or cfg.get("password")


@flix_cli.result_callback()
@click.pass_context
def save_config(ctx: click.Context, *args, **kwargs):
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
):
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
async def curl(ctx: click.Context, url: str, data: Any | None, request: str | None):
    if request is None:
        request = "GET" if data is None else "POST"

    url_parse = urllib.parse.urlparse(url)
    server = url if url_parse.hostname else None
    path = url_parse.path

    async with await get_client(ctx, server=server) as flix_client:
        print(
            (
                await flix_client.request(request, path, body=data, parse_body=False)
            ).decode()
        )


@flix_cli.group(help="Manage webhooks.")
def webhook():
    pass


@webhook.command("add", help="Add a new webhook.")
@click.pass_context
async def webhook_add(ctx):
    async with await get_client(ctx) as flix_client:
        webhook_form = await flix_client.form("/webhook")
        data = webhook_form.prompt()
        click.echo()
        webhook_form.print(data)
        if click.confirm("Save webhook?", True):
            wh = await flix_client.post("/webhook", data)
            click.echo(f"New webhook secret: {wh['secret']}")
            click.echo(
                "Ensure that you have noted down the secret, as you will not be able to view it again."
            )


@webhook.command("list", help="List all webhooks.")
@click.pass_context
async def webhook_list(ctx):
    async with await get_client(ctx) as flix_client:
        webhooks = await flix_client.get("/webhooks")
        webhook_form = await flix_client.form("/webhook")

        for i, wh in enumerate(webhooks["webhooks"]):
            click.echo("ID: {}".format(wh["id"]))
            webhook_form.print(wh)
            if i < len(webhooks["webhooks"]) - 1:
                click.echo()


@webhook.command("delete", help="Delete a webhook.")
@click.pass_context
async def webhook_delete(ctx):
    async with await get_client(ctx) as flix_client:
        webhooks: dict[Any] = await flix_client.get("/webhooks")
        if len(webhooks["webhooks"]) == 0:
            raise click.ClickException("No webhooks added.")
        webhook_form = await flix_client.form("/webhook")

        j = forms.prompt_enum(
            [forms.Choice(i, wh["name"]) for i, wh in enumerate(webhooks["webhooks"])],
            prompt="Which webhook do you want to delete?",
            prompt_suffix=" ",
        )
        wh = webhooks["webhooks"][j]
        webhook_form.print(wh)

        if click.confirm("Delete this webhook?", False):
            await flix_client.delete(
                "/webhook/{}".format(webhooks["webhooks"][j]["id"])
            )
            click.echo(
                "Deleted successfully. It may take a few seconds for your changes to be reflected."
            )


@webhook.command("edit", help="Edit a webhook.")
@click.pass_context
async def webhook_edit(ctx):
    async with await get_client(ctx) as flix_client:
        webhooks: dict[Any] = await flix_client.get("/webhooks")
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
        click.echo(
            "Saved successfully. It may take a few seconds for your changes to be reflected."
        )


def main():
    try:
        return flix_cli(auto_envvar_prefix="FLIX", _anyio_backend="asyncio")
    except errors.FlixError as e:
        click.echo(str(e))
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
