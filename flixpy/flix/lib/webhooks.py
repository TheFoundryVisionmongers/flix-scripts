"""Utilities for easily listening to webhook events sent by the Flix Server.

Webhook events are sent from the Flix Server to a registered webhook
when certain predefined actions are performed, such as publishing to editorial
or creating a new revision of a sequence.
"""

from __future__ import annotations

import asyncio
import contextlib
import enum
import json
import logging
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, cast

import aiohttp.typedefs
import aiohttp.web
import dateutil.parser
from typing_extensions import Required, TypedDict, Unpack

import flix
from flix.lib import client as _client
from flix.lib import errors, models, types

if TYPE_CHECKING:
    import ssl

__all__ = [
    "ErrorEvent",
    "EventFactory",
    "EventType",
    "ExportSBPEvent",
    "NewContactSheetEvent",
    "NewPanelRevisionEvent",
    "NewSequenceRevisionEvent",
    "PingEvent",
    "PublishEditorialEvent",
    "PublishFlixEvent",
    "WebhookEvent",
    "WebhookHandler",
    "WebhookHandlerType",
    "run_webhook_server",
    "webhook",
]

logger = logging.getLogger(__name__)


class EventType(enum.Enum):
    ERROR = "An error occurred"
    PUBLISH_EDITORIAL = "Publish to editorial"
    PUBLISH_FLIX = "Publish to Flix"
    EXPORT_SBP = "Sequence revision sent to SBP"
    NEW_SEQUENCE_REVISION = "Sequence revision created"
    NEW_PANEL_REVISION = "Panel revision created"
    NEW_CONTACT_SHEET = "Contact sheet created"
    PING = "Ping"


class WebhookEvent:
    """A general Flix event."""

    def __init__(self, event_data: models.Event) -> None:
        self.event_type = EventType(event_data["event_type"])
        self.event_payload = event_data


EventModelType = TypeVar("EventModelType", bound=models.Event)
WebhookEventType = TypeVar("WebhookEventType", bound=WebhookEvent)
WebhookHandlerType = Callable[[WebhookEventType], Coroutine[Any, Any, None]]
EventFactory: TypeAlias = Callable[[models.Event, _client.Client | None], WebhookEventType]

_EVENT_TYPES: dict[EventType, EventFactory[WebhookEvent]] = {}


def _event(
    event_type: EventType,
) -> Callable[[EventFactory[WebhookEventType]], EventFactory[WebhookEventType]]:
    """Registers a class as an event type."""

    def _register_event(
        f: EventFactory[WebhookEventType],
    ) -> EventFactory[WebhookEventType]:
        _EVENT_TYPES[event_type] = f
        return f

    return _register_event


@_event(EventType.ERROR)
class ErrorEvent(WebhookEvent):
    """An event sent when an error is logged by the Flix server."""

    def __init__(self, data: models.Event, _: _client.Client | None) -> None:
        super().__init__(data)
        event_data = cast(models.ErrorEvent, data)
        self.message = event_data["message"]
        self.fields = event_data["fields"]


@_event(EventType.PUBLISH_EDITORIAL)
class PublishEditorialEvent(WebhookEvent):
    """An event sent when publishing from Flix to editorial."""

    def __init__(
        self,
        data: models.Event,
        client: _client.Client | None,
    ) -> None:
        super().__init__(data)
        event_data = cast(models.PublishToEditorialEvent, data)
        self.target_app = event_data["target_app"]
        self.user = types.User.from_dict(event_data["user"], _client=client)
        self.created_media_objects = [
            types.MediaObject.from_dict(mo, _client=client)
            for mo in event_data["created_media_objects"]
        ]
        self.show = types.Show.from_dict(event_data["show"], _client=client)
        self.sequence = types.Sequence.from_dict(
            event_data["sequence"], _show=self.show, _client=client, _episode=None
        )
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"],
            _client=client,
            _sequence=self.sequence,
        )


@_event(EventType.PUBLISH_FLIX)
class PublishFlixEvent(WebhookEvent):
    """An event sent when publishing from editorial to Flix."""

    def __init__(self, data: models.Event, client: _client.Client | None) -> None:
        super().__init__(data)
        event_data = cast(models.PublishToFlixEvent, data)
        self.source_app = event_data["source_app"]
        self.user = types.User.from_dict(event_data["user"], _client=client)
        self.show = types.Show.from_dict(event_data["show"], _client=client)
        self.sequence = types.Sequence.from_dict(
            event_data["sequence"], _show=self.show, _episode=None, _client=client
        )
        self.new_sequence_revision = types.SequenceRevision.from_dict(
            event_data["new_sequence_revision"],
            _sequence=self.sequence,
            _client=client,
        )


_SparseIDs = models.SequenceRevision | models.PanelRevision


def _sparse_show(data: _SparseIDs, client: _client.Client | None) -> types.Show:
    """Create a sparse show from just IDs for events that don't include show data."""
    return types.Show(show_id=data["show_id"], _client=client)


def _sparse_sequence(data: _SparseIDs, client: _client.Client | None) -> types.Sequence:
    """Create a sparse sequence from just IDs for events that don't include sequence data."""
    return types.Sequence(
        sequence_id=data["sequence_id"],
        _show=_sparse_show(data, client),
        _episode=None,
        _client=client,
    )


@_event(EventType.EXPORT_SBP)
class ExportSBPEvent(WebhookEvent):
    """An event sent when exporting a sequence revision to Storyboard Pro."""

    def __init__(self, data: models.Event, client: _client.Client | None) -> None:
        super().__init__(data)
        event_data = cast(models.ExportToSBPEvent, data)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"],
            _sequence=_sparse_sequence(event_data["sequence_revision"], client),
            _client=client,
        )


@_event(EventType.NEW_SEQUENCE_REVISION)
class NewSequenceRevisionEvent(WebhookEvent):
    """An event sent when a new sequence revision is saved."""

    def __init__(
        self,
        data: models.Event,
        client: _client.Client | None,
    ) -> None:
        super().__init__(data)
        event_data = cast(models.SequenceRevisionCreatedEvent, data)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"],
            _sequence=_sparse_sequence(event_data["sequence_revision"], client),
            _client=client,
        )


@_event(EventType.NEW_PANEL_REVISION)
class NewPanelRevisionEvent(WebhookEvent):
    """An event sent when a new panel revision is saved."""

    def __init__(
        self,
        data: models.Event,
        client: _client.Client | None,
    ) -> None:
        super().__init__(data)
        event_data = cast(models.PanelRevisionCreatedEvent, data)
        self.panel_revision = types.PanelRevision.from_dict(
            event_data["panel_revision"],
            _sequence=_sparse_sequence(event_data["panel_revision"], client),
            _client=client,
        )


@_event(EventType.NEW_CONTACT_SHEET)
class NewContactSheetEvent(WebhookEvent):
    """An event sent when a new contact sheet is exported."""

    def __init__(
        self,
        data: models.Event,
        client: _client.Client | None,
    ) -> None:
        super().__init__(data)
        event_data = cast(models.ContactSheetCreatedEvent, data)
        self.asset = types.Asset.from_dict(event_data["asset"], _client=client)
        self.user = types.User.from_dict(event_data["user"], _client=client)
        self.show = types.Show.from_dict(event_data["show"], _client=client)
        self.sequence = types.Sequence.from_dict(
            event_data["sequence"], _show=self.show, _episode=None, _client=client
        )
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"],
            _sequence=self.sequence,
            _client=client,
        )


@_event(EventType.PING)
class PingEvent(WebhookEvent):
    """An event sent when the server is asked to ping a webhook."""

    def __init__(self, data: models.Event, client: _client.Client | None) -> None:
        super().__init__(data)
        event_data = cast(models.PingEvent, data)
        self.event_time = dateutil.parser.parse(event_data["event_time"])
        self.user = types.User.from_dict(event_data["user"], _client=client)


class WebhookHandler:
    """This class handles authentication and parsing of incoming Flix events.

    An instance of this class can be added as a route to an aiohttp.web.Application.
    A function accepting a Flix event can be transformed into a WebhookHandler using
    the webhook decorator.
    """

    def __init__(
        self,
        handler: WebhookHandlerType[WebhookEvent],
        path: str = "/",
        secret: str | None = None,
    ) -> None:
        self.path = path
        self.secret = secret
        self.handler = handler
        self._sub_handlers: dict[
            EventFactory[WebhookEvent], list[WebhookHandlerType[WebhookEvent]]
        ] = {}

    def set_secret(self, secret: str) -> None:
        """Sets the secret to use for this handler.

        Args:
            secret: The secret to use to authenticate incoming events.
        """
        self.secret = secret

    def handle(
        self, event_type: EventFactory[WebhookEventType]
    ) -> Callable[[WebhookHandlerType[WebhookEventType]], WebhookHandlerType[WebhookEventType]]:
        """A decorator for specialised webhook handlers that handle a specific type of event.

        Args:
            event_type: The type of event to handle.

        Returns:
            A decorator which registers the decorated function as a webhook handler.
        """

        def decorator(
            f: WebhookHandlerType[WebhookEventType],
        ) -> WebhookHandlerType[WebhookEventType]:
            self._add_handler(event_type, f)
            return f

        return decorator

    def _add_handler(
        self,
        event_type: EventFactory[WebhookEventType],
        handler: WebhookHandlerType[WebhookEventType],
    ) -> None:
        if event_type not in self._sub_handlers:
            self._sub_handlers[event_type] = []
        self._sub_handlers[event_type].append(cast(WebhookHandlerType[WebhookEvent], handler))

    def _get_handlers(
        self, event_type: EventFactory[WebhookEventType]
    ) -> list[WebhookHandlerType[WebhookEventType]]:
        if (handlers := self._sub_handlers.get(event_type)) is not None:
            return cast(list[WebhookHandlerType[WebhookEventType]], handlers)
        return []

    def make_route(self, client: _client.Client | None) -> aiohttp.web.RouteDef:
        """Create an aiohttp route definition for this handler.

        Args:
            client: The client instance to use for server requests in webhook handlers.

        Returns:
            A route that can be added to an [Application][aiohttp.web.Application].
        """

        async def _handle(request: aiohttp.web.BaseRequest) -> aiohttp.web.Response:
            return await self(request, client=client)

        return aiohttp.web.post(self.path, _handle)

    async def __call__(
        self, request: aiohttp.web.BaseRequest, *, client: _client.Client | None = None
    ) -> aiohttp.web.Response:
        if self.secret is None:
            raise errors.FlixError("no secret set for webhook handler")

        data = await request.read()
        sig = flix.signature(data, self.secret, as_hex=True)
        if (req_sig := request.headers.get("X-Flix-Signature-256")) != sig:
            if req_sig is not None:
                logger.warning(
                    (
                        "dropping '%s' event with unexpected signature"
                        " (did you specify the right secret?)"
                    ),
                    request.headers.get("X-Flix-Event"),
                )
            return aiohttp.web.Response(status=400)

        event_type = EventType(request.headers.get("X-Flix-Event"))
        event_body = cast(models.Event, json.loads(data))
        event_factory = _EVENT_TYPES[event_type]
        event = event_factory(event_body, client)

        await self.handler(event)
        for sub_handler in self._get_handlers(event_factory):
            await sub_handler(event)

        return aiohttp.web.Response()


def webhook(
    secret: str | None = None,
    path: str = "/",
) -> Callable[[WebhookHandlerType[WebhookEvent]], WebhookHandler]:
    """Decorator for webhook handlers.

    Args:
        secret: The secret used to authenticate webhook events.
        path: The endpoint path of the webhook, e.g. ``"/events"``.

    Returns:
        A decorator transforming a function into a WebhookHandler.
    """

    def decorator(f: WebhookHandlerType[WebhookEvent]) -> WebhookHandler:
        return WebhookHandler(f, path=path, secret=secret)

    return decorator


class ClientOptions(TypedDict, total=False):
    """Options to pass to [Client][flix.Client]."""

    hostname: Required[str]
    port: Required[int]
    ssl: bool
    disable_ssl_validation: bool
    username: str
    password: str
    auto_extend_session: bool
    access_key: _client.AccessKey


class ServerOptions(TypedDict, total=False):
    """Options to pass to [TCPSite][aiohttp.web.TCPSite]."""

    shutdown_timeout: float
    backlog: int
    reuse_address: bool
    reuse_port: bool


async def run_webhook_server(
    *handlers: WebhookHandler,
    host: str | None = None,
    port: int | None = None,
    ssl_context: ssl.SSLContext | None = None,
    client_options: ClientOptions | None = None,
    **kwargs: Unpack[ServerOptions],
) -> None:
    """Run a server that listens for webhook events.

    This function will run indefinitely until cancelled.

    Example:
        ```python
        # define handlers
        @flix.webhook(path="/events", secret="...")
        def on_event(
            event: flix.WebhookEvent,
        ) -> None: ...


        @on_event.handle(flix.PublishEditorialEvent)
        def on_publish(
            event: flix.PublishEditorialEvent,
        ) -> None: ...


        # start webhook server
        asyncio.run(
            flix.run_webhook_server(
                on_event,
                port=8888,
                # allow Flix Server requests from handlers
                client_options={
                    "hostname": "localhost",
                    "port": 8080,
                    "username": "admin",
                    "password": "admin",
                },
            ),
        )
        ```

    Args:
        *handlers: One or more webhook handlers.
        host: The hostname to bind to. Defaults to ``"0.0.0.0"``.
        port: The port to listen to. Defaults to ``8080``, or ``8443`` if
            ``ssl_context`` is provided.
        ssl_context: If provided, the server will run with SSL/TLS encryption.
        client_options: [Client][flix.Client] options. If passed, a client
            will be attached to any incoming events, allowing event handlers
            to call methods that request data from the Flix Server.
        **kwargs: Additional options to pass to [TCPSite][aiohttp.web.TCPSite].
    """
    async with _webhook_client(client_options) as client:
        app = aiohttp.web.Application()
        app.add_routes([handler.make_route(client) for handler in handlers])

        async with _webhook_runner(app) as runner:
            await aiohttp.web.TCPSite(
                runner, host=host, port=port, ssl_context=ssl_context, **kwargs
            ).start()
            await asyncio.Future[None]()


@contextlib.asynccontextmanager
async def _webhook_client(
    client_options: ClientOptions | None,
) -> AsyncIterator[_client.Client | None]:
    if client_options is not None:
        async with _client.Client(**client_options) as client:
            yield client
    else:
        yield None


@contextlib.asynccontextmanager
async def _webhook_runner(
    app: aiohttp.web.Application,
) -> AsyncIterator[aiohttp.web.AppRunner]:
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    try:
        yield runner
    finally:
        await runner.cleanup()
