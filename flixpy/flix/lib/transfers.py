import json
import os
import pathlib
import random
import ssl
import uuid
from collections.abc import Iterable
from typing import (
    BinaryIO,
    Callable,
    Union,
    AsyncIterable,
    AsyncIterator,
    Type,
    TypeVar,
    cast,
    TYPE_CHECKING,
)

import grpc.aio
from cryptography import x509
from grpc.aio import ClientCallDetails, StreamStreamCall

from . import client, errors, types, signing
from .proto import transfer_pb2_grpc, transfer_pb2


_CHUNK_SIZE = 8 * 1024


Streamer = Callable[[bytes], AsyncIterator[transfer_pb2.TransferReq]]
RequestType = TypeVar("RequestType")
ResponseType = TypeVar("ResponseType")
RequestIterableType = AsyncIterable[RequestType] | Iterable[RequestType]
ResponseIterableType = AsyncIterable[ResponseType]


def download_streamer() -> Streamer:
    async def streamer(metadata: bytes) -> AsyncIterator[transfer_pb2.TransferReq]:
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


def upload_streamer(f: BinaryIO, *, name: str, size: int) -> Streamer:
    async def streamer(metadata: bytes) -> AsyncIterator[transfer_pb2.TransferReq]:
        suffix = pathlib.Path(name).suffix
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


if TYPE_CHECKING:
    BaseInterceptor = grpc.aio.StreamStreamClientInterceptor[transfer_pb2.TransferReq, transfer_pb2.TransferResp]
else:
    BaseInterceptor = grpc.aio.StreamStreamClientInterceptor


class MessageSigner(BaseInterceptor):
    def __init__(self, access_key: "client.AccessKey"):
        self._access_key = access_key

    def intercept_stream_stream(  # type: ignore[override] # https://github.com/shabbyrobe/grpc-stubs/issues/47
        self,
        continuation: Callable[
            [ClientCallDetails, transfer_pb2.TransferReq],
            StreamStreamCall[transfer_pb2.TransferReq, transfer_pb2.TransferResp],
        ],
        client_call_details: ClientCallDetails,
        request_iterator: RequestIterableType[transfer_pb2.TransferReq],
    ) -> Union[
        ResponseIterableType[transfer_pb2.TransferResp],
        StreamStreamCall[transfer_pb2.TransferReq, transfer_pb2.TransferResp],
    ]:
        time = signing.get_time_rfc3999()
        # https://github.com/grpc/grpc/issues/31092
        if isinstance(client_call_details.method, bytes):
            method = client_call_details.method.decode()
        else:
            method = client_call_details.method
        message = f"{method}{time}"
        signature = signing.signature(message.encode(), self._access_key.secret_access_key)
        if client_call_details.metadata is not None:
            client_call_details.metadata.add("fnauth", f"{self._access_key.id}:{signature}")
            client_call_details.metadata.add("time", time)
        # https://github.com/shabbyrobe/grpc-stubs/issues/46
        return continuation(client_call_details, request_iterator)  # type: ignore[arg-type]


def get_channel(hostname: str, port: int, access_key: "client.AccessKey") -> grpc.aio.Channel:
    target = f"{hostname}:{port}"
    certificate, names = get_certificate(hostname, port)
    channel = grpc.aio.secure_channel(
        target,
        grpc.ssl_channel_credentials(certificate),
        [("grpc.ssl_target_name_override", name) for name in names],
        interceptors=[cast(grpc.aio.ClientInterceptor, MessageSigner(access_key))],
    )
    return channel


async def transfer(
    flix_client: "client.Client",
    asset_id: int,
    media_object_id: int,
    streamer: Streamer,
    filepath: str | None = None,
) -> AsyncIterator[transfer_pb2.TransferResp]:
    access_key = flix_client.access_key
    if access_key is None:
        raise errors.FlixError("must authenticate before transferring files")

    servers = await flix_client.servers()
    server: "types.Server" = random.choice(servers)
    async with get_channel(server.hostname, server.transfer_port, access_key) as channel:
        metadata = json.dumps(
            {
                "AssetID": asset_id,
                "MediaObjectID": media_object_id,
                "Filepath": filepath,
            }
        ).encode()

        stub = transfer_pb2_grpc.FileTransferStub(channel)
        if TYPE_CHECKING:
            async_stub = cast(transfer_pb2_grpc.FileTransferAsyncStub, stub)
        else:
            async_stub = stub

        async for resp in async_stub.Transfer(
            streamer(metadata),
            metadata=grpc.aio.Metadata(("x-flix-metadata", metadata)),
        ):
            yield resp


async def upload(
    flix_client: "client.Client",
    f: BinaryIO,
    asset_id: int,
    media_object_id: int,
    *,
    name: str | None = None,
    size: int | None = None,
) -> None:
    if name is None:
        name = f.name
    if size is None:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0, os.SEEK_SET)

    stream = transfer(
        flix_client,
        asset_id,
        media_object_id,
        streamer=upload_streamer(f, name=name, size=size),
        filepath=name,
    )
    async for _ in stream:
        pass


async def download(
    flix_client: "client.Client",
    asset_id: int,
    media_object_id: int,
) -> AsyncIterable[bytes]:
    stream = transfer(
        flix_client,
        asset_id,
        media_object_id,
        streamer=download_streamer(),
    )
    # read initial message
    _ = await anext(stream)
    async for resp in stream:
        yield resp.Returned.Data.ChunkData[: resp.Returned.Data.ChunkSize]
