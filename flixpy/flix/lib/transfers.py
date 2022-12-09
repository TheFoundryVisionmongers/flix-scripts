import json
import os
import pathlib
import random
import ssl
import uuid
from collections.abc import Iterable
from typing import BinaryIO, Callable, Union, AsyncIterable, AsyncIterator, Type, TypeVar, Protocol, cast, Generic

import grpc.aio  # type: ignore[import]
from cryptography import x509
from grpc.aio import ClientCallDetails
from grpc.aio._call import StreamStreamCall  # type: ignore[import]

from . import client, types, signing
from .proto import transfer_pb2_grpc, transfer_pb2


_CHUNK_SIZE = 8 * 1024


Streamer = Callable[[bytes], AsyncIterable[transfer_pb2.TransferReq]]
RequestType = TypeVar("RequestType", contravariant=True)
ResponseType = TypeVar("ResponseType", covariant=True)
RequestIterableType = AsyncIterable[RequestType] | Iterable[RequestType]
ResponseIterableType = AsyncIterable[ResponseType]


def download_streamer() -> Streamer:
    async def streamer(metadata: bytes) -> AsyncIterable[transfer_pb2.TransferReq]:
        transfer_id = str(uuid.uuid4())
        yield transfer_pb2.TransferReq(
            StartMsg=transfer_pb2.TransferReq.StartMessage(
                Action=transfer_pb2.TransferReq.StartMessage.DOWNLOAD,
                State=transfer_pb2.TransferReq.StartMessage.NEW,
                StartFrom=0,
                Metadata=metadata,
            ),
            UUID=transfer_id,
        )

        while True:
            yield transfer_pb2.TransferReq(DataMsg=transfer_pb2.TransferReq.DataMessage())

    return streamer


def upload_streamer(f: BinaryIO) -> Streamer:
    async def streamer(metadata: bytes) -> AsyncIterable[transfer_pb2.TransferReq]:
        suffix = pathlib.Path(f.name).suffix
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0, os.SEEK_SET)

        transfer_id = str(uuid.uuid4())
        yield transfer_pb2.TransferReq(
            StartMsg=transfer_pb2.TransferReq.StartMessage(
                Action=transfer_pb2.TransferReq.StartMessage.UPLOAD,
                State=transfer_pb2.TransferReq.StartMessage.NEW,
                StartFrom=0,
                TotalBytes=size,
                OriginalExt=suffix,
                Metadata=metadata,
            ),
            UUID=transfer_id,
        )

        while data := f.read(_CHUNK_SIZE):
            yield transfer_pb2.TransferReq(
                DataMsg=transfer_pb2.TransferReq.DataMessage(
                    Action=transfer_pb2.TransferReq.DataMessage.DATA,
                    Data=transfer_pb2.ChunkData(
                        ChunkSize=len(data),
                        ChunkData=data,
                    ),
                ),
                UUID=transfer_id,
            )

        yield transfer_pb2.TransferReq(
            CloseMsg=transfer_pb2.TransferReq.CloseMessage(
                Status=transfer_pb2.TransferReq.CloseMessage.COMPLETE,
            ),
            UUID=transfer_id,
        )

    return streamer


def get_certificate(hostname: str, port: int) -> tuple[bytes, Iterable[str]]:
    certificate_data = ssl.get_server_certificate((hostname, port)).encode()
    cert = x509.load_pem_x509_certificate(certificate_data)
    alt_names = cert.extensions.get_extension_for_class(x509.extensions.SubjectAlternativeName).value
    name_types: list[Type[x509.IPAddress | x509.DNSName]] = [x509.IPAddress, x509.DNSName]
    return certificate_data, [
        str(name) for name_type in name_types for name in alt_names.get_values_for_type(name_type)
    ]


class MessageSigner(grpc.aio.StreamStreamClientInterceptor, Generic[RequestType, ResponseType]):  # type: ignore[misc]
    def __init__(self, access_key: "client.AccessKey"):
        self._access_key = access_key

    def intercept_stream_stream(
        self,
        continuation: Callable[[ClientCallDetails, RequestIterableType[RequestType]], StreamStreamCall],
        client_call_details: ClientCallDetails,
        request_iterator: RequestIterableType[RequestType],
    ) -> Union[ResponseIterableType[ResponseType], StreamStreamCall]:
        time = signing.get_time_rfc3999()
        message = f"{client_call_details.method.decode()}{time}"
        signature = signing.signature(message.encode(), self._access_key.secret_access_key)
        client_call_details.metadata.add("fnauth", f"{self._access_key.id}:{signature}")
        client_call_details.metadata.add("time", time)
        return continuation(client_call_details, request_iterator)


def get_channel(hostname: str, port: int, access_key: "client.AccessKey") -> grpc.aio.Channel:
    target = f"{hostname}:{port}"
    certificate, names = get_certificate(hostname, port)
    channel = grpc.aio.secure_channel(
        target,
        grpc.ssl_channel_credentials(certificate),
        [("grpc.ssl_target_name_override", name) for name in names],
        interceptors=[MessageSigner(access_key)],
    )
    return channel


class AsyncStreamStreamMultiCallable(Protocol[RequestType, ResponseType]):
    def __call__(
        self,
        request_iterator: RequestIterableType[RequestType],
        timeout: float | None = None,
        metadata: grpc.aio.Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
        wait_for_ready: bool | None = None,
        compression: grpc.Compression | None = None,
    ) -> ResponseIterableType[ResponseType]:
        ...


class AsyncFileTransferStub:
    """FileTransfer is the server which handles data transfers."""

    def __init__(self, channel: grpc.aio.Channel) -> None:
        ...

    Transfer: AsyncStreamStreamMultiCallable[
        transfer_pb2.TransferReq,
        transfer_pb2.TransferResp,
    ]


async def transfer(
    flix_client: "client.Client",
    asset_id: int,
    media_object_id: int,
    streamer: Streamer,
    filepath: str | None = None,
) -> AsyncIterator[transfer_pb2.TransferResp]:
    access_key = flix_client.access_key
    if access_key is None:
        raise RuntimeError("must authenticate before transferring files")

    servers = await flix_client.servers()
    server: "types.Server" = random.choice(servers)
    channel = get_channel(server.hostname, server.transfer_port, access_key)
    metadata = json.dumps(
        {
            "AssetID": asset_id,
            "MediaObjectID": media_object_id,
            "Filepath": filepath,
        }
    ).encode()

    # https://github.com/nipunn1313/mypy-protobuf/issues/216
    stub = cast(AsyncFileTransferStub, transfer_pb2_grpc.FileTransferStub(channel))

    async for resp in stub.Transfer(
        streamer(metadata),
        metadata=grpc.aio.Metadata(("x-flix-metadata", metadata)),
    ):
        yield resp


async def upload(
    flix_client: "client.Client",
    f: BinaryIO,
    asset_id: int,
    media_object_id: int,
) -> None:
    async for _ in transfer(flix_client, asset_id, media_object_id, upload_streamer(f), filepath=f.name):
        pass


async def download(
    flix_client: "client.Client",
    asset_id: int,
    media_object_id: int,
) -> AsyncIterable[bytes]:
    stream = transfer(flix_client, asset_id, media_object_id, download_streamer())
    # read initial message
    _ = await anext(stream)
    async for resp in stream:
        yield resp.Returned.Data.ChunkData[: resp.Returned.Data.ChunkSize]
