import enum
import json
import logging
from typing import Callable, Any, Coroutine, TypeVar, Type, cast

import aiohttp.web
import dateutil.parser

import flix
from flix.lib import models, types

__all__ = [
    "EventType",
    "WebhookEvent",
    "ErrorEvent",
    "PublishEditorialEvent",
    "PublishFlixEvent",
    "ExportSBPEvent",
    "NewSequenceRevisionEvent",
    "NewPanelRevisionEvent",
    "PingEvent",
    "WebhookHandler",
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

    def __init__(self, event_data: models.Event):
        self.event_type = EventType(event_data["event_type"])
        self.event_payload = event_data


class ErrorEvent(WebhookEvent):
    """An event sent when an error is logged by the Flix server."""

    def __init__(self, event_data: models.ErrorEvent):
        super().__init__(event_data)
        self.message = event_data["message"]
        self.fields = event_data["fields"]


class PublishEditorialEvent(WebhookEvent):
    """An event sent when publishing from Flix to editorial."""

    def __init__(self, event_data: models.PublishToEditorialEvent):
        super().__init__(event_data)
        self.target_app = event_data["target_app"]
        self.user = types.User.from_dict(event_data["user"], _client=None)
        self.created_media_objects = [
            types.MediaObject.from_dict(mo, _client=None) for mo in event_data["created_media_objects"]
        ]
        self.show = types.Show.from_dict(event_data["show"], _client=None)
        self.sequence = types.Sequence.from_dict(event_data["sequence"], _show=self.show, _client=None, _episode=None)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"], _client=None, _sequence=self.sequence
        )


class PublishFlixEvent(WebhookEvent):
    """An event sent when publishing from editorial to Flix."""

    def __init__(self, event_data: models.PublishToFlixEvent):
        super().__init__(event_data)
        self.source_app = event_data["source_app"]
        self.user = types.User.from_dict(event_data["user"], _client=None)
        self.show = types.Show.from_dict(event_data["show"], _client=None)
        self.sequence = types.Sequence.from_dict(event_data["sequence"], _show=self.show, _client=None, _episode=None)
        self.new_sequence_revision = types.SequenceRevision.from_dict(
            event_data["new_sequence_revision"], _client=None, _sequence=self.sequence
        )


class ExportSBPEvent(WebhookEvent):
    """An event sent when exporting a sequence revision to Storyboard Pro."""

    def __init__(self, event_data: models.ExportToSBPEvent):
        super().__init__(event_data)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"], _client=None, _sequence=None
        )


class NewSequenceRevisionEvent(WebhookEvent):
    """An event sent when a new sequence revision is saved."""

    def __init__(self, event_data: models.SequenceRevisionCreatedEvent):
        super().__init__(event_data)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"], _client=None, _sequence=None
        )


class NewPanelRevisionEvent(WebhookEvent):
    """An event sent when a new panel revision is saved."""

    def __init__(self, event_data: models.PanelRevisionCreatedEvent):
        super().__init__(event_data)
        self.panel_revision = types.PanelRevision.from_dict(event_data["panel_revision"], _sequence=None, _client=None)


class NewContactSheetEvent(WebhookEvent):
    """An event sent when a new contact sheet is exported."""

    def __init__(self, event_data: models.ContactSheetCreatedEvent):
        super().__init__(event_data)
        self.asset = types.Asset.from_dict(event_data["asset"], _client=None)
        self.user = types.User.from_dict(event_data["user"], _client=None)
        self.show = types.Show.from_dict(event_data["show"], _client=None)
        self.sequence = types.Sequence.from_dict(event_data["sequence"], _show=self.show, _client=None, _episode=None)
        self.sequence_revision = types.SequenceRevision.from_dict(
            event_data["sequence_revision"], _client=None, _sequence=self.sequence
        )


class PingEvent(WebhookEvent):
    """An event sent when the server is asked to ping a webhook."""

    def __init__(self, event_data: models.PingEvent):
        super().__init__(event_data)
        self.event_time = dateutil.parser.parse(event_data["event_time"])
        self.user = types.User.from_dict(event_data["user"], _client=None)


T = TypeVar("T", bound=WebhookEvent)
WebhookHandlerType = Callable[[T], Coroutine[Any, Any, None]]


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
        self._sub_handlers: dict[Type[WebhookEvent], list[WebhookHandlerType[WebhookEvent]]] = {}

    def set_secret(self, secret: str) -> None:
        """
        Sets the secret to use for this handler.

        :param secret: The secret to use to authenticate incoming events
        """
        self.secret = secret

    def handle(self, event_type: Type[T]) -> Callable[[WebhookHandlerType[T]], WebhookHandlerType[T]]:
        """
        A decorator for specialised webhook handlers that handle a specific type of event.

        :param event_type: The type of event to handle
        :return: A decorator which registers the decorated function as a webhook handler
        """

        def decorator(f: WebhookHandlerType[T]) -> WebhookHandlerType[T]:
            self._add_handler(event_type, f)
            return f

        return decorator

    def _add_handler(self, event_type: Type[T], handler: WebhookHandlerType[T]) -> None:
        if event_type not in self._sub_handlers:
            self._sub_handlers[event_type] = []
        self._sub_handlers[event_type].append(cast(WebhookHandlerType[WebhookEvent], handler))

    def _get_handlers(self, event_type: Type[T]) -> list[WebhookHandlerType[T]]:
        if (handlers := self._sub_handlers.get(event_type)) is not None:
            return cast(list[WebhookHandlerType[T]], handlers)
        return []

    async def __call__(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        if self.secret is None:
            raise RuntimeError("no secret set for webhook handler")

        data = await request.read()
        sig = flix.signature(data, self.secret, as_hex=True)
        if (req_sig := request.headers.get("X-Flix-Signature-256")) != sig:
            if req_sig is not None:
                logger.warning("dropping '%s' event with unexpected signature", request.headers.get("X-Flix-Event"))
            return aiohttp.web.Response(status=400)

        event = _parse_event(request.headers.get("X-Flix-Event"), json.loads(data))
        await self.handler(event)

        for sub_handler in self._get_handlers(type(event)):
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
