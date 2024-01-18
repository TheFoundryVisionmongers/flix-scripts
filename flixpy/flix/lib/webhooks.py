import enum
import json
import logging
from typing import Callable, Any, Coroutine, TypeVar, cast

import aiohttp.web
import dateutil.parser
from typing_extensions import TypeAlias

import flix
from flix.lib import client as _client, errors, models, types

__all__ = [
    "EventType",
    "WebhookEvent",
    "ErrorEvent",
    "PublishEditorialEvent",
    "PublishFlixEvent",
    "ExportSBPEvent",
    "NewSequenceRevisionEvent",
    "NewPanelRevisionEvent",
    "NewContactSheetEvent",
    "PingEvent",
    "WebhookHandler",
    "webhook",
    "WebhookHandlerType",
    "EventFactory",
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

    def __init__(self, event_data: models.Event):
        self.event_type = EventType(event_data["event_type"])
        self.event_payload = event_data


EventModelType = TypeVar("EventModelType", bound=models.Event)
WebhookEventType = TypeVar("WebhookEventType", bound=WebhookEvent)
WebhookHandlerType = Callable[[WebhookEventType], Coroutine[Any, Any, None]]
EventFactory: TypeAlias = Callable[
    [models.Event, _client.Client | None], WebhookEventType
]

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

    def __init__(self, data: models.Event, _: _client.Client | None):
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
    ):
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

    def __init__(self, data: models.Event, client: _client.Client | None):
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

    def __init__(self, data: models.Event, client: _client.Client | None):
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
    ):
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
    ):
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
    ):
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

    def __init__(self, data: models.Event, client: _client.Client | None):
        super().__init__(data)
        event_data = cast(models.PingEvent, data)
        self.event_time = dateutil.parser.parse(event_data["event_time"])
        self.user = types.User.from_dict(event_data["user"], _client=client)


class WebhookHandler:
    """
    This class handles authentication and parsing of incoming Flix events.
    An instance of this class can be added as a route to an aiohttp.web.Application.

    A function accepting a Flix event can be transformed into a WebhookHandler using the webhook decorator.
    """

    def __init__(
        self,
        handler: WebhookHandlerType[WebhookEvent],
        secret: str | None = None,
    ):
        self.secret = secret
        self.handler = handler
        self._sub_handlers: dict[
            EventFactory[WebhookEvent], list[WebhookHandlerType[WebhookEvent]]
        ] = {}

    def set_secret(self, secret: str) -> None:
        """
        Sets the secret to use for this handler.

        :param secret: The secret to use to authenticate incoming events
        """
        self.secret = secret

    def handle(
        self, event_type: EventFactory[WebhookEventType]
    ) -> Callable[
        [WebhookHandlerType[WebhookEventType]], WebhookHandlerType[WebhookEventType]
    ]:
        """
        A decorator for specialised webhook handlers that handle a specific type of event.

        :param event_type: The type of event to handle
        :return: A decorator which registers the decorated function as a webhook handler
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
        self._sub_handlers[event_type].append(
            cast(WebhookHandlerType[WebhookEvent], handler)
        )

    def _get_handlers(
        self, event_type: EventFactory[WebhookEventType]
    ) -> list[WebhookHandlerType[WebhookEventType]]:
        if (handlers := self._sub_handlers.get(event_type)) is not None:
            return cast(list[WebhookHandlerType[WebhookEventType]], handlers)
        return []

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


def webhook(secret: str | None = None) -> Callable[[WebhookHandlerType[WebhookEvent]], WebhookHandler]:
    """
    Decorator for webhook handlers.

    :param secret: The secret used to authenticate webhook events
    :return: A decorator transforming a function into a WebhookHandler
    """

    def decorator(f: WebhookHandlerType[WebhookEvent]) -> WebhookHandler:
        return WebhookHandler(f, secret=secret)

    return decorator


_EVENT_TYPES: dict[EventType, Type[WebhookEvent]] = {
    EventType.ERROR: ErrorEvent,
    EventType.PUBLISH_EDITORIAL: PublishEditorialEvent,
    EventType.PUBLISH_FLIX: PublishFlixEvent,
    EventType.EXPORT_SBP: ExportSBPEvent,
    EventType.NEW_SEQUENCE_REVISION: NewSequenceRevisionEvent,
    EventType.NEW_PANEL_REVISION: NewPanelRevisionEvent,
    EventType.NEW_CONTACT_SHEET: NewContactSheetEvent,
    EventType.PING: PingEvent,
}


def _parse_event(event_name: str | None, data: models.Event) -> WebhookEvent:
    event_type = _EVENT_TYPES[EventType(event_name)]
    return event_type(data)
