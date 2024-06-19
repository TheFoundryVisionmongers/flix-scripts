"""Pythonic abstractions of the models used by the Flix Server REST API."""

from __future__ import annotations

import base64
import collections.abc
import contextlib
import dataclasses
import datetime
import enum
import os
import pathlib
from collections.abc import AsyncIterable, Callable, Iterable, Iterator, Mapping, MutableMapping
from typing import Any, BinaryIO, Literal, Protocol, TypedDict, cast

import dateutil.parser

from . import client, errors, models, transfers, websocket

__all__ = [
    "MetadataField",
    "Metadata",
    "Group",
    "Permission",
    "Role",
    "GroupRolePair",
    "User",
    "MediaObjectStatus",
    "MediaObjectHash",
    "MediaObject",
    "Episode",
    "Sequence",
    "Asset",
    "ContactSheetOrientation",
    "ContactSheetStyle",
    "ContactSheetPanelOptions",
    "ContactSheetCoverOptions",
    "ContactSheet",
    "Show",
    "Keyframe",
    "PanelComment",
    "OriginSBP",
    "OriginAvid",
    "OriginFCPXML",
    "DuplicateRef",
    "Panel",
    "PanelRevision",
    "SequencePanel",
    "SequenceRevision",
    "DialogueFormat",
    "Server",
    "Dialogue",
    "ColorTag",
]


def _params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class FlixType:
    def __init__(self, _client: client.Client | None) -> None:
        self._client = _client

    @property
    def client(self) -> client.Client:
        if self._client is None:
            raise errors.FlixError("client is not set")
        return self._client


class AddressableFlixType(Protocol):
    def path_prefix(self) -> str:
        ...


class MetadataField:
    def __init__(
        self,
        value: Any | None,
        *,
        value_type: str = "",
        created_date: datetime.datetime | None = None,
        modified_date: datetime.datetime | None = None,
    ) -> None:
        self._value = value
        self._value_type = value_type
        self.created_date = created_date or datetime.datetime.now(datetime.timezone.utc)
        self.modified_date = modified_date or datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    def from_dict(cls, data: models.MetadataField) -> MetadataField:
        if data["value"] and data["value_type"] == "datetime":
            value = dateutil.parser.parse(data["value"])
        else:
            value = data["value"]

        return cls(
            value=value,
            value_type=data["value_type"],
            created_date=dateutil.parser.parse(data["created_date"]),
            modified_date=dateutil.parser.parse(data["modified_date"]),
        )

    def to_dict(self, name: str) -> models.MetadataField:
        return models.MetadataField(
            name=name,
            value=self.json_value,
            value_type=self.value_type,
        )

    @property
    def value(self) -> Any | None:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value
        # leave any existing value type unchanged if just nulling out the value
        if value is not None:
            self._value_type = ""
        self.modified_date = datetime.datetime.now(datetime.timezone.utc)

    @property
    def value_type(self) -> str:
        if self._value_type == "":
            self._value_type = MetadataField.get_value_type(self.value)
        return self._value_type

    @staticmethod
    def get_value_type(value: Any) -> str:  # noqa: PLR0911
        match value:
            case bool():
                return "bool"
            case int():
                return "int"
            case float():
                return "float"
            case datetime.datetime():
                return "datetime"
            case str():
                return "string"
            case collections.abc.Sequence() as seq if all(isinstance(elem, str) for elem in seq):
                return "stringarray"
        return "object"

    @property
    def json_value(self) -> Any | None:
        match self.value:
            case datetime.datetime() as d:
                if d.tzinfo is None:
                    # make timezone aware to ensure correct date format; assume UTC
                    d = d.replace(tzinfo=datetime.timezone.utc)
                return d.isoformat()
            case _:
                return self.value

    @property
    def string_value(self) -> str | None:
        if self.value is None:
            return None
        return str(self.value)

    @property
    def int_value(self) -> int | None:
        if self.value is None:
            return None
        return int(self.value)

    @property
    def float_value(self) -> float | None:
        if self.value is None:
            return None
        return float(self.value)

    @property
    def bool_value(self) -> bool | None:
        if self.value is None:
            return None
        return bool(self.value)

    @property
    def stringarray_value(self) -> list[str] | None:
        match self.value:
            case None:
                return None
            case [*elems]:
                return [str(elem) for elem in elems]
            case other:
                return [str(other)]

    def __repr__(self) -> str:
        return (
            f"MetadataField(value={self.value}, value_type={self.value_type}, "
            f"created_date={self.created_date}, modified_date={self.modified_date})"
        )


class _MetadataModel(TypedDict):
    metadata: list[models.MetadataField]


class Metadata(FlixType, MutableMapping[str, Any]):
    def __init__(
        self,
        metadata: Mapping[str, Any] | None = None,
        *,
        parent: AddressableFlixType | None,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._fields = dict[str, MetadataField]()
        self._parent = parent
        if metadata is not None:
            if isinstance(metadata, Metadata):
                self._fields = metadata._fields
            else:
                for name, value in metadata.items():
                    self[name] = value

    @classmethod
    def from_dict(
        cls,
        data: list[models.MetadataField] | None,
        *,
        into: Metadata | None = None,
        parent: AddressableFlixType | None,
        _client: client.Client | None,
    ) -> Metadata:
        if into is None:
            into = cls(parent=parent, _client=_client)
        else:
            into.clear()

        if data is not None:
            for field in data:
                into.set_field(field["name"], MetadataField.from_dict(field))
        return into

    def to_dict(self) -> list[models.MetadataField]:
        return [field.to_dict(name) for name, field in self._fields.items()]

    def get_field(self, key: str) -> MetadataField:
        return self._fields[key]

    def get_string(self, key: str) -> str | None:
        return self._fields[key].string_value

    def get_bool(self, key: str) -> bool | None:
        return self._fields[key].bool_value

    def get_int(self, key: str) -> int | None:
        return self._fields[key].int_value

    def get_float(self, key: str) -> float | None:
        return self._fields[key].float_value

    def get_stringarray(self, key: str) -> list[str] | None:
        return self._fields[key].stringarray_value

    def set_field(self, key: str, value: MetadataField) -> None:
        self._fields[key] = value

    def path_prefix(self) -> str:
        if self._parent is None:
            raise errors.FlixError("metadata parent is not set")
        return f"{self._parent.path_prefix()}/metadata"

    async def fetch_metadata(self) -> Metadata:
        result = cast(_MetadataModel, await self.client.get(self.path_prefix()))
        Metadata.from_dict(result["metadata"], into=self, parent=self._parent, _client=self.client)
        return self

    async def fetch_field(self, name: str) -> MetadataField:
        result = cast(
            models.MetadataField, await self.client.get(self.path_prefix(), params={"name": name})
        )
        field = MetadataField.from_dict(result)
        self.set_field(name, field)
        return field

    async def delete_field(self, name: str) -> None:
        del self[name]
        await self.client.delete(self.path_prefix(), params={"name": name})

    async def set_and_save(self, name: str, value: Any) -> None:
        self[name] = value
        await self.client.put(
            self.path_prefix(), body=self.get_field(name).to_dict(name), params={"name": name}
        )

    async def set_field_and_save(self, name: str, field: MetadataField) -> None:
        self.set_field(name, field)
        await self.client.put(
            self.path_prefix(), body=self.get_field(name).to_dict(name), params={"name": name}
        )

    async def save(self, clear_missing: bool = False) -> None:
        method = "PUT" if clear_missing else "PATCH"
        await self.client.request(
            method, self.path_prefix(), body=_MetadataModel(metadata=self.to_dict())
        )

    def __getitem__(self, key: str) -> Any:
        return self.get_field(key).value

    def __setitem__(self, key: str, value: Any) -> None:
        if field := self._fields.get("key"):
            field.value = value
        else:
            self._fields[key] = MetadataField(value)

    def __delitem__(self, key: str) -> None:
        del self._fields[key]

    def __len__(self) -> int:
        return len(self._fields)

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def clear(self) -> None:
        self._fields.clear()

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={field.value}" for name, field in self._fields.items())
        return f"Metadata({fields})"


@dataclasses.dataclass
class Group:
    title: str
    group_id: int | None = None

    @staticmethod
    def from_dict(data: models.Group) -> Group:
        return Group(
            title=data.get("title", ""),
            group_id=data["id"],
        )

    def to_dict(self) -> models.Group:
        group = models.Group(
            title=self.title,
        )
        if self.group_id is not None:
            group["id"] = self.group_id
        return group


@dataclasses.dataclass
class Permission:
    name: str
    mask: int

    @staticmethod
    def from_dict(data: models.Permission) -> Permission:
        return Permission(
            name=data["name"],
            mask=data["mask"],
        )

    def to_dict(self) -> models.Permission:
        return models.Permission(
            name=self.name,
            mask=self.mask,
        )


@dataclasses.dataclass
class Role:
    name: str
    permissions: list[Permission]
    role_id: int | None = None

    @staticmethod
    def from_dict(data: models.Role) -> Role:
        return Role(
            role_id=data["id"],
            name=data.get("name", ""),
            permissions=[Permission.from_dict(role) for role in data.get("permissions") or []],
        )


@dataclasses.dataclass
class GroupRolePair:
    group: Group
    role: Role

    @staticmethod
    def from_dict(data: models.GroupRolePair) -> GroupRolePair:
        return GroupRolePair(
            group=Group.from_dict(data["group"]),
            role=Role.from_dict(data["role"]),
        )


class User(FlixType):
    def __init__(
        self,
        username: str = "",
        email: str = "",
        is_admin: bool = False,
        groups: list[GroupRolePair] | None = None,
        *,
        user_id: int | None = None,
        password: str | None = None,
        created_date: datetime.datetime | None = None,
        is_system: bool = False,
        is_third_party: bool = False,
        user_type: str = "flix",
        deleted: bool = False,
        metadata: Mapping[str, Any] | None = None,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.groups = groups or []
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.user_type = user_type
        self.is_admin = is_admin
        self.is_system = is_system
        self.is_third_party = is_third_party
        self.deleted = deleted
        self.metadata = Metadata(metadata, parent=self, _client=_client)

    @classmethod
    def from_dict(
        cls, data: models.User, *, into: User | None = None, _client: client.Client | None
    ) -> User:
        if into is None:
            into = cls(_client=_client)
        into.user_id = data["id"]
        into.username = data.get("username", "")
        into.email = data.get("email", "")
        into.groups = [GroupRolePair.from_dict(group) for group in data.get("groups") or []]
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.user_type = data.get("type", "")
        into.is_admin = data.get("is_admin", False)
        into.is_system = data.get("is_system", False)
        into.is_third_party = data.get("is_third_party", False)
        into.deleted = data.get("deleted", False)
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        return into

    def path_prefix(self) -> str:
        return f"/user/{self.user_id}"


class MediaObjectStatus(enum.Enum):
    """Describes the status of a media object."""

    INITIALIZED = 0
    """The media object has been created, but no file data has been uploaded."""
    UPLOADED = 1
    """File data has been successfully uploaded for the media object."""
    ERRORED = 2
    """The media object is in a failed state."""


@dataclasses.dataclass
class MediaObjectHash:
    """A hash of the contents of the file described by a media object.

    This may be a simple MD5 hash of the file,
    but it could also be something like a perceptual hash allowing for
    measuring the visual similarity of two images.
    """

    value: str
    """The hash string used to find other possibly identical files."""
    source_type: str
    """The type of this hash."""
    data: bytes | None
    """Optional binary data allowing for more fine-grained comparison of files."""

    @classmethod
    def from_dict(cls, data: models.Hash) -> MediaObjectHash:
        return cls(
            value=data["value"],
            source_type=data["source_type"],
            data=base64.b64decode(data["data"]) if data.get("data") else None,
        )

    def to_dict(self) -> models.Hash:
        h = models.Hash(
            value=self.value,
            source_type=self.source_type,
        )
        if self.data is not None:
            h["data"] = base64.b64encode(self.data).decode()
        return h


class MediaObject(FlixType):
    """Represents a single physical file within an asset."""

    def __init__(
        self,
        media_object_id: int = 0,
        asset_id: int = 0,
        filename: str = "",
        content_type: str = "",
        content_length: int = 0,
        content_hashes: list[MediaObjectHash] | None = None,
        created_date: datetime.datetime | None = None,
        status: MediaObjectStatus = MediaObjectStatus.INITIALIZED,
        owner: User | None = None,
        asset_type: str = "",
        *,
        _client: client.Client | None,
    ) -> None:
        """Initialise a MediaObject.

        Args:
            media_object_id: The unique ID of the media object.
            asset_id: The ID of the asset this media object belongs to.
            filename: The name of the file described by this media object.
            content_type: The content type of the file described by this media object.
            content_length: The size of the file described by this media object.
            content_hashes: Hashes for comparing the contents of the file
                described by this media object.
            created_date: The date this media object was created.
            status: The status of this media object.
            owner: The user that created this media object.
            asset_type: A string describing the purpose of this media object,
                e.g. `"artwork"` or `"thumbnail"`
            _client: A [Client][flix.Client] instance.
        """
        super().__init__(_client)
        self.media_object_id: int = media_object_id
        self.asset_id: int = asset_id
        self.filename: str = filename
        self.content_type: str = content_type
        self.content_length: int = content_length
        self.content_hashes: list[MediaObjectHash] = content_hashes or []
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.status: MediaObjectStatus = status
        self.owner: User | None = owner
        self.asset_type: str = asset_type

    @classmethod
    def from_dict(
        cls,
        data: models.MediaObject,
        *,
        into: MediaObject | None = None,
        _client: client.Client | None,
    ) -> MediaObject:
        if into is None:
            into = cls(_client=_client)
        into.media_object_id = data["id"]
        into.asset_id = data["asset_id"]
        into.filename = data.get("name", "")
        into.content_type = data.get("content_type", "")
        into.content_length = data.get("content_length", 0)
        into.content_hashes = [
            MediaObjectHash.from_dict(h) for h in data.get("content_hashes") or []
        ]
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.status = (
            MediaObjectStatus(data["status"])
            if data.get("status")
            else MediaObjectStatus.INITIALIZED
        )
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.asset_type = data.get("asset_type", "")
        into._client = _client  # noqa: SLF001
        return into

    async def update(self) -> None:
        path = f"/file/{self.media_object_id}"
        result = cast(models.MediaObject, await self.client.get(path))
        self.from_dict(result, into=self, _client=self.client)

    async def upload(
        self, f: BinaryIO, *, name: str | None = None, size: int | None = None
    ) -> None:
        """Populate this media object with a file.

        Args:
            f: The file to upload.
            name: The name of the file. If not provided, the name will be fetched
                from the file handle. Useful when uploading a file handle that
                doesn't correspond to a physical file on disk.
            size: The total size of the file. If not provided, the size will be
                automatically detected from the file handle.
        """
        if name is None:
            name = f.name
        if size is None:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0, os.SEEK_SET)

        await transfers.upload(
            self.client,
            transfers.chunk_file(f),
            self.asset_id,
            self.media_object_id,
            name=name,
            size=size,
        )

        # fetching the media object info requires download permissions,
        # so if we only have upload permissions, skip updating the local mo info
        with contextlib.suppress(errors.FlixHTTPError):
            await self.update()

    async def upload_stream(self, stream: AsyncIterable[bytes], *, name: str, size: int) -> None:
        """Populate this media object with data from a stream.

        Args:
            stream: The data stream to upload.
            name: The name of the file.
            size: The total size of the file.
        """
        await transfers.upload(
            self.client,
            stream,
            self.asset_id,
            self.media_object_id,
            name=name,
            size=size,
        )

        with contextlib.suppress(errors.FlixHTTPError):
            await self.update()

    async def download(self) -> bytes:
        """Get the file contents of this media object.

        This function should not be used to download large files
        that may not fit in memory.

        Returns:
            A byte string containing the entire file contents of this media object.
        """
        return b"".join(
            [
                chunk
                async for chunk in transfers.download(
                    self.client, self.asset_id, self.media_object_id
                )
            ]
        )

    async def download_to(
        self, directory: str | os.PathLike[str], filename: str | None = None
    ) -> pathlib.Path:
        """Save this media object's file contents to disk.

        Args:
            directory: The directory to download the file to.
            filename: The name of the file inside the directory.
                If not specified, a unique filename for this media object will be picked.

        Returns:
            The path to the saved file.
        """
        dirpath = pathlib.Path(directory)
        dirpath.mkdir(parents=True, exist_ok=True)
        if filename is None:
            path = dirpath / f"{self.media_object_id}_{self.filename}"
        else:
            path = dirpath / filename

        with path.open("wb") as f:
            async for chunk in transfers.download(self.client, self.asset_id, self.media_object_id):
                f.write(chunk)

        return path


@dataclasses.dataclass
class ColorTag:
    color_tag_id: int | None = None
    color_name: str = ""
    value: str = ""

    @classmethod
    def from_dict(cls, data: models.ColorTag) -> ColorTag:
        return cls(
            color_tag_id=data["id"],
            color_name=data["colour_name"],
            value=data["value"],
        )

    def to_dict(self) -> models.ColorTag:
        return models.ColorTag(
            id=self.color_tag_id or 0,
            colour_name=self.color_name,
            value=self.value,
        )


class Episode(FlixType):
    def __init__(
        self,
        episode_number: int = 0,
        tracking_code: str = "",
        description: str = "",
        title: str = "",
        hidden: bool = False,
        *,
        episode_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        metadata: Mapping[str, Any] | None = None,
        _show: Show,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._show = _show
        self.tracking_code = tracking_code
        self.description = description
        self.title = title
        self.episode_id = episode_id
        self.episode_number = episode_number
        self.created_date = created_date
        self.owner = owner
        self.hidden = hidden
        self.metadata = Metadata(metadata, parent=self, _client=_client)

    @classmethod
    def from_dict(
        cls,
        data: models.Episode,
        *,
        into: Episode | None = None,
        _show: Show,
        _client: client.Client | None,
    ) -> Episode:
        if into is None:
            into = cls(_show=_show, _client=_client)
        into.episode_id = data["id"]
        into.episode_number = data.get("episode_number", 0)
        into.tracking_code = data.get("tracking_code", "")
        into.description = data.get("description", "")
        into.title = data.get("title", "")
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client)
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        into.hidden = data["hidden"]
        return into

    def to_dict(self) -> models.Episode:
        episode = models.Episode(
            episode_number=self.episode_number,
            tracking_code=self.tracking_code,
            description=self.description,
            title=self.title,
            metadata=self.metadata.to_dict(),
            hidden=self.hidden,
        )
        if self.episode_id is not None:
            episode["id"] = self.episode_id
        return episode

    def path_prefix(self) -> str:
        return f"{self._show.path_prefix()}/episode/{self.episode_id}"

    async def get_all_sequences(
        self, include_hidden: bool = False, page: int | None = None, per_page: int | None = None
    ) -> list[Sequence]:
        class _AllSequences(TypedDict):
            sequences: list[models.Sequence]

        path = f"{self.path_prefix()}/sequences"
        params = _params(
            display_hidden="true" if include_hidden else None,
            page=page,
            per_page=per_page,
        )
        all_sequences = cast(_AllSequences, await self.client.get(path, params=params))
        return [
            Sequence.from_dict(sequence, _show=self._show, _episode=self, _client=self.client)
            for sequence in all_sequences["sequences"]
        ]

    async def save(self, force_create_new: bool = False) -> None:
        """Save this episode.

        Args:
            force_create_new: Always create a new episode instead of updating an existing one.
        """
        if self.episode_id is None or force_create_new:
            path = f"{self._show.path_prefix()}/episode"
            result = cast(models.Episode, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.Episode, await self.client.patch(path, body=self.to_dict()))
        self.from_dict(result, into=self, _show=self._show, _client=self.client)


class Sequence(FlixType):
    def __init__(
        self,
        tracking_code: str = "",
        description: str = "",
        hidden: bool = False,
        color_tag: ColorTag | None = None,
        *,
        sequence_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        revision_count: int = 0,
        panel_revision_count: int = 0,
        metadata: Mapping[str, Any] | None = None,
        _show: Show,
        _episode: Episode | None,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._show = _show
        self._episode = _episode
        self.sequence_id = sequence_id
        self.tracking_code = tracking_code
        self.description = description
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.owner = owner
        self.revision_count = revision_count
        self.panel_revision_count = panel_revision_count
        self.metadata = Metadata(metadata, parent=self, _client=_client)
        self.hidden = hidden
        self.color_tag = color_tag

    @classmethod
    def from_dict(
        cls,
        data: models.Sequence,
        *,
        into: Sequence | None = None,
        _show: Show,
        _episode: Episode | None,
        _client: client.Client | None,
    ) -> Sequence:
        if into is None:
            into = cls(_show=_show, _episode=_episode, _client=_client)
        into.sequence_id = data["id"]
        into.tracking_code = data.get("tracking_code", "")
        into.description = data.get("description", "")
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.revision_count = data.get("revisions_count", 0)
        into.panel_revision_count = data.get("panel_revision_count", 0)
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        into.hidden = data.get("hidden", False)
        into.color_tag = ColorTag.from_dict(c) if (c := data.get("colour_tag")) else None
        return into

    def to_dict(self) -> models.Sequence:
        sequence = models.Sequence(
            tracking_code=self.tracking_code,
            description=self.description,
            hidden=self.hidden,
            metadata=self.metadata.to_dict(),
            colour_tag=self.color_tag.to_dict() if self.color_tag else None,
        )
        if self.sequence_id is not None:
            sequence["id"] = self.sequence_id

        return sequence

    @property
    def show(self) -> Show:
        return self._show

    @property
    def episode(self) -> Episode | None:
        return self._episode

    def path_prefix(self, include_episode: bool = True) -> str:
        if self._episode is not None and include_episode:
            return f"{self._episode.path_prefix()}/sequence/{self.sequence_id}"
        else:
            return f"{self._show.path_prefix()}/sequence/{self.sequence_id}"

    @property
    def color_tag_name(self) -> str:
        """The name of the current color tag for this sequence.

        This property allows for getting and setting color tags by name.
        If a color tag is set by name, the corresponding ID will be looked up
        when saving the sequence.

        Setting the name to the empty string will clear the color tag.
        Setting an invalid name will cause an error on save.
        """
        if self.color_tag is not None:
            return self.color_tag.color_name
        else:
            return ""

    @color_tag_name.setter
    def color_tag_name(self, value: str) -> None:
        if value != "":
            self.color_tag = ColorTag(color_name=value)
        else:
            self.color_tag = None

    def new_sequence_revision(
        self,
        comment: str = "",
        panels: list[SequencePanel] | None = None,
        source_files: list[Asset] | None = None,
    ) -> SequenceRevision:
        return SequenceRevision(
            comment=comment,
            panels=panels,
            source_files=source_files,
            _sequence=self,
            _client=self.client,
        )

    def new_panel(
        self,
        origin: str = "Manual Import",
        asset: Asset | None = None,
        is_ref: bool = False,
        related_panels: list[PanelRevision] | None = None,
    ) -> PanelRevision:
        return PanelRevision(
            origin=origin,
            asset=asset,
            is_ref=is_ref,
            related_panels=related_panels,
            _sequence=self,
            _client=self.client,
        )

    async def save_panels(self, panels: list[PanelRevision]) -> None:
        """Save a batch of panel revisions.

        Each panel revision will be given a new panel ID.
        """

        class _Panels(TypedDict):
            panels: list[models.PanelRevision]

        prefix = self.path_prefix(include_episode=False)
        path = f"{prefix}/panels"
        result = cast(
            _Panels, await self.client.post(path, body=[panel.to_dict() for panel in panels])
        )
        for i, result_panel in enumerate(result["panels"]):
            PanelRevision.from_dict(
                result_panel, into=panels[i], _sequence=self, _client=self.client
            )

    async def get_sequence_revision(
        self, revision_number: int, *, fetch_panels: bool = False
    ) -> SequenceRevision:
        """Fetch an existing revision of this sequence.

        Args:
            revision_number: The revision number of the sequence revision to fetch.
            fetch_panels: Automatically populate the sequence revision with its panels.

        Returns:
            The sequence revision with the requested revision number.
        """
        path = f"{self.path_prefix()}/revision/{revision_number}"
        revision = cast(models.SequenceRevision, await self.client.get(path))
        seqrev = SequenceRevision.from_dict(revision, _sequence=self, _client=self.client)

        if fetch_panels:
            await seqrev.get_all_panel_revisions()
        return seqrev

    async def get_all_sequence_revisions(self) -> list[SequenceRevision]:
        class _AllRevisions(TypedDict):
            sequence_revisions: list[models.SequenceRevision]

        path = f"{self.path_prefix()}/revisions"
        all_revisions = cast(_AllRevisions, await self.client.get(path))
        return [
            SequenceRevision.from_dict(revision, _sequence=self, _client=self.client)
            for revision in all_revisions["sequence_revisions"]
        ]

    async def get_panel_revision(self, panel_id: int, panel_revision: int) -> PanelRevision:
        prefix = self.path_prefix(include_episode=False)
        path = f"{prefix}/panel/{panel_id}/revision/{panel_revision}"
        result = cast(models.PanelRevision, await self.client.get(path))
        return PanelRevision.from_dict(result, _sequence=self, _client=self.client)

    async def get_all_panel_revisions(
        self,
        latest_revision_only: bool = True,
        page: int | None = None,
        per_page: int | None = None,
    ) -> list[PanelRevision]:
        class _AllPanels(TypedDict):
            panels: list[models.PanelRevision]

        path = f"{self.path_prefix(include_episode=False)}/panels"
        params = _params(
            showAll="true" if not latest_revision_only else None,
            page=page,
            per_page=per_page,
        )
        all_panels = cast(_AllPanels, await self.client.get(path, params=params))
        return [
            PanelRevision.from_dict(panel, _sequence=self, _client=self.client)
            for panel in all_panels["panels"]
        ]

    async def import_aaf(
        self,
        aaf_asset: Asset,
        comment: str = "",
        extra_params: Mapping[str, Any] | None = None,
        timeout: float | None = None,
        chain_status_callback: Callable[[websocket.MessageJobChainStatus], None] | None = None,
        panel_status_callback: Callable[[websocket.MessageEditorialImportStatus], None]
        | None = None,
    ) -> SequenceRevision:
        path = f"{self.path_prefix()}/revision/0/reconform/avid"
        params = extra_params or {}
        async with self.client.websocket() as ws:
            await self.client.post(
                path,
                body={
                    "asset_id": aaf_asset.asset_id,
                    "client_id": ws.client_id,
                    "comment": comment,
                    "publish_settings": {
                        "bitrate": "36M",
                    },
                    **params,
                },
            )

            waiter = ws.wait_on_chain(
                websocket.MessageEditorialImportComplete,
                message_filter=(websocket.MessageEditorialImportStatus,),
                timeout=timeout,
            )
            async for msg in waiter:
                if (
                    isinstance(msg, websocket.MessageJobChainStatus)
                    and chain_status_callback is not None
                ):
                    chain_status_callback(msg)
                elif (
                    isinstance(msg, websocket.MessageEditorialImportStatus)
                    and panel_status_callback is not None
                ):
                    panel_status_callback(msg)
            return await waiter.result.get_sequence_revision(self)

    async def save(self, force_create_new: bool = False) -> None:
        """Save this sequence.

        Args:
            force_create_new: Always create a new sequence instead of updating an existing one.
        """
        if self.color_tag is not None and self.color_tag.color_tag_id is None:
            self.color_tag = await self.show.get_color_tag("sequence", self.color_tag.color_name)

        if self.sequence_id is None or force_create_new:
            path = f"{self._show.path_prefix()}/sequence"
            result = cast(models.Sequence, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.Sequence, await self.client.patch(path, body=self.to_dict()))
        self.from_dict(
            result, into=self, _show=self._show, _episode=self._episode, _client=self.client
        )

    async def delete(self) -> None:
        path = self.path_prefix()
        await self.client.delete(path)


class Asset(FlixType):
    """A collection of files.

    An asset generally contains one or more [media objects][flix.MediaObject],
    grouped by [asset type][flix.MediaObject.asset_type].
    For instance, an asset belonging to an animated panel might contain a single
    `artwork` media object for the original artwork created by the artist,
    a `source_media` media object containing a prerendered QuickTime of the panel,
    and a number of `thumbnail` media objects, one per frame.
    """

    def __init__(
        self,
        *,
        asset_id: int = 0,
        show_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        media_objects: dict[str, list[MediaObject]] | None = None,
        _client: client.Client | None,
    ) -> None:
        """Initialise an Asset.

        Args:
            asset_id: The unique ID of the asset.
            show_id: The ID of the show this asset belongs to.
            created_date: The time this asset was created.
            owner: The user that created this asset.
            media_objects: The media objects belonging to this asset.
            _client: A [Client][flix.Client] instance.
        """
        super().__init__(_client)
        self.asset_id: int = asset_id
        self.show_id: int | None = show_id
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.owner: User | None = owner
        self.media_objects: dict[str, list[MediaObject]] = media_objects or {}

    @staticmethod
    def from_dict(data: models.Asset, *, _client: client.Client | None) -> Asset:
        return Asset(
            asset_id=data["asset_id"],
            show_id=data["show_id"],
            created_date=dateutil.parser.parse(data["created_date"]),
            owner=(
                User.from_dict(data["owner_id"], _client=_client) if data.get("owner_id") else None
            ),
            media_objects={
                ref: [MediaObject.from_dict(mo, _client=_client) for mo in mos]
                for ref, mos in (data.get("media_objects") or {}).items()
            },
            _client=_client,
        )

    def to_dict(self) -> models.Asset:
        asset = models.Asset(asset_id=self.asset_id)
        if self.show_id is not None:
            asset["show_id"] = self.show_id
        return asset

    async def create_media_object(self, ref: str) -> MediaObject:
        class _MediaObjects(TypedDict):
            media_objects: list[models.MediaObject]

        path = f"/show/{self.show_id}/media_object/{ref}"
        body = {"asset_ids": [self.asset_id]}
        mos = cast(_MediaObjects, await self.client.post(path, body=body))
        media_object = MediaObject.from_dict(mos["media_objects"][0], _client=self.client)
        self.media_objects.setdefault(ref, []).append(media_object)
        return media_object


class ContactSheetOrientation(enum.Enum):
    LANDSCAPE = 0
    PORTRAIT = 1


class ContactSheetStyle(enum.Enum):
    SINGLE_PANEL = 0
    GRID = 1
    LIST = 2


class ContactSheetPanelOptions(enum.Enum):
    PANEL_ID = "panel id"
    PANEL_NUMBER = "panel number"
    DIALOGUE = "dialogue"
    HIGHLIGHT_TAG = "highlight tag"
    NEW_MARKER = "new marker"
    PANEL_DURATION = "panel duration"
    ANNOTATIONS = "annotations"
    DATE_AND_TIME = "date and time"


class ContactSheetCoverOptions(enum.Enum):
    SHOW_NAME = "show name"
    SEQUENCE_NAME = "sequence name"
    REVISION = "revision"
    REVISION_COMMENT = "revision comment"


class ContactSheet(FlixType):
    def __init__(
        self,
        name: str = "",
        orientation: ContactSheetOrientation = ContactSheetOrientation.PORTRAIT,
        width: int = 210,
        height: int = 297,
        style: ContactSheetStyle = ContactSheetStyle.SINGLE_PANEL,
        columns: int | None = None,
        rows: int | None = None,
        panel_options: Iterable[ContactSheetPanelOptions] = (),
        show_header: bool = True,
        show_comments: bool = True,
        show_watermark: bool = True,
        show_company: bool = True,
        show_cover: bool = False,
        cover_options: Iterable[ContactSheetCoverOptions] = (),
        cover_description: str = "",
        *,
        contactsheet_id: int | None = None,
        owner: User | None = None,
        created_date: datetime.datetime | None = None,
        modified_date: datetime.datetime | None = None,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self.contactsheet_id = contactsheet_id
        self.name = name
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.modified_date: datetime.datetime = modified_date or datetime.datetime.now(
            datetime.timezone.utc
        )

        self.orientation = orientation
        self.width = width
        self.height = height
        self.style = style
        self.columns = columns
        self.rows = rows
        self.panel_options = set(panel_options)
        self.show_header = show_header
        self.show_comments = show_comments
        self.show_watermark = show_watermark
        self.show_company = show_company
        self.show_cover = show_cover
        self.cover_options = set(cover_options)
        self.cover_description = cover_description

    @classmethod
    def from_dict(
        cls,
        data: models.ContactSheet,
        *,
        into: ContactSheet | None = None,
        _client: client.Client | None,
    ) -> ContactSheet:
        if into is None:
            into = cls(_client=_client)
        into.contactsheet_id = data["id"]
        into.name = data["name"]
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.modified_date = dateutil.parser.parse(data["modified_date"])
        into.orientation = ContactSheetOrientation(data["orientation"])
        into.width = data["page_size"]["width"]
        into.height = data["page_size"]["height"]
        into.style = ContactSheetStyle(data["style"])
        into.columns = data.get("columns")
        into.rows = data.get("rows")
        into.panel_options = {
            ContactSheetPanelOptions(opt) for opt in data.get("panel_options") or ()
        }
        into.show_header = data["show_header"]
        into.show_comments = data["show_comments"]
        into.show_watermark = data["show_watermark"]
        into.show_company = data["show_company"]
        into.show_cover = data["show_cover"]
        into.cover_options = {
            ContactSheetCoverOptions(opt) for opt in data.get("cover_options") or ()
        }
        into.cover_description = data["cover_description"]
        return into

    def to_dict(self) -> models.ContactSheet:
        cs = models.ContactSheet(
            name=self.name,
            orientation=self.orientation.value,
            page_size=models.PageSize(
                width=self.width,
                height=self.height,
            ),
            style=self.style.value,
            panel_options=[opt.value for opt in self.panel_options],
            show_header=self.show_header,
            show_comments=self.show_comments,
            show_watermark=self.show_watermark,
            show_company=self.show_company,
            show_cover=self.show_cover,
            cover_options=[opt.value for opt in self.cover_options],
            cover_description=self.cover_description,
        )
        if self.contactsheet_id is not None:
            cs["id"] = self.contactsheet_id
        if self.columns is not None:
            cs["columns"] = self.columns
        if self.rows is not None:
            cs["rows"] = self.rows
        return cs


class ShowState(enum.Enum):
    ACTIVE = "active"
    ARCHIVING = "archiving"
    ARCHIVED = "archived"
    RESTORING = "restoring"
    ARCHIVE_ERRORED = "archive_errored"
    RESTORE_ERRORED = "restore_errored"


class Show(FlixType):
    def __init__(
        self,
        tracking_code: str = "",
        aspect_ratio: float = 1.77,
        frame_rate: float = 24,
        title: str = "",
        description: str = "",
        episodic: bool = False,
        groups: list[Group] | None = None,
        show_thumbnail_id: int | None = None,
        hidden: bool = False,
        *,
        show_id: int | None = None,
        owner: User | None = None,
        created_date: datetime.datetime | None = None,
        state: ShowState = ShowState.ACTIVE,
        metadata: Mapping[str, Any] | None = None,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self.show_id = show_id
        self.tracking_code = tracking_code
        self.aspect_ratio = aspect_ratio
        self.frame_rate = frame_rate
        self.title = title
        self.description = description
        self.episodic = episodic
        self.groups = groups
        self.show_thumbnail_id = show_thumbnail_id
        self.hidden = hidden
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.state = state
        self.metadata = Metadata(metadata, parent=self, _client=_client)

        self._color_tags: dict[Literal["sequence", "sequencerevision"], dict[str, ColorTag]] = {}

    @classmethod
    def from_dict(
        cls: type[Show],
        data: models.Show,
        *,
        into: Show | None = None,
        _client: client.Client | None,
    ) -> Show:
        if into is None:
            into = cls(_client=_client)
        into.show_id = data["id"]
        into.tracking_code = data.get("tracking_code") or ""
        into.aspect_ratio = data["aspect_ratio"]
        into.frame_rate = data["frame_rate"]
        into.title = data.get("title") or ""
        into.description = data.get("description") or ""
        into.groups = [Group.from_dict(group) for group in data.get("groups") or []]
        into.episodic = data.get("episodic", False)
        into.show_thumbnail_id = data.get("show_thumbnail_id")
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        into.hidden = data.get("hidden", False)
        into.state = ShowState(data["state"])
        return into

    def to_dict(self) -> models.Show:
        show = models.Show(
            tracking_code=self.tracking_code,
            aspect_ratio=self.aspect_ratio,
            description=self.description,
            title=self.title,
            episodic=self.episodic,
            frame_rate=self.frame_rate,
            hidden=self.hidden,
            metadata=self.metadata.to_dict(),
        )
        if self.show_id is not None:
            show["id"] = self.show_id
        if self.show_thumbnail_id is not None:
            show["show_thumbnail_id"] = self.show_thumbnail_id
        if self.groups is not None:
            show["groups"] = [group.to_dict() for group in self.groups]
        return show

    def path_prefix(self) -> str:
        return f"/show/{self.show_id}"

    def hide(self) -> None:
        self.hidden = True

    async def get_sequence(self, sequence_id: int) -> Sequence:
        path = f"{self.path_prefix()}/sequence/{sequence_id}"
        sequence = cast(models.Sequence, await self.client.get(path))
        return Sequence.from_dict(sequence, _show=self, _episode=None, _client=self.client)

    async def get_all_sequences(
        self, include_hidden: bool = False, page: int | None = None, per_page: int | None = None
    ) -> list[Sequence]:
        class _AllSequences(TypedDict):
            sequences: list[models.Sequence]

        path = f"{self.path_prefix()}/sequences"
        params = _params(
            display_hidden="true" if include_hidden else None,
            page=page,
            per_page=per_page,
        )
        all_sequences = cast(_AllSequences, await self.client.get(path, params=params))
        return [
            Sequence.from_dict(sequence, _show=self, _episode=None, _client=self.client)
            for sequence in all_sequences["sequences"]
        ]

    async def get_episode(self, episode_id: int) -> Episode:
        path = f"{self.path_prefix()}/episode/{episode_id}"
        episode = cast(models.Episode, await self.client.get(path))
        return Episode.from_dict(episode, _show=self, _client=self.client)

    async def get_all_episodes(self) -> list[Episode]:
        class _AllEpisodes(TypedDict):
            episodes: list[models.Episode]

        path = f"{self.path_prefix()}/episodes"
        all_episodes = cast(_AllEpisodes, await self.client.get(path))
        return [
            Episode.from_dict(episode, _show=self, _client=self.client)
            for episode in all_episodes["episodes"]
        ]

    async def get_assigned_contactsheets(self) -> list[ContactSheet]:
        class _AllContactSheets(TypedDict):
            contact_sheets: list[models.ContactSheet]

        path = f"{self.path_prefix()}/contactsheets"
        all_contactsheets = cast(_AllContactSheets, await self.client.get(path))
        return [
            ContactSheet.from_dict(cs, _client=self.client)
            for cs in all_contactsheets["contact_sheets"]
        ]

    async def get_all_color_tags(
        self, model: Literal["sequence", "sequencerevision"]
    ) -> dict[str, ColorTag]:
        """Get all color tags assignable to the given type in this show.

        Returns:
            A mapping from color tag name to color tag.
        """
        if cached_tags := self._color_tags.get(model):
            return cached_tags

        class _AllColorTags(TypedDict):
            colour_tags: list[models.ColorTag]

        path = f"{self.path_prefix()}/colourtags/{model}"
        all_tags = cast(_AllColorTags, await self.client.get(path))
        tag_by_name = {
            tag["colour_name"]: ColorTag.from_dict(tag) for tag in all_tags["colour_tags"]
        }

        self._color_tags[model] = tag_by_name
        return tag_by_name

    async def get_color_tag(
        self, model: Literal["sequence", "sequencerevision"], name: str
    ) -> ColorTag:
        """Get the color tag with the given name.

        Raises:
            errors.FlixError: If the given name is not a valid color tag name
                for the specified type.
        """
        color_tags = await self.get_all_color_tags(model)
        if tag := color_tags.get(name):
            return tag
        else:
            raise errors.FlixError(
                "'{}' is not a valid color tag name; available names: {}".format(
                    name,
                    ", ".join(color_tags),
                )
            )

    async def create_assets(self, num_assets: int) -> list[Asset]:
        class _Assets(TypedDict):
            assets: list[models.Asset]

        path = f"{self.path_prefix()}/asset"
        body = {"asset_count": num_assets}
        assets = cast(_Assets, await self.client.post(path, body=body))
        return [Asset.from_dict(asset, _client=self.client) for asset in assets["assets"]]

    async def create_media_objects(self, assets: list[Asset], ref: str) -> list[MediaObject]:
        class _MediaObjects(TypedDict):
            media_objects: list[models.MediaObject]

        path = f"{self.path_prefix()}/media_object/{ref}"
        body = {"asset_ids": [asset.asset_id for asset in assets]}
        mos = cast(_MediaObjects, await self.client.post(path, body=body))
        media_objects = [
            MediaObject.from_dict(mo, _client=self.client) for mo in mos["media_objects"]
        ]

        asset_by_id: dict[int, Asset] = {asset.asset_id: asset for asset in assets}
        for mo in media_objects:
            if asset := asset_by_id.get(mo.asset_id):
                asset.media_objects.setdefault(ref, []).append(mo)

        return media_objects

    async def transcode_assets(self, assets: list[Asset]) -> list[str]:
        """Transcodes an asset with an 'artwork' media object.

        This will create thumbnail, scaled and fullres images for the asset.

        Args:
            assets: The list of assets which need to be transcoded.

        Returns:
            The list of task IDs which have been created to perform the transcode jobs.
        """

        class _Tasks(TypedDict):
            task_ids: list[str]

        path = f"{self.path_prefix()}/asset/transcode"
        body = {"asset_ids": [a.asset_id for a in assets]}
        task_ids = cast(_Tasks, await self.client.post(path, body))
        return task_ids["task_ids"]

    async def upload_file(
        self, f: BinaryIO, ref: str, *, name: str | None = None, size: int | None = None
    ) -> Asset:
        """Upload a new file to this show.

        This will create a new asset and a new media object with the given asset type.

        Example:
            ```python
            with open("artwork.psd", "rb") as f:
                await show.upload_file(f, "artwork")
            ```

        Args:
            f: The file to upload.
            ref: The [asset type][flix.MediaObject.asset_type] of the media object to create,
                e.g. ``"artwork"`` or ``"show-thumbnail"``.
            name: The name of the file. If not provided, the name will be fetched
                from the file handle. Useful when uploading a file handle that
                doesn't correspond to a physical file on disk.
            size: The total size of the file. If not provided, the size will be
                automatically detected from the file handle.

        Returns:
            The new asset populated with the new media object.
        """
        asset, mo = await self._create_singleton_asset(ref)
        await mo.upload(f, name=name, size=size)
        return asset

    async def upload_stream(
        self, stream: AsyncIterable[bytes], ref: str, *, name: str, size: int
    ) -> Asset:
        """Upload a data stream as a new file to this show.

        This will create a new asset and a new media object with the given asset type.

        Args:
            stream: The data stream to upload.
            ref: The [asset type][flix.MediaObject.asset_type] of the media object to create,
                e.g. ``"artwork"`` or ``"show-thumbnail"``.
            name: The name of the file.
            size: The total size of the file.

        Returns:
            The new asset populated with the new media object.
        """
        asset, mo = await self._create_singleton_asset(ref)
        await mo.upload_stream(stream, name=name, size=size)
        return asset

    async def _create_singleton_asset(self, ref: str) -> tuple[Asset, MediaObject]:
        """Create a new asset with a single media object."""
        asset = (await self.create_assets(1))[0]
        mo = await asset.create_media_object(ref)
        return asset, mo

    def new_episode(
        self,
        episode_number: int,
        tracking_code: str,
        title: str = "",
        description: str = "",
    ) -> Episode:
        if not self.episodic:
            raise errors.FlixError("cannot create an episode in a non-episodic show")
        return Episode(
            episode_number=episode_number,
            tracking_code=tracking_code,
            title=title or tracking_code,
            description=description,
            _show=self,
            _client=self.client,
        )

    def new_sequence(self, tracking_code: str, description: str = "") -> Sequence:
        return Sequence(
            tracking_code=tracking_code,
            description=description or tracking_code,
            _show=self,
            _episode=None,
            _client=self.client,
        )

    async def export_yaml(
        self,
        anonymize_strings: bool = False,
        include_assets: bool = False,
        sequences: list[Sequence] | None = None,
    ) -> MediaObject:
        path = f"{self.path_prefix()}/export/yaml"
        params: dict[str, Any] = {
            "anonymize_strings": anonymize_strings,
            "include_assets": include_assets,
        }
        if sequences is not None:
            params["sequence_ids"] = [seq.sequence_id for seq in sequences]

        async with self.client.websocket() as ws:
            await self.client.post(path, body=params, headers={"Flix-Client-Id": ws.client_id})
            complete_msg: websocket.MessageStateYAMLCreated = await ws.wait_on_chain(
                websocket.MessageStateYAMLCreated
            )

        asset = await complete_msg.get_asset()
        return asset.media_objects["state_yaml"][0]

    async def create_archive(self, skip_transcoded_files: bool = False) -> str:
        """Create an archive of this show.

        Args:
            skip_transcoded_files: If True, files generated by transcoding, such as thumbnails
            or scaled images, will not be included in the archive.

        Returns:
            The path to the archive on the Flix Server.
        """
        path = f"{self.path_prefix()}/archive"
        params: dict[str, Any] = {}
        if skip_transcoded_files:
            params["skip_transcoded_files"] = True

        async with self.client.websocket() as ws:
            await self.client.post(path, body=params, headers={"Flix-Client-Id": ws.client_id})
            complete_msg: websocket.MessageArchiveCreated = await ws.wait_on_chain(
                websocket.MessageArchiveCreated
            )

        return complete_msg.archive_path

    async def save(self, force_create_new: bool = False) -> None:
        """Save this show.

        Args:
            force_create_new: Always create a new show instead of updating an existing one.
        """
        if self.show_id is None or force_create_new:
            path = "/show"
            result = cast(models.Show, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.Show, await self.client.patch(path, body=self.to_dict()))
        self.from_dict(result, into=self, _client=self.client)

    async def update(self) -> None:
        """Re-fetch this show from the server and update it in-place."""
        path = f"/show/{self.show_id}"
        result = cast(models.Show, await self.client.get(path))
        self.from_dict(result, into=self, _client=self.client)


@dataclasses.dataclass
class Keyframe:
    @dataclasses.dataclass
    class Viewport:
        width: int
        height: int
        offset_x: float
        offset_y: float
        scale: float

    start_key: int
    scale: float = 100
    rotation: float = 0
    center_horiz: float = 0
    center_vert: float = 0
    anchor_point_horiz: float = 0
    anchor_point_vert: float = 0
    viewport: Viewport | None = None
    show_id: int | None = None
    sequence_id: int | None = None
    panel_id: int | None = None
    panel_revision: int | None = None

    @staticmethod
    def from_dict(data: models.Keyframe) -> Keyframe:
        return Keyframe(
            show_id=data["show_id"],
            sequence_id=data["sequence_id"],
            panel_id=data["panel_id"],
            panel_revision=data["panel_revision"],
            start_key=data["start_key"],
            scale=data.get("scale", 0),
            rotation=data.get("rotation", 0),
            center_horiz=data.get("center_horiz", 0),
            center_vert=data.get("center_vert", 0),
            anchor_point_horiz=data.get("anchor_point_horiz", 0),
            anchor_point_vert=data.get("anchor_point_vert", 0),
            viewport=(
                Keyframe.Viewport(
                    width=data["viewport"]["width"],
                    height=data["viewport"]["height"],
                    offset_x=data["viewport"].get("offset_x", 0),
                    offset_y=data["viewport"].get("offset_y", 0),
                    scale=data["viewport"].get("scale", 1),
                )
                if data.get("viewport")
                else None
            ),
        )

    def to_dict(self) -> models.Keyframe:
        kf = models.Keyframe(
            start_key=self.start_key,
            scale=self.scale,
            rotation=self.rotation,
            center_horiz=self.center_horiz,
            center_vert=self.center_vert,
            anchor_point_horiz=self.anchor_point_horiz,
            anchor_point_vert=self.anchor_point_vert,
        )
        if self.viewport is not None:
            kf["viewport"] = models.Viewport(
                width=self.viewport.width,
                height=self.viewport.height,
                offset_x=self.viewport.offset_x,
                offset_y=self.viewport.offset_y,
                scale=self.viewport.scale,
            )
        if self.show_id is not None:
            kf["show_id"] = self.show_id
        if self.sequence_id is not None:
            kf["sequence_id"] = self.sequence_id
        if self.panel_id is not None:
            kf["panel_id"] = self.panel_id
        if self.panel_revision is not None:
            kf["panel_revision"] = self.panel_revision
        return kf


@dataclasses.dataclass
class PanelComment:
    body: str
    panel_id: int
    revision_id: int
    closer_user_id: int | None = None
    closed_date: datetime.datetime | None = None
    created_date: datetime.datetime | None = None
    comment_id: int | None = None
    deleted: bool = False
    closed: bool = False
    owner: User | None = None

    @staticmethod
    def from_dict(data: models.PanelComment, *, _client: client.Client | None) -> PanelComment:
        return PanelComment(
            comment_id=data["id"],
            body=data.get("body", ""),
            panel_id=data["panel_id"],
            revision_id=data["revision_id"],
            closer_user_id=data.get("closer_user_id"),
            closed_date=(
                dateutil.parser.parse(data["closed_date"]) if data.get("closed_date") else None
            ),
            created_date=dateutil.parser.parse(data["created_date"]),
            deleted=data.get("deleted", False),
            closed=data.get("closed", False),
            owner=User.from_dict(data["owner"], _client=_client) if data.get("owner") else None,
        )


@dataclasses.dataclass
class OriginSBP:
    project_path: str
    sbp_id: str
    mastercomment2: str
    layer_transform_hash: str | None

    @staticmethod
    def from_dict(data: models.OriginSBP) -> OriginSBP:
        return OriginSBP(
            project_path=data.get("project_path", ""),
            sbp_id=data.get("sbp_id", ""),
            mastercomment2=data.get("mastercomment2", ""),
            layer_transform_hash=data.get("layer_transform_hash"),
        )

    def to_dict(self) -> models.OriginSBP:
        return models.OriginSBP(
            project_path=self.project_path,
            sbp_id=self.sbp_id,
            mastercomment2=self.mastercomment2,
            layer_transform_hash=self.layer_transform_hash,
        )


@dataclasses.dataclass
class OriginAvid:
    effects_hash: str | None

    @staticmethod
    def from_dict(data: models.OriginAvid) -> OriginAvid:
        return OriginAvid(
            effects_hash=data.get("effects_hash") or None,
        )

    def to_dict(self) -> models.OriginAvid:
        return models.OriginAvid(
            effects_hash=self.effects_hash or "",
        )


@dataclasses.dataclass
class OriginFCPXML:
    effect_hash: str | None
    editorial_id: str | None

    @staticmethod
    def from_dict(data: models.OriginFCPXML) -> OriginFCPXML:
        return OriginFCPXML(
            effect_hash=data.get("effect_hash"),
            editorial_id=data.get("editorial_id"),
        )

    def to_dict(self) -> models.OriginFCPXML:
        origin = models.OriginFCPXML()
        if self.effect_hash:
            origin["effect_hash"] = self.effect_hash
        if self.editorial_id:
            origin["editorial_id"] = self.editorial_id
        return origin


@dataclasses.dataclass
class DuplicateRef:
    panel_id: int
    panel_revision: int
    sequence_id: int

    @staticmethod
    def from_dict(data: models.DuplicateRef) -> DuplicateRef:
        return DuplicateRef(
            panel_id=data["panel_id"],
            panel_revision=data["panel_revision"],
            sequence_id=data["sequence_id"],
        )

    def to_dict(self) -> models.DuplicateRef:
        return models.DuplicateRef(
            panel_id=self.panel_id,
            panel_revision=self.panel_revision,
            sequence_id=self.sequence_id,
        )


class Panel(FlixType):
    def __init__(
        self,
        *,
        panel_id: int | None = None,
        sequence_id: int | None = None,
        show_id: int | None = None,
        revision_count: int = 0,
        owner: User | None = None,
        created_date: datetime.datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self.panel_id = panel_id
        self.sequence_id = sequence_id
        self.show_id = show_id
        self.revision_count = revision_count
        self.owner = owner
        self.created_date = created_date or datetime.datetime.now(datetime.timezone.utc)
        self.metadata = Metadata(metadata, parent=self, _client=_client)
        self._sequence = _sequence

    @classmethod
    def from_dict(
        cls,
        data: models.Panel,
        *,
        into: Panel | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> Panel:
        if into is None:
            into = cls(_sequence=_sequence, _client=_client)
        into.panel_id = data["id"]
        into.sequence_id = data["sequence_id"]
        into.show_id = data["show_id"]
        into.revision_count = data["revision_count"]
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        return into

    def to_dict(self) -> models.Panel:
        panel = models.Panel(metadata=self.metadata.to_dict())
        if self.panel_id is not None:
            panel["id"] = self.panel_id
        if self.sequence_id is not None:
            panel["sequence_id"] = self.sequence_id
        if self.show_id is not None:
            panel["show_id"] = self.show_id
        return panel

    def path_prefix(self) -> str:
        return f"{self._sequence.path_prefix(include_episode=False)}/panel/{self.panel_id}"


class PanelRevision(FlixType):
    def __init__(
        self,
        origin: str = "Manual Import",
        asset: Asset | None = None,
        is_ref: bool = False,
        keyframes: list[Keyframe] | None = None,
        related_panels: list[PanelRevision] | None = None,
        *,
        panel_id: int | None = None,
        revision_number: int | None = None,
        sequence_id: int | None = None,
        show_id: int | None = None,
        revision_counter: int = 0,
        created_date: datetime.datetime | None = None,
        modified_date: datetime.datetime | None = None,
        owner: User | None = None,
        published: int | None = None,
        latest_open_comment: PanelComment | None = None,
        origin_sbp: OriginSBP | None = None,
        origin_avid: OriginAvid | None = None,
        origin_fcpxml: OriginFCPXML | None = None,
        layer_transform: bool = False,
        duplicate: DuplicateRef | None = None,
        panel: Panel | None = None,
        metadata: Mapping[str, Any] | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._sequence = _sequence
        self.sequence_id = sequence_id
        self.show_id = show_id
        self.panel_id = panel_id
        self.revision_number = revision_number
        self.origin = origin
        self.asset = asset
        self.is_ref = is_ref
        self.keyframes = keyframes or []
        self.related_panels = related_panels or []
        self.revision_counter = revision_counter
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.modified_date: datetime.datetime = modified_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.owner = owner
        self.published = published
        self.latest_open_comment = latest_open_comment
        self.origin_sbp = origin_sbp
        self.origin_avid = origin_avid
        self.origin_fcpxml = origin_fcpxml
        self.layer_transform = layer_transform
        self.duplicate = duplicate
        self.panel = panel
        self.metadata = Metadata(metadata, parent=self, _client=_client)

    @classmethod
    def from_dict(
        cls: type[PanelRevision],
        data: models.PanelRevision,
        *,
        into: PanelRevision | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> PanelRevision:
        if into is None:
            into = cls(_sequence=_sequence, _client=_client)
        into.sequence_id = data["sequence_id"]
        into.show_id = data["show_id"]
        into.panel_id = data["panel_id"]
        into.revision_number = data["revision_number"]
        into.origin = data.get("origin", "")
        into.asset = Asset.from_dict(data["asset"], _client=_client) if data.get("asset") else None
        into.is_ref = data.get("is_ref", False)
        into.keyframes = [Keyframe.from_dict(keyframe) for keyframe in data.get("keyframes") or []]
        into.related_panels = [
            PanelRevision.from_dict(panel, _sequence=_sequence, _client=_client)
            for panel in data.get("related_panels") or []
        ]
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.published = data.get("published", None)
        into.latest_open_comment = (
            PanelComment.from_dict(data["latest_open_comment"], _client=_client)
            if data.get("latest_open_comment")
            else None
        )
        into.origin_sbp = (
            OriginSBP.from_dict(data["origin_sbp"]) if data.get("origin_sbp") else None
        )
        into.origin_avid = (
            OriginAvid.from_dict(data["origin_avid"]) if data.get("origin_avid") else None
        )
        into.origin_fcpxml = (
            OriginFCPXML.from_dict(data["origin_fcpxml"]) if data.get("origin_fcpxml") else None
        )
        into.layer_transform = data.get("layer_transform", False)
        into.duplicate = (
            DuplicateRef.from_dict(data["duplicate"]) if data.get("duplicate") else None
        )
        into.panel = (
            Panel.from_dict(data["panel"], _sequence=_sequence, _client=_client)
            if data.get("panel")
            else None
        )
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        return into

    def to_dict(self) -> models.PanelRevision:
        pr = models.PanelRevision(
            origin=self.origin,
            is_ref=self.is_ref,
            keyframes=[keyframe.to_dict() for keyframe in self.keyframes],
            related_panels=[panel.to_dict() for panel in self.related_panels],
            published=self.published,
            metadata=self.metadata.to_dict(),
        )
        if self.asset is not None:
            pr["asset"] = self.asset.to_dict()
        if self.origin_sbp is not None:
            pr["origin_sbp"] = self.origin_sbp.to_dict()
        if self.origin_avid is not None:
            pr["origin_avid"] = self.origin_avid.to_dict()
        if self.duplicate is not None:
            pr["duplicate"] = self.duplicate.to_dict()
        if self.panel_id is not None:
            pr["panel_id"] = self.panel_id
        if self.revision_number is not None:
            pr["revision_number"] = self.revision_number
        if self.sequence_id is not None:
            pr["sequence_id"] = self.sequence_id
        if self.show_id is not None:
            pr["show_id"] = self.show_id
        return pr

    @property
    def sequence(self) -> Sequence:
        return self._sequence

    @property
    def show(self) -> Show:
        return self.sequence.show

    def path_prefix(self, include_episode: bool = False) -> str:
        prefix = self._sequence.path_prefix(include_episode=include_episode)
        return f"{prefix}/panel/{self.panel_id}/revision/{self.revision_number}"

    def new_sequence_panel(
        self,
        duration: int = 12,
        trim_in_frame: int | None = None,
        trim_out_frame: int | None = None,
        dialogue: Dialogue | None = None,
        hidden: bool = False,
        sequence_revision: int | None = None,
    ) -> SequencePanel:
        return SequencePanel(
            panel=self,
            duration=duration,
            trim_in_frame=trim_in_frame or 0,
            trim_out_frame=trim_out_frame or 0,
            dialogue=dialogue,
            hidden=hidden,
            sequence_revision=sequence_revision,
        )

    def new_keyframe(
        self,
        start_key: int,
        scale: float = 100,
        rotation: float = 0,
        center_horiz: float = 0,
        center_vert: float = 0,
        anchor_point_horiz: float = 0,
        anchor_point_vert: float = 0,
        viewport: Keyframe.Viewport | None = None,
    ) -> Keyframe:
        kf = Keyframe(
            start_key=start_key,
            scale=scale,
            rotation=rotation,
            center_horiz=center_horiz,
            center_vert=center_vert,
            anchor_point_horiz=anchor_point_horiz,
            anchor_point_vert=anchor_point_vert,
            viewport=viewport,
        )
        self.keyframes.append(kf)
        return kf

    async def get_dialogue_history(self) -> list[Dialogue]:
        """Get all dialogue entries associated with the panel ID of this panel revision."""

        class _AllDialogue(TypedDict):
            dialogues: list[models.Dialogue]

        path = f"{self._sequence.path_prefix()}/panel/{self.panel_id}/dialogues"
        result = cast(_AllDialogue, await self.client.get(path))
        return [
            Dialogue.from_dict(d, _show=self.show, _client=self.client) for d in result["dialogues"]
        ]

    async def save(self, force_create_new_panel: bool = False) -> None:
        """Save this panel revision.

        Args:
            force_create_new_panel: Always create a new panel ID for this panel revision
                instead of versioning up an existing panel.
        """
        if self.panel_id is None or force_create_new_panel:
            path = f"{self._sequence.path_prefix()}/panel"
            result = cast(models.PanelRevision, await self.client.post(path, body=self.to_dict()))
        else:
            path = f"{self._sequence.path_prefix()}/panel/{self.panel_id}/revision"
            result = cast(models.PanelRevision, await self.client.post(path, body=self.to_dict()))
        self.from_dict(result, into=self, _sequence=self._sequence, _client=self.client)


class Dialogue(FlixType):
    def __init__(
        self,
        text: str,
        *,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        dialogue_id: int | None = None,
        _show: Show,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._show = _show
        self.dialogue_id = dialogue_id
        self._text = text
        self.created_date = created_date or datetime.datetime.now(datetime.timezone.utc)
        self.owner = owner

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        # clear dialogue id when updating text to avoid user error
        # if changing dialogue of existing object
        self.dialogue_id = None

    @classmethod
    def from_dict(
        cls,
        data: models.Dialogue,
        *,
        into: Dialogue | None = None,
        _show: Show,
        _client: client.Client | None,
    ) -> Dialogue:
        if into is None:
            into = cls(text="", _client=_client, _show=_show)
        # set text first since it also clears dialogue id
        into.text = data["text"]
        into.dialogue_id = data["dialogue_id"]
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client)
        return into

    def to_dict(self) -> models.Dialogue:
        dialogue = models.Dialogue(text=self.text)
        if self.dialogue_id is not None:
            dialogue["dialogue_id"] = self.dialogue_id
        return dialogue

    async def save(self) -> None:
        """Save this dialogue entry.

        Always creates a new dialogue entry. Called automatically for any unsaved dialogue
        when saving a sequence revision.
        """
        path = f"{self._show.path_prefix()}/dialogue"
        result = cast(models.Dialogue, await self.client.post(path, body=self.to_dict()))
        self.from_dict(result, into=self, _client=self.client, _show=self._show)


@dataclasses.dataclass
class SequencePanel:
    panel: PanelRevision
    duration: int
    trim_in_frame: int
    trim_out_frame: int
    dialogue: Dialogue | None = None
    hidden: bool = False
    sequence_revision: int | None = None

    @property
    def dialogue_text(self) -> str:
        """The dialogue for this sequence panel as a string.

        Safe to read and write even if ``dialogue`` is ``None``.
        If set to the empty string, the dialogue will be removed.
        """
        if self.dialogue is not None:
            return self.dialogue.text
        else:
            return ""

    @dialogue_text.setter
    def dialogue_text(self, value: str) -> None:
        if value:
            self.dialogue = Dialogue(text=value, _show=self.panel.show, _client=self.panel.client)
        else:
            self.dialogue = None

    @classmethod
    def from_dict(
        cls,
        data: models.SequencePanel,
        *,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> SequencePanel:
        return cls(
            panel=PanelRevision.from_dict(data, _sequence=_sequence, _client=_client),
            sequence_revision=data["sequence_revision"],
            duration=data["duration"],
            trim_in_frame=data.get("trim_in_frame") or 0,
            trim_out_frame=data.get("trim_out_frame") or 0,
            dialogue=(
                Dialogue.from_dict(d, _show=_sequence.show, _client=_client)
                if (d := data.get("dialogue"))
                else None
            ),
            hidden=data["hidden"],
        )

    def to_dict(self) -> models.SequencePanel:
        pr = models.SequencePanel(
            duration=self.duration,
            trim_in_frame=self.trim_in_frame,
            trim_out_frame=self.trim_out_frame,
            hidden=self.hidden,
        )
        if self.panel.panel_id is not None:
            pr["panel_id"] = self.panel.panel_id
        if self.panel.revision_number is not None:
            pr["revision_number"] = self.panel.revision_number
        if self.dialogue:
            pr["dialogue"] = self.dialogue.to_dict()
        return pr


class DialogueFormat(enum.Enum):
    SRT = "srt"
    AVID = "avid"


class SequenceRevision(FlixType):
    def __init__(
        self,
        panels: list[SequencePanel] | None = None,
        comment: str = "",
        hidden: bool = False,
        color_tag: ColorTag | None = None,
        autosave: bool = False,
        *,
        sequence_id: int | None = None,
        episode_id: int | None = None,
        show_id: int | None = None,
        revision_number: int | None = None,
        owner: User | None = None,
        created_date: datetime.datetime | None = None,
        published: bool = False,
        imported: bool = False,
        task_id: str | None = None,
        source_files: list[Asset] | None = None,
        metadata: Mapping[str, Any] | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> None:
        super().__init__(_client)
        self._sequence = _sequence
        self.sequence_id = sequence_id
        self.episode_id = episode_id
        self.show_id = show_id
        self.revision_number = revision_number
        self.panels = panels or []
        self.comment = comment
        self.hidden = hidden
        self.color_tag = color_tag
        self.autosave = autosave
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.now(
            datetime.timezone.utc
        )
        self.published = published
        self.imported = imported
        self.task_id = task_id
        self.source_files = source_files or []
        self.metadata = Metadata(metadata, parent=self, _client=_client)

    @classmethod
    def from_dict(
        cls,
        data: models.SequenceRevision,
        *,
        into: SequenceRevision | None = None,
        _sequence: Sequence,
        _client: client.Client | None,
    ) -> SequenceRevision:
        if into is None:
            into = cls(_sequence=_sequence, _client=_client)
        into.revision_number = data["revision"]
        into.sequence_id = data["sequence_id"]
        into.episode_id = data.get("episode_id", 0)
        into.show_id = data["show_id"]
        into.comment = data.get("comment", "")
        into.hidden = data["hidden"]
        into.color_tag = ColorTag.from_dict(c) if (c := data.get("colour_tag")) else None
        into.autosave = data["autosave"]
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.published = data.get("published", False)
        into.imported = data.get("imported", False)
        into.task_id = data.get("task_id")
        into.source_files = [
            Asset.from_dict(asset, _client=_client) for asset in data.get("source_files") or []
        ]
        into.metadata = Metadata.from_dict(data.get("metadata"), parent=into, _client=_client)
        return into

    def to_dict(self) -> models.SequenceRevision:
        revision = models.SequenceRevision(
            comment=self.comment,
            revisioned_panels=[panel.to_dict() for panel in self.panels],
            source_files=[asset.to_dict() for asset in self.source_files],
            hidden=self.hidden,
            autosave=self.autosave,
            colour_tag=self.color_tag.to_dict() if self.color_tag else None,
            metadata=self.metadata.to_dict(),
        )
        if self.show_id is not None:
            revision["show_id"] = self.show_id
        if self.episode_id is not None:
            revision["episode_id"] = self.episode_id
        if self.sequence_id is not None:
            revision["sequence_id"] = self.sequence_id
        if self.revision_number is not None:
            revision["revision"] = self.revision_number
        return revision

    def path_prefix(self, include_episode: bool = True) -> str:
        return f"{self._sequence.path_prefix(include_episode)}/revision/{self.revision_number}"

    @property
    def sequence(self) -> Sequence:
        return self._sequence

    @property
    def show(self) -> Show:
        return self.sequence.show

    @property
    def color_tag_name(self) -> str:
        """The name of the current color tag for this sequence.

        This property allows for getting and setting color tags by name.
        If a color tag is set by name, the corresponding ID will be looked up
        when saving the sequence. Setting an invalid name will cause an error on save.
        """
        if self.color_tag is not None:
            return self.color_tag.color_name
        else:
            return ""

    @color_tag_name.setter
    def color_tag_name(self, value: str) -> None:
        if value != "":
            self.color_tag = ColorTag(color_name=value)
        else:
            self.color_tag = None

    def add_panel(
        self,
        panel: PanelRevision,
        duration: int = 12,
        trim_in_frame: int | None = None,
        trim_out_frame: int | None = None,
    ) -> None:
        self.add_sequence_panel(
            panel.new_sequence_panel(
                duration=duration,
                trim_in_frame=trim_in_frame,
                trim_out_frame=trim_out_frame,
                sequence_revision=self.revision_number,
            )
        )

    def add_sequence_panel(self, sequence_panel: SequencePanel) -> None:
        self.panels.append(sequence_panel)

    async def get_all_panel_revisions(self) -> list[SequencePanel]:
        """Fetch all panels belonging to this sequence revision.

        This method also populates [panels][flix.SequenceRevision.panels]
        with the returned panels.
        """

        class _AllPanels(TypedDict):
            panels: list[models.SequencePanel]

        path = f"{self.path_prefix()}/panels"
        all_panels = cast(_AllPanels, await self.client.get(path))
        self.panels = [
            SequencePanel.from_dict(panel, _sequence=self._sequence, _client=self.client)
            for panel in all_panels["panels"]
        ]
        return self.panels

    async def _export(
        self,
        msg_type: type[websocket.AssetCreatedMessageType],
        asset_ref: str,
        path: str,
        params: dict[str, Any],
        panels: list[PanelRevision] | None = None,
    ) -> MediaObject:
        if panels is not None:
            params["panel_revisions"] = [panel.to_dict() for panel in panels]

        async with self.client.websocket() as ws:
            await self.client.post(path, body=params, headers={"Flix-Client-Id": ws.client_id})
            complete_msg = await ws.wait_on_chain(msg_type)

        asset = await complete_msg.get_asset()
        return asset.media_objects[asset_ref][0]

    async def export_quicktime(
        self, include_dialogue: bool = False, panels: list[PanelRevision] | None = None
    ) -> MediaObject:
        path = f"{self.path_prefix()}/export/quicktime"
        params: dict[str, Any] = {"include_dialogue": include_dialogue}
        return await self._export(
            websocket.MessageQuicktimeCreated, "artwork", path, params, panels
        )

    async def export_dialogue(
        self,
        file_format: DialogueFormat,
        clip_name: str = "",
        panels: list[PanelRevision] | None = None,
    ) -> MediaObject:
        path = f"{self.path_prefix()}/export/dialogue"
        params: dict[str, Any] = {
            "format": file_format.value,
            "clip_name": clip_name,
        }
        return await self._export(
            websocket.MessageDialogueComplete, "dialogue", path, params, panels
        )

    async def export_contactsheet(
        self, template: ContactSheet, panels: list[PanelRevision] | None = None
    ) -> MediaObject:
        path = f"{self.path_prefix()}/export/contactsheet"
        params: dict[str, Any] = {
            "contactsheet_id": template.contactsheet_id,
        }
        return await self._export(
            websocket.MessageContactSheetCreated, "contactsheet", path, params, panels
        )

    async def save(self, force_create_new: bool = False) -> None:
        """Save this sequence revision.

        Any unsaved dialogue will be saved automatically.

        Args:
            force_create_new: Always create a new sequence revision instead
                of updating an existing one.
        """
        if self.color_tag is not None and self.color_tag.color_tag_id is None:
            self.color_tag = await self.show.get_color_tag(
                "sequencerevision", self.color_tag.color_name
            )

        if self.revision_number is None or force_create_new:
            # auto-save any unsaved dialogue
            for panel in self.panels:
                if panel.dialogue and not panel.dialogue.dialogue_id:
                    await panel.dialogue.save()

            path = f"{self._sequence.path_prefix()}/revision"
            result = cast(
                models.SequenceRevision, await self.client.post(path, body=self.to_dict())
            )
        else:
            path = self.path_prefix()
            result = cast(
                models.SequenceRevision, await self.client.patch(path, body=self.to_dict())
            )
        self.from_dict(result, into=self, _sequence=self._sequence, _client=self.client)


@dataclasses.dataclass
class Server:
    uuid: str
    region: str
    ip: str
    port: int
    running: bool
    start_date: datetime.datetime
    hostname: str
    db_ident: str
    is_ssl: bool
    transfer_port: int

    @classmethod
    def from_dict(cls, data: models.Server) -> Server:
        return cls(
            uuid=data["id"],
            region=data["region"],
            ip=data["ip"],
            port=data["port"],
            running=data["running"],
            start_date=dateutil.parser.parse(data["start_date"]),
            hostname=data["hostname"],
            db_ident=data["db_ident"],
            is_ssl=data["is_ssl"],
            transfer_port=data["transfer_port"],
        )
