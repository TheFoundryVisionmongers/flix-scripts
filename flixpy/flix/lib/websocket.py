import asyncio
import enum
import json
import time
import urllib.parse
import uuid
from collections.abc import Iterable, AsyncIterator, Generator
from types import TracebackType
from typing import TypeVar, AsyncIterable, TypedDict, cast, Type, Generic, Any

import aiohttp
import yarl

from . import client, signing, errors, types


__all__ = [
    "MessageType",
    "WebsocketMessage",
    "KnownWebsocketMessage",
    "UnknownWebsocketMessage",
    "MessagePing",
    "MessageAssetStatus",
    "MessageAssetUpdated",
    "MessagePublishCompleted",
    "MessageQuicktimeCreated",
    "MessageJobError",
    "MessageLicenseValid",
    "MessageAAFCreated",
    "MessageJobChainStatus",
    "MessageEditorialImportStatus",
    "MessageEditorialImportComplete",
    "MessageFCPXMLCreated",
    "MessageContactSheetCreated",
    "MessageDialogueComplete",
    "MessageStoryboardProImportComplete",
    "MessageThumbnailCreationError",
    "Websocket",
    "ChainWaiter",
]


class MessageType(enum.Enum):
    PING = 0
    ASSET_UPDATED = 1
    PUBLISH_COMPLETED = 2
    QUICKTIME_CREATED = 3
    JOB_ERROR = 5
    LICENSE_VALID = 6
    AAF_CREATED = 7
    JOB_CHAIN_STATUS = 10
    EDITORIAL_IMPORT_STATUS = 12
    EDITORIAL_IMPORT_COMPLETE = 13
    STORYBOARD_PRO_IMPORT_COMPLETE = 14
    FCPXML_CREATED = 15
    DIALOGUE_COMPLETE = 16
    ASSET_STATUS = 17
    THUMBNAIL_CREATION_ERROR = 18


class WebsocketMessage:
    def __init__(self, flix_client: "client.Client", raw_data: bytes):
        self.client = flix_client
        self.data = json.loads(raw_data) if raw_data else None


class KnownWebsocketMessage(WebsocketMessage):
    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, raw_data)
        self.msg_type = msg_type


class UnknownWebsocketMessage(WebsocketMessage):
    def __init__(self, flix_client: "client.Client", msg_type: int, raw_data: bytes):
        super().__init__(flix_client, raw_data)
        self.msg_type = msg_type


class MessagePing(KnownWebsocketMessage):
    pass


class MessageAssetUpdated(KnownWebsocketMessage):
    class Model(TypedDict):
        assetID: int
        status: str

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageAssetUpdated.Model, self.data)
        self.asset_id = data["assetID"]
        self.status = data["status"]


class MessagePublishCompleted(KnownWebsocketMessage):
    pass


class AssetCreatedMessage(KnownWebsocketMessage):
    class Model(TypedDict):
        assetID: int

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(AssetCreatedMessage.Model, self.data)
        self.asset_id = data["assetID"]

    async def get_asset(self) -> "types.Asset":
        return await self.client.get_asset(self.asset_id)


class MessageQuicktimeCreated(AssetCreatedMessage):
    pass


class MessageJobError(KnownWebsocketMessage):
    class Model(TypedDict):
        taskId: str
        percentage: int
        status: str
        error: str

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageJobError.Model, self.data)
        self.task_id = data["taskId"]
        self.percentage = data["percentage"]
        self.status = data["status"]
        self.error = data["error"]


class MessageLicenseValid(KnownWebsocketMessage):
    class Model(TypedDict):
        licensed: bool

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageLicenseValid.Model, self.data)
        self.licensed = data["licensed"]


class MessageAAFCreated(AssetCreatedMessage):
    pass


class MessageJobChainStatus(KnownWebsocketMessage):
    class Model(TypedDict):
        taskId: str
        percentage: int
        status: str

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageJobChainStatus.Model, self.data)
        self.task_id = data["taskId"]
        self.percentage = data["percentage"]
        self.status = data["status"]


class MessageEditorialImportStatus(KnownWebsocketMessage):
    class Model(TypedDict):
        position: int
        frameIn: int
        name: str
        ref: bool
        status: str
        error: str

    class Status(enum.Enum):
        PENDING = "pending"
        IN_PROGRESS = "inProgress"
        COMPLETE = "complete"
        UNSUPPORTED = "unsupported"
        ERRORED = "errored"

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageEditorialImportStatus.Model, self.data)
        self.position = data["position"]
        self.frame_in = data["frameIn"]
        self.name = data["name"]
        self.is_ref = data["ref"]
        self.status = MessageEditorialImportStatus.Status(data["status"])
        self.error = data.get("error")


class MessageEditorialImportComplete(KnownWebsocketMessage):
    class Model(TypedDict):
        sequence_revision: int

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageEditorialImportComplete.Model, self.data)
        self.sequence_revision = data["sequence_revision"]

    async def get_sequence_revision(self, sequence: "types.Sequence") -> "types.SequenceRevision":
        return await sequence.get_sequence_revision(self.sequence_revision)


class MessageStoryboardProImportComplete(KnownWebsocketMessage):
    class MissingAssetModel(TypedDict):
        asset_id: int
        artwork: int
        source_media: int

    class Model(TypedDict):
        sequence_revision: int
        missing_assets: dict[str, "MessageStoryboardProImportComplete.MissingAssetModel"]

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageStoryboardProImportComplete.Model, self.data)
        self.sequence_revision = data["sequence_revision"]


class MessageFCPXMLCreated(AssetCreatedMessage):
    pass


class MessageDialogueComplete(AssetCreatedMessage):
    class Model(TypedDict):
        taskId: str
        assetID: int

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageDialogueComplete.Model, self.data)
        # asset ID is set in AssetCreatedMessage
        self.task_id = data["taskId"]


class MessageAssetStatus(KnownWebsocketMessage):
    class Model(TypedDict):
        assetID: int
        status: str

    def __init__(self, flix_client: "client.Client", msg_type: MessageType, raw_data: bytes):
        super().__init__(flix_client, msg_type, raw_data)
        data = cast(MessageAssetStatus.Model, self.data)
        self.asset_id = data["assetID"]
        self.status = data["status"]


class MessageThumbnailCreationError(MessageAssetStatus):
    pass


class MessageContactSheetCreated(AssetCreatedMessage):
    pass


_MESSAGE_TYPES: dict[MessageType, Type[KnownWebsocketMessage]] = {
    MessageType.PING: MessagePing,
    MessageType.ASSET_UPDATED: MessageAssetUpdated,
    MessageType.PUBLISH_COMPLETED: MessagePublishCompleted,
    MessageType.QUICKTIME_CREATED: MessageQuicktimeCreated,
    MessageType.JOB_ERROR: MessageJobError,
    MessageType.LICENSE_VALID: MessageLicenseValid,
    MessageType.AAF_CREATED: MessageAAFCreated,
    MessageType.JOB_CHAIN_STATUS: MessageJobChainStatus,
    MessageType.EDITORIAL_IMPORT_STATUS: MessageEditorialImportStatus,
    MessageType.EDITORIAL_IMPORT_COMPLETE: MessageEditorialImportComplete,
    MessageType.STORYBOARD_PRO_IMPORT_COMPLETE: MessageStoryboardProImportComplete,
    MessageType.FCPXML_CREATED: MessageFCPXMLCreated,
    MessageType.DIALOGUE_COMPLETE: MessageDialogueComplete,
    MessageType.ASSET_STATUS: MessageAssetStatus,
    MessageType.THUMBNAIL_CREATION_ERROR: MessageThumbnailCreationError,
}


WebsocketSelf = TypeVar("WebsocketSelf", bound="Websocket")
WebsocketMessageType = TypeVar("WebsocketMessageType", bound="WebsocketMessage")


class ChainWaiter(Generic[WebsocketMessageType]):
    def __init__(
        self,
        ws: "Websocket",
        complete_message_type: Type[WebsocketMessageType],
        message_filter: Iterable[Type[WebsocketMessage]] = (),
        timeout: float | None = None,
    ):
        self._ws = ws
        self._complete_message_type = complete_message_type
        self._filter: tuple[Type[WebsocketMessage], ...] = (MessageJobChainStatus, *message_filter)
        self.timeout = timeout
        self._result: WebsocketMessageType | None = None

    @property
    def result(self) -> WebsocketMessageType:
        if self._result is None:
            raise RuntimeError("attempted to access result before completion")
        return self._result

    async def __aiter__(self) -> AsyncIterator[WebsocketMessage]:
        start_time = time.time()
        it = aiter(self._ws)
        while True:
            if self.timeout is not None:
                timeout = self.timeout - (time.time() - start_time)
            else:
                timeout = None
            msg = await asyncio.wait_for(anext(it), timeout=timeout)

            if isinstance(msg, self._complete_message_type):
                self._result = msg
                break
            elif isinstance(msg, MessageJobError):
                raise errors.FlixError(f"{msg.status}: {msg.error}")
            elif isinstance(msg, MessageThumbnailCreationError):
                raise errors.FlixError(msg.status)
            elif isinstance(msg, self._filter):
                yield msg

    async def _run_until_complete(self) -> WebsocketMessageType:
        async for _ in self:
            pass
        return self.result

    def __await__(self) -> Generator[Any, None, WebsocketMessageType]:
        return self._run_until_complete().__await__()


class Websocket:
    def __init__(self, session: aiohttp.ClientSession, _client: "client.Client"):
        self._session = session
        self._client = _client
        access_key = _client.access_key
        if access_key is None:
            raise RuntimeError("must be authenticated to open websocket")
        self._access_key = access_key
        self.client_id = str(uuid.uuid4())
        self._ws: aiohttp.ClientWebSocketResponse | None = None

    @property
    def signed_path(self) -> yarl.URL:
        time = signing.get_time_rfc3999()
        # yarl does not escape : while the server does, so manually build the url for signing
        path_to_sign = f"{self.endpoint}?keyid={self._access_key.id}&expiretime={urllib.parse.quote(time)}"
        signature = signing.signature(path_to_sign.encode(), self._access_key.secret_access_key)
        return self.endpoint.with_query(
            {"keyid": self._access_key.id, "expiretime": time, "signature": signature, "id": self.client_id}
        )

    @property
    def endpoint(self) -> yarl.URL:
        protocol = "wss" if self._client.ssl else "ws"
        return yarl.URL(f"{protocol}://{self._client.hostname}:{self._client.port}/ws", encoded=True)

    async def open(self) -> None:
        self._ws = await self._session.ws_connect(self.signed_path)

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()

    def wait_on_chain(
        self,
        complete_message_type: Type[WebsocketMessageType],
        message_filter: Iterable[Type[WebsocketMessage]] = (),
        timeout: float | None = None,
    ) -> ChainWaiter[WebsocketMessageType]:
        return ChainWaiter(self, complete_message_type, message_filter=message_filter, timeout=timeout)

    async def __aiter__(self) -> AsyncIterator[WebsocketMessage]:
        if self._ws is None:
            raise RuntimeError("must open websocket before iterating")

        msg: aiohttp.WSMessage
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.ERROR:
                exc = msg.data
                if isinstance(exc, aiohttp.WebSocketError):
                    raise errors.FlixHTTPError(exc.code, "Websocket error")
                else:
                    raise exc
            elif msg.type == aiohttp.WSMsgType.BINARY:
                data: bytes = msg.data
                try:
                    msg_type = MessageType(data[0])
                    msg_class = _MESSAGE_TYPES[msg_type]
                except (ValueError, KeyError):
                    yield UnknownWebsocketMessage(self._client, data[0], data[1:])
                else:
                    yield msg_class(self._client, msg_type, data[1:])

    async def __aenter__(self: WebsocketSelf) -> WebsocketSelf:
        await self.open()
        return self

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        await self.close()
