"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class TransferReq(google.protobuf.message.Message):
    """TransferReq is a request message which is streamed to the Transfer endpoint."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class StartMessage(google.protobuf.message.Message):
        """StartMessage is the message sent at the beginning of a stream to the Transfer endpoint. This should be the first
        message, and should be the only StartMessage in the stream.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        class _StartAction:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _StartActionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[TransferReq.StartMessage._StartAction.ValueType], builtins.type):  # noqa: F821
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            UPLOAD: TransferReq.StartMessage._StartAction.ValueType  # 0
            DOWNLOAD: TransferReq.StartMessage._StartAction.ValueType  # 1

        class StartAction(_StartAction, metaclass=_StartActionEnumTypeWrapper):
            """StartAction is the direction of the transfer, up or down."""

        UPLOAD: TransferReq.StartMessage.StartAction.ValueType  # 0
        DOWNLOAD: TransferReq.StartMessage.StartAction.ValueType  # 1

        class _StartState:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _StartStateEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[TransferReq.StartMessage._StartState.ValueType], builtins.type):  # noqa: F821
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            NEW: TransferReq.StartMessage._StartState.ValueType  # 0
            """NEW is for when this transfer is new and requires initialising."""
            RESUME: TransferReq.StartMessage._StartState.ValueType  # 1
            """RESUME is for when this transfer has already been initialised and needs to start part way through the data."""
            CANCEL: TransferReq.StartMessage._StartState.ValueType  # 2
            """CANCEL is for when this transfer is being cancelled from the calling end. This is the only StartState where the
            client should send no further messages. The client should immediately close the send stream after this message.
            """

        class StartState(_StartState, metaclass=_StartStateEnumTypeWrapper):
            """StartState is the state this transfer is starting in."""

        NEW: TransferReq.StartMessage.StartState.ValueType  # 0
        """NEW is for when this transfer is new and requires initialising."""
        RESUME: TransferReq.StartMessage.StartState.ValueType  # 1
        """RESUME is for when this transfer has already been initialised and needs to start part way through the data."""
        CANCEL: TransferReq.StartMessage.StartState.ValueType  # 2
        """CANCEL is for when this transfer is being cancelled from the calling end. This is the only StartState where the
        client should send no further messages. The client should immediately close the send stream after this message.
        """

        ACTION_FIELD_NUMBER: builtins.int
        STATE_FIELD_NUMBER: builtins.int
        STARTFROM_FIELD_NUMBER: builtins.int
        TOTALBYTES_FIELD_NUMBER: builtins.int
        METADATA_FIELD_NUMBER: builtins.int
        ORIGINALEXT_FIELD_NUMBER: builtins.int
        Action: global___TransferReq.StartMessage.StartAction.ValueType
        """Action is the action for this message."""
        State: global___TransferReq.StartMessage.StartState.ValueType
        """State is the state this message should start in."""
        StartFrom: builtins.int
        """StartFrom is only used when the client is requesting data. This is the amount of bytes to seek before sending the
        first chunk.
        """
        TotalBytes: builtins.int
        """TotalBytes is only used when the client is providing data. This is the total number of bytes the server should
        ultimately expect for the file, and is used to calculate percentage completion.
        """
        Metadata: builtins.bytes
        """Metadata holds any data required by the src application."""
        OriginalExt: builtins.str
        """OriginalExt is the original extension of the file, if being uploaded. This will preserve the extension during the
        upload. If this is not set, the resultant uploaded file will have no extension. The string, if set, should
        contain the leading '.'.
        """
        def __init__(
            self,
            *,
            Action: global___TransferReq.StartMessage.StartAction.ValueType = ...,
            State: global___TransferReq.StartMessage.StartState.ValueType = ...,
            StartFrom: builtins.int = ...,
            TotalBytes: builtins.int = ...,
            Metadata: builtins.bytes = ...,
            OriginalExt: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["Action", b"Action", "Metadata", b"Metadata", "OriginalExt", b"OriginalExt", "StartFrom", b"StartFrom", "State", b"State", "TotalBytes", b"TotalBytes"]) -> None: ...

    @typing_extensions.final
    class DataMessage(google.protobuf.message.Message):
        """DataMessage is used while providing data from the client to the server. It either provides a chunk of data, or a
        pause instruction.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        class _DataAction:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _DataActionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[TransferReq.DataMessage._DataAction.ValueType], builtins.type):  # noqa: F821
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            DATA: TransferReq.DataMessage._DataAction.ValueType  # 0
            """DATA indicates this message is providing data."""
            PAUSE: TransferReq.DataMessage._DataAction.ValueType  # 1
            """PAUSE indicates this is the last message of this stream, however the transfer will be resumed at a later stage."""

        class DataAction(_DataAction, metaclass=_DataActionEnumTypeWrapper):
            """DataAction is the instruction type of this DataMessage."""

        DATA: TransferReq.DataMessage.DataAction.ValueType  # 0
        """DATA indicates this message is providing data."""
        PAUSE: TransferReq.DataMessage.DataAction.ValueType  # 1
        """PAUSE indicates this is the last message of this stream, however the transfer will be resumed at a later stage."""

        ACTION_FIELD_NUMBER: builtins.int
        DATA_FIELD_NUMBER: builtins.int
        Action: global___TransferReq.DataMessage.DataAction.ValueType
        """Action is the action type for this message."""
        @property
        def Data(self) -> global___ChunkData:
            """Data is the chunk data for this message. This will be empty on a PAUSE action."""
        def __init__(
            self,
            *,
            Action: global___TransferReq.DataMessage.DataAction.ValueType = ...,
            Data: global___ChunkData | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["Data", b"Data"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["Action", b"Action", "Data", b"Data"]) -> None: ...

    @typing_extensions.final
    class CloseMessage(google.protobuf.message.Message):
        """CloseMessage concludes the stream and sets the final status. This may complete the transfer, or cancel it part way
        through.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        class _CloseStatus:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _CloseStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[TransferReq.CloseMessage._CloseStatus.ValueType], builtins.type):  # noqa: F821
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            COMPLETE: TransferReq.CloseMessage._CloseStatus.ValueType  # 0
            """COMPLETE is when the transfer has completed successfully."""
            CANCEL: TransferReq.CloseMessage._CloseStatus.ValueType  # 1
            """CANCEL is when the stream is ending before the transfer has completed."""

        class CloseStatus(_CloseStatus, metaclass=_CloseStatusEnumTypeWrapper):
            """CloseStatus is the status of this close message."""

        COMPLETE: TransferReq.CloseMessage.CloseStatus.ValueType  # 0
        """COMPLETE is when the transfer has completed successfully."""
        CANCEL: TransferReq.CloseMessage.CloseStatus.ValueType  # 1
        """CANCEL is when the stream is ending before the transfer has completed."""

        STATUS_FIELD_NUMBER: builtins.int
        Status: global___TransferReq.CloseMessage.CloseStatus.ValueType
        """Status is the status of this message."""
        def __init__(
            self,
            *,
            Status: global___TransferReq.CloseMessage.CloseStatus.ValueType = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["Status", b"Status"]) -> None: ...

    STARTMSG_FIELD_NUMBER: builtins.int
    DATAMSG_FIELD_NUMBER: builtins.int
    CLOSEMSG_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    @property
    def StartMsg(self) -> global___TransferReq.StartMessage:
        """StartMsg is the first message sent in the stream; there will only be one StartMsg sent per stream. It will either
        initialise a transfer, or cancel a paused transfer.
        """
    @property
    def DataMsg(self) -> global___TransferReq.DataMessage:
        """DataMsg make up the bulk of the stream when sending data from client to server."""
    @property
    def CloseMsg(self) -> global___TransferReq.CloseMessage:
        """CloseMessage concludes a stream. No further messages will be sent after this message."""
    UUID: builtins.str
    def __init__(
        self,
        *,
        StartMsg: global___TransferReq.StartMessage | None = ...,
        DataMsg: global___TransferReq.DataMessage | None = ...,
        CloseMsg: global___TransferReq.CloseMessage | None = ...,
        UUID: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["CloseMsg", b"CloseMsg", "DataMsg", b"DataMsg", "Message", b"Message", "StartMsg", b"StartMsg"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["CloseMsg", b"CloseMsg", "DataMsg", b"DataMsg", "Message", b"Message", "StartMsg", b"StartMsg", "UUID", b"UUID"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["Message", b"Message"]) -> typing_extensions.Literal["StartMsg", "DataMsg", "CloseMsg"] | None: ...

global___TransferReq = TransferReq

@typing_extensions.final
class TransferResp(google.protobuf.message.Message):
    """TransferResp is the response message streamed from the Transfer endpoint."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class RecvResp(google.protobuf.message.Message):
        """RecvResp is the response structure when the server has received data on a client to server transfer."""

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        class _RespStatus:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _RespStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[TransferResp.RecvResp._RespStatus.ValueType], builtins.type):  # noqa: F821
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            SUCCESS: TransferResp.RecvResp._RespStatus.ValueType  # 0
            ERROR: TransferResp.RecvResp._RespStatus.ValueType  # 1

        class RespStatus(_RespStatus, metaclass=_RespStatusEnumTypeWrapper):
            """RespStatus is the receive status. Upon error, the send can be retried without cancelling the stream/transfer."""

        SUCCESS: TransferResp.RecvResp.RespStatus.ValueType  # 0
        ERROR: TransferResp.RecvResp.RespStatus.ValueType  # 1

        STATUS_FIELD_NUMBER: builtins.int
        STARTFROM_FIELD_NUMBER: builtins.int
        TOTALBYTES_FIELD_NUMBER: builtins.int
        ERROR_FIELD_NUMBER: builtins.int
        Status: global___TransferResp.RecvResp.RespStatus.ValueType
        """Status is whether this chunk was received successfully or if it needs resending."""
        StartFrom: builtins.int
        """StartFrom will only be set on the first response of a client to server transfer. This indicates to the client
        where to seek to in the data before sending the first chunk.
        """
        TotalBytes: builtins.int
        """TotalBytes is only used when the server is providing data. This is the total number of bytes the client should
        ultimately expect for the file, and is used to calculate percentage completion.
        """
        Error: builtins.str
        """Error will be set to the string representation of the error, if one has occurred. Otherwise this will not be set."""
        def __init__(
            self,
            *,
            Status: global___TransferResp.RecvResp.RespStatus.ValueType = ...,
            StartFrom: builtins.int = ...,
            TotalBytes: builtins.int = ...,
            Error: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["Error", b"Error", "StartFrom", b"StartFrom", "Status", b"Status", "TotalBytes", b"TotalBytes"]) -> None: ...

    @typing_extensions.final
    class SendResp(google.protobuf.message.Message):
        """SendResp is the response message for when the client is receiving the data."""

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        ERROR_FIELD_NUMBER: builtins.int
        DATA_FIELD_NUMBER: builtins.int
        Error: builtins.str
        """Error will be set to the string representation of the server-side error, if and only if one occurred. This will
         otherwise be an empty string. An error here would be a total failure of transfer.
        """
        @property
        def Data(self) -> global___ChunkData:
            """Data holds the chunk data for the response."""
        def __init__(
            self,
            *,
            Error: builtins.str = ...,
            Data: global___ChunkData | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["Data", b"Data"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["Data", b"Data", "Error", b"Error"]) -> None: ...

    RECEIVED_FIELD_NUMBER: builtins.int
    RETURNED_FIELD_NUMBER: builtins.int
    @property
    def Received(self) -> global___TransferResp.RecvResp:
        """Received is used when the client is sending the server data."""
    @property
    def Returned(self) -> global___TransferResp.SendResp:
        """Returned is used when the server is sending the client data."""
    def __init__(
        self,
        *,
        Received: global___TransferResp.RecvResp | None = ...,
        Returned: global___TransferResp.SendResp | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["Received", b"Received", "Resp", b"Resp", "Returned", b"Returned"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["Received", b"Received", "Resp", b"Resp", "Returned", b"Returned"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["Resp", b"Resp"]) -> typing_extensions.Literal["Received", "Returned"] | None: ...

global___TransferResp = TransferResp

@typing_extensions.final
class ChunkData(google.protobuf.message.Message):
    """ChunkData holds a chunk of data."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CHUNKSIZE_FIELD_NUMBER: builtins.int
    CHUNKDATA_FIELD_NUMBER: builtins.int
    ChunkSize: builtins.int
    """ChunkSize is the number of bytes in this chunk."""
    ChunkData: builtins.bytes
    """ChunkData is the byte data."""
    def __init__(
        self,
        *,
        ChunkSize: builtins.int = ...,
        ChunkData: builtins.bytes = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["ChunkData", b"ChunkData", "ChunkSize", b"ChunkSize"]) -> None: ...

global___ChunkData = ChunkData