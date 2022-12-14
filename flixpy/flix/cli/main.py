import base64

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

_CONFIG_DIR = pathlib.Path(appdirs.user_config_dir("flix-sdk", "foundry"))
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

    parsed = urllib.parse.urlsplit(server)
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
@click.option(
    "--disable-ssl-validation",
    type=bool,
    help="Disables validation of SSL certificates. WARNING: This option enables MITM attacks.",
)
@click.option("--clear", is_flag=True, help="Clear the config.")
@click.pass_context
def config(
    ctx: click.Context,
    server: str | None,
    username: str | None,
    password: str | None,
    disable_ssl_validation: bool,
    clear: bool,
) -> None:
    cfg = ctx.obj["config"]
    cfg["disable_ssl_validation"] = disable_ssl_validation
    if server:
        cfg["server"] = server
    if username:
        cfg["username"] = username
    if password:
        cfg["password"] = password
    if clear:
        cfg = {}
    ctx.obj["config"] = cfg


@flix_cli.command("logout", help="Log out the user from Flix by removing any active access key.")
@click.pass_context
def logout(ctx: click.Context) -> None:
    try:
        del ctx.obj["config"]["access_key"]
    except KeyError:
        pass


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

    url_parse = urllib.parse.urlsplit(url)
    server = url if url_parse.hostname else None
    path = urllib.parse.urlunsplit(("", "", url_parse.path, url_parse.query, url_parse.fragment))

    async with await get_client(ctx, server=server) as flix_client:
        resp = await flix_client.request(request, path, body=data)
        if resp.content_type in ("application/json", "text/plain"):
            click.echo(await resp.text())
        else:
            click.echo(await resp.read())


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


@webhook.command("server")
@click.argument("path", type=str)
@click.option("-p", "--port", type=int, default=8080, help="The port on which to listen for events.", show_default=True)
@click.option("--address", type=str, default="0.0.0.0", help="The address to listen on.", show_default=True)
@click.option(
    "--secret",
    type=str,
    required=True,
    help="The secret given when registering the webhook, used to authenticate events.",
)
@click.option("--certfile", type=str, help="Path to a signed certificate. Providing this will enable HTTPS.")
@click.option("--keyfile", type=str, help="Path to the private key used to sign the certificate.")
async def webhook_server(
    path: str, port: int, address: str, secret: str, certfile: str | None, keyfile: str | None
) -> None:
    """Run a test server that prints events to standard out.

    PATH should be the path of the endpoint that events will be posted to, not including the hostname, e.g. /events.
    """

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


@flix_cli.group(help="Manage contact sheet templates.")
def contactsheet() -> None:
    pass


async def contactsheet_edit_loop(
    flix_client: client.Client, contactsheet_form: forms.Form, data: models.ContactSheet
) -> models.ContactSheet:
    preview_file = "preview.pdf"
    while True:
        action = forms.prompt_enum(
            [forms.Choice("edit", "Edit"), forms.Choice("preview", "Preview"), forms.Choice("save", "Save")],
            prompt="What would you like to do?",
            prompt_suffix=" ",
        )
        if action == "edit":
            data = contactsheet_form.prompt_edit(data)
        elif action == "preview":
            preview_file = click.prompt(
                "Where would you like to save the preview?", default=preview_file, show_default=True
            )
            data_str = json.dumps(data)
            b64 = base64.b64encode(data_str.encode()).decode()
            pdf_response = await flix_client.request(
                "GET", "/contactsheet/preview", params={"data": b64, "format": "pdf"}
            )
            with open(preview_file, "wb") as f:
                f.write(await pdf_response.read())
        elif action == "save":
            return data


@contactsheet.command("add", help="Add a new contact sheet template.")
@click.pass_context
async def contactsheet_add(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        contactsheet_form = await flix_client.form("/contactsheet")
        data = cast(models.ContactSheet, contactsheet_form.prompt())
        click.echo(err=True)
        contactsheet_form.print(data, err=True)

        data = await contactsheet_edit_loop(flix_client, contactsheet_form, data)

        if click.confirm("Save contact sheet template?", True, err=True):
            await flix_client.post("/contactsheet", data)
            click.echo(f"Contact sheet template saved successfully.", err=True)


_ContactSheetResponse = TypedDict("_ContactSheetResponse", {"contact_sheets": list[models.ContactSheet]})


@contactsheet.command("list", help="List all contact sheet templates.")
@click.pass_context
async def contactsheet_list(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        contactsheets = cast(_ContactSheetResponse, await flix_client.get("/contactsheets"))
        contactsheet_form = await flix_client.form("/contactsheet")

        for i, cs in enumerate(contactsheets["contact_sheets"]):
            click.echo("ID: {}".format(cs["id"]))
            contactsheet_form.print(cs)
            show_list = ", ".join(
                "{} [{}]".format(show["title"], show["tracking_code"]) for show in cs.get("shows") or []
            )
            click.echo("Assigned shows: {}".format(show_list or "None"))
            if i < len(contactsheets["contact_sheets"]) - 1:
                click.echo()


@contactsheet.command("delete", help="Delete a contact sheet template.")
@click.pass_context
async def contactsheet_delete(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        contactsheets = cast(_ContactSheetResponse, await flix_client.get("/contactsheets"))
        if len(contactsheets["contact_sheets"]) == 0:
            raise click.ClickException("No contact sheet templates added.")
        contactsheet_form = await flix_client.form("/contactsheet")

        j = forms.prompt_enum(
            [forms.Choice(i, cs["name"]) for i, cs in enumerate(contactsheets["contact_sheets"])],
            prompt="Which contact sheet template do you want to delete?",
            prompt_suffix=" ",
        )
        cs = contactsheets["contact_sheets"][j]
        contactsheet_form.print(cs, err=True)

        if click.confirm("Delete this contact sheet template?", False, err=True):
            await flix_client.delete("/contactsheet/{}".format(contactsheets["contact_sheets"][j]["id"]))
            click.echo("Deleted successfully. It may take a few seconds for your changes to be reflected.", err=True)


@contactsheet.command("edit", help="Edit a contact sheet template.")
@click.pass_context
async def contactsheet_edit(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        contactsheets = cast(_ContactSheetResponse, await flix_client.get("/contactsheets"))
        if len(contactsheets["contact_sheets"]) == 0:
            raise click.ClickException("No contact sheet templates added.")
        contactsheet_form = await flix_client.form("/contactsheet")

        j = forms.prompt_enum(
            [forms.Choice(i, cs["name"]) for i, cs in enumerate(contactsheets["contact_sheets"])],
            prompt="Which contact sheet template do you want to edit?",
            prompt_suffix=" ",
        )
        cs = contactsheets["contact_sheets"][j]
        try:
            # don't update shows
            del cs["shows"]
        except KeyError:
            pass

        cs = contactsheet_form.prompt_edit(cs)

        cs = await contactsheet_edit_loop(flix_client, contactsheet_form, cs)

        await flix_client.patch(f"/contactsheet/{cs['id']}", cs)
        click.echo("Saved successfully. It may take a few seconds for your changes to be reflected.", err=True)


_ShowResponse = TypedDict("_ShowResponse", {"shows": list[models.Show]})


@contactsheet.command("assign", help="Assign a contact sheet template to shows.")
@click.pass_context
async def contactsheet_assign(ctx: click.Context) -> None:
    async with await get_client(ctx) as flix_client:
        contactsheets = cast(_ContactSheetResponse, await flix_client.get("/contactsheets"))
        if len(contactsheets["contact_sheets"]) == 0:
            raise click.ClickException("No contact sheet templates added.")

        j = forms.prompt_enum(
            [forms.Choice(i, cs["name"]) for i, cs in enumerate(contactsheets["contact_sheets"])],
            prompt="Which contact sheet template do you want assign?",
            prompt_suffix=" ",
        )
        cs = contactsheets["contact_sheets"][j]
        assigned_shows: list[models.Show] = cs.get("shows") or []

        all_shows = cast(_ShowResponse, await flix_client.get("/shows"))["shows"]

        while True:
            show_list = ", ".join(
                "{} [{}]".format(show["title"], show["tracking_code"]) for show in assigned_shows or []
            )
            click.echo("Currently assigned shows: {}".format(show_list or "None"), err=True)

            action = forms.prompt_enum(
                [
                    forms.Choice("assign", "Assign shows"),
                    forms.Choice("unassign", "Unassign shows"),
                    forms.Choice("save", "Save"),
                ],
                prompt="What would you like to do?",
                prompt_suffix=" ",
            )
            assigned_show_ids = {show["id"] for show in assigned_shows or []}
            if action == "assign":
                shows = [show for show in all_shows if show["id"] not in assigned_show_ids]
            elif action == "unassign":
                shows = assigned_shows
            else:
                break

            if len(shows) == 0:
                click.echo("Error: No shows to {}".format(action), err=True)
                continue

            selected_shows = forms.prompt_multichoice(
                [
                    forms.Choice(i, "{} [{}]".format(show["title"], show["tracking_code"]))
                    for i, show in enumerate(shows)
                ],
                prompt="Specify a comma-separated list of shows to {}".format(action),
            )

            if action == "assign":
                assigned_shows = assigned_shows + [shows[i] for i in selected_shows]
            else:
                assigned_shows = [show for i, show in enumerate(shows) if i not in selected_shows]

        updated_contactsheet: models.ContactSheet = {
            "shows": assigned_shows,
        }
        await flix_client.patch("/contactsheet/{}".format(cs["id"]), body=updated_contactsheet)


def main() -> Any:
    try:
        return flix_cli(auto_envvar_prefix="FLIX", _anyio_backend="asyncio")
    except errors.FlixHTTPError as e:
        click.echo(str(e), err=True)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
