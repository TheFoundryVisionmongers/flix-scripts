import dataclasses
import datetime
import enum
import os
import pathlib
from collections.abc import Mapping
from typing import Any, Type, cast, TypedDict, BinaryIO, Callable

import dateutil.parser

from . import models, client, transfers, websocket

__all__ = [
    "Group",
    "Permission",
    "Role",
    "GroupRolePair",
    "User",
    "MediaObjectStatus",
    "MediaObject",
    "Episode",
    "Sequence",
    "Asset",
    "Show",
    "Keyframe",
    "PanelComment",
    "OriginSBP",
    "OriginAvid",
    "DuplicateRef",
    "PanelRevision",
    "SequenceRevision",
]


def _params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class FlixType:
    def __init__(self, _client: "client.Client | None"):
        self._client = _client

    @property
    def client(self) -> "client.Client":
        if self._client is None:
            raise RuntimeError("client is not set")
        return self._client


@dataclasses.dataclass
class Group:
    title: str
    group_id: int | None = None

    @staticmethod
    def from_dict(data: models.Group) -> "Group":
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
    def from_dict(data: models.Permission) -> "Permission":
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
    def from_dict(data: models.Role) -> "Role":
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
    def from_dict(data: models.GroupRolePair) -> "GroupRolePair":
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
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.groups = groups or []
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.user_type = user_type
        self.is_admin = is_admin
        self.is_system = is_system
        self.is_third_party = is_third_party
        self.deleted = deleted

    @classmethod
    def from_dict(cls, data: models.User, *, into: "User | None" = None, _client: "client.Client | None") -> "User":
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
        return into


class MediaObjectStatus(enum.Enum):
    INITIALIZED = 0
    UPLOADED = 1
    ERRORED = 2


@dataclasses.dataclass
class MediaObject(FlixType):
    def __init__(
        self,
        media_object_id: int = 0,
        asset_id: int = 0,
        filename: str = "",
        content_type: str = "",
        content_length: int = 0,
        content_hash: str = "",
        created_date: datetime.datetime | None = None,
        status: MediaObjectStatus = MediaObjectStatus.INITIALIZED,
        owner: User | None = None,
        asset_type: str = "",
        show_id: int = 0,
        *,
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self.media_object_id = media_object_id
        self.asset_id = asset_id
        self.filename = filename
        self.content_type = content_type
        self.content_length = content_length
        self.content_hash = content_hash
        self.created_date = created_date or datetime.datetime.utcnow()
        self.status = status
        self.owner = owner
        self.asset_type = asset_type
        self.show_id = show_id

    @classmethod
    def from_dict(
        cls, data: models.MediaObject, *, into: "MediaObject | None" = None, _client: "client.Client | None"
    ) -> "MediaObject":
        if into is None:
            into = cls(_client=_client)
        into.media_object_id = data["id"]
        into.asset_id = data["asset_id"]
        into.filename = data.get("name", "")
        into.content_type = data.get("content_type", "")
        into.content_length = data.get("content_length", 0)
        into.content_hash = data.get("content_hash", "")
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.status = MediaObjectStatus(data["status"]) if data.get("status") else MediaObjectStatus.INITIALIZED
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.asset_type = data.get("asset_type", "")
        into.show_id = data.get("show_id", 0)
        into._client = _client
        return into

    async def update(self) -> None:
        path = f"/file/{self.media_object_id}"
        result = cast(models.MediaObject, await self.client.get(path))
        self.from_dict(result, into=self, _client=self.client)

    async def upload(self, f: BinaryIO) -> None:
        await transfers.upload(self.client, f, self.asset_id, self.media_object_id)
        await self.update()

    async def download(self) -> bytes:
        return b"".join([chunk async for chunk in transfers.download(self.client, self.asset_id, self.media_object_id)])

    async def download_to(self, directory: str | os.PathLike[str], filename: str | None = None) -> None:
        dirpath = pathlib.Path(directory)
        dirpath.mkdir(parents=True, exist_ok=True)
        if filename is None:
            path = dirpath / f"{self.media_object_id}_{self.filename}"
        else:
            path = dirpath / filename

        with path.open("wb") as f:
            async for chunk in transfers.download(self.client, self.asset_id, self.media_object_id):
                f.write(chunk)


class Episode(FlixType):
    def __init__(
        self,
        episode_number: int = 0,
        tracking_code: str = "",
        description: str = "",
        title: str = "",
        *,
        episode_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        metadata: dict[str, Any] | None = None,
        _show: "Show",
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self._show = _show
        self.tracking_code = tracking_code
        self.description = description
        self.title = title
        self.episode_id = episode_id
        self.episode_number = episode_number
        self.created_date = created_date
        self.owner = owner
        self.metadata = metadata or {}

    @classmethod
    def from_dict(
        cls, data: models.Episode, *, into: "Episode | None" = None, _show: "Show", _client: "client.Client | None"
    ) -> "Episode":
        if into is None:
            into = cls(_show=_show, _client=_client)
        into.episode_id = data["id"]
        into.episode_number = data.get("episode_number", 0)
        into.tracking_code = data.get("tracking_code", "")
        into.description = data.get("description", "")
        into.title = data.get("title", "")
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client)
        into.metadata = data.get("meta_data") or {}
        return into

    def to_dict(self) -> models.Episode:
        episode = models.Episode(
            episode_number=self.episode_number,
            tracking_code=self.tracking_code,
            description=self.description,
            title=self.title,
            meta_data=self.metadata,
        )
        if self.episode_id is not None:
            episode["id"] = self.episode_id
        return episode

    def path_prefix(self) -> str:
        return f"{self._show.path_prefix()}/episode/{self.episode_id}"

    async def get_all_sequences(
        self, include_hidden: bool = False, page: int | None = None, per_page: int | None = None
    ) -> list["Sequence"]:
        path = f"{self.path_prefix()}/sequences"
        params = _params(
            display_hidden="true" if include_hidden else None,
            page=page,
            per_page=per_page,
        )
        all_sequences_model = TypedDict("all_sequences_model", {"sequences": list[models.Sequence]})
        all_sequences = cast(all_sequences_model, await self.client.get(path, params=params))
        return [
            Sequence.from_dict(sequence, _show=self._show, _episode=self, _client=self.client)
            for sequence in all_sequences["sequences"]
        ]

    async def save(self, force_create_new: bool = False) -> None:
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
        *,
        sequence_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        revision_count: int = 0,
        panel_revision_count: int = 0,
        metadata: dict[str, Any] | None = None,
        _show: "Show",
        _episode: "Episode | None",
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self._show = _show
        self._episode = _episode
        self.sequence_id = sequence_id
        self.tracking_code = tracking_code
        self.description = description
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.owner = owner
        self.revision_count = revision_count
        self.panel_revision_count = panel_revision_count
        self.metadata: dict[str, Any] = metadata or {}
        self.hidden = hidden

    @classmethod
    def from_dict(
        cls,
        data: models.Sequence,
        *,
        into: "Sequence | None" = None,
        _show: "Show",
        _episode: "Episode | None",
        _client: "client.Client | None",
    ) -> "Sequence":
        if into is None:
            into = cls(_show=_show, _episode=_episode, _client=_client)
        into.sequence_id = data["id"]
        into.tracking_code = data.get("tracking_code", "")
        into.description = data.get("description", "")
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.revision_count = data.get("revisions_count", 0)
        into.panel_revision_count = data.get("panel_revision_count", 0)
        into.metadata = data.get("meta_data") or {}
        into.hidden = data.get("hidden", False)
        return into

    def to_dict(self) -> models.Sequence:
        sequence = models.Sequence(
            tracking_code=self.tracking_code,
            description=self.description,
            hidden=self.hidden,
            meta_data=self.metadata,
        )
        if self.sequence_id is not None:
            sequence["id"] = self.sequence_id

        return sequence

    def path_prefix(self, include_episode: bool = True) -> str:
        if self._episode is not None and include_episode:
            return f"{self._episode.path_prefix()}/sequence/{self.sequence_id}"
        else:
            return f"{self._show.path_prefix()}/sequence/{self.sequence_id}"

    def new_sequence_revision(
        self,
        comment: str = "",
        panels: list["SequencePanel"] | None = None,
        source_files: list["Asset"] | None = None,
    ) -> "SequenceRevision":
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
        asset: "Asset | None" = None,
        is_ref: bool = False,
        related_panels: list["PanelRevision"] | None = None,
    ) -> "PanelRevision":
        return PanelRevision(
            origin=origin,
            asset=asset,
            is_ref=is_ref,
            related_panels=related_panels,
            _sequence=self,
            _client=self.client,
        )

    async def save_panels(self, panels: list["PanelRevision"]) -> None:
        path = f"{self.path_prefix(False)}/panels"
        panels_model = TypedDict("panels_model", {"panels": list[models.Panel]})
        result = cast(panels_model, await self.client.post(path, body=[panel.to_dict() for panel in panels]))
        for i, result_panel in enumerate(result["panels"]):
            PanelRevision.from_dict(result_panel["revision"], into=panels[i], _sequence=self, _client=self.client)

    async def get_sequence_revision(self, revision_number: int) -> "SequenceRevision":
        path = f"{self.path_prefix()}/revision/{revision_number}"
        revision = cast(models.SequenceRevision, await self.client.get(path))
        return SequenceRevision.from_dict(revision, _sequence=self, _client=self.client)

    async def get_all_sequence_revisions(self) -> list["SequenceRevision"]:
        path = f"{self.path_prefix()}/revisions"
        all_revisions_model = TypedDict("all_revisions_model", {"sequence_revisions": list[models.SequenceRevision]})
        all_revisions = cast(all_revisions_model, await self.client.get(path))
        return [
            SequenceRevision.from_dict(revision, _sequence=self, _client=self.client)
            for revision in all_revisions["sequence_revisions"]
        ]

    async def get_panel_revision(self, panel_id: int, panel_revision: int) -> "PanelRevision":
        path = f"{self.path_prefix(False)}/panel/{panel_id}/revision/{panel_revision}"
        result = cast(models.PanelRevision, await self.client.get(path))
        return PanelRevision.from_dict(result, _sequence=self, _client=self.client)

    async def get_all_panel_revisions(
        self,
        latest_revision_only: bool = True,
        page: int | None = None,
        per_page: int | None = None,
    ) -> list["PanelRevision"]:
        path = f"{self.path_prefix(False)}/panels"
        params = _params(
            showAll="true" if not latest_revision_only else None,
            page=page,
            per_page=per_page,
        )
        all_panels_model = TypedDict("all_panels_model", {"panels": list[models.PanelRevision]})
        all_panels = cast(all_panels_model, await self.client.get(path, params=params))
        return [PanelRevision.from_dict(panel, _sequence=self, _client=self.client) for panel in all_panels["panels"]]

    async def import_aaf(
        self,
        aaf_asset: "Asset",
        comment: str = "",
        extra_params: Mapping[str, Any] | None = None,
        timeout: float | None = None,
        chain_status_callback: Callable[[websocket.MessageJobChainStatus], None] | None = None,
        panel_status_callback: Callable[[websocket.MessageEditorialImportStatus], None] | None = None,
    ) -> "SequenceRevision":
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
                if isinstance(msg, websocket.MessageJobChainStatus) and chain_status_callback is not None:
                    chain_status_callback(msg)
                elif isinstance(msg, websocket.MessageEditorialImportStatus) and panel_status_callback is not None:
                    panel_status_callback(msg)
            return await waiter.result.get_sequence_revision(self)

    async def save(self, force_create_new: bool = False) -> None:
        if self.sequence_id is None or force_create_new:
            path = f"{self._show.path_prefix()}/sequence"
            result = cast(models.Sequence, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.Sequence, await self.client.patch(path, body=self.to_dict()))
        self.from_dict(result, into=self, _show=self._show, _episode=self._episode, _client=self.client)

    async def delete(self) -> None:
        path = self.path_prefix()
        await self.client.delete(path)


class Asset(FlixType):
    def __init__(
        self,
        *,
        asset_id: int = 0,
        show_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        media_objects: dict[str, list[MediaObject]] | None = None,
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self.asset_id = asset_id
        self.show_id = show_id
        self.created_date = created_date or datetime.datetime.utcnow()
        self.owner = owner
        self.media_objects = media_objects or {}

    @staticmethod
    def from_dict(data: models.Asset, *, _client: "client.Client | None") -> "Asset":
        return Asset(
            asset_id=data["asset_id"],
            show_id=data["show_id"],
            created_date=dateutil.parser.parse(data["created_date"]),
            owner=User.from_dict(data["owner_id"], _client=_client) if data.get("owner_id") else None,
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
        path = f"/show/{self.show_id}/media_object/{ref}"
        body = {"asset_ids": [self.asset_id]}
        mos_model = TypedDict("mos_model", {"media_objects": list[models.MediaObject]})
        mos = cast(mos_model, await self.client.post(path, body=body))
        media_object = MediaObject.from_dict(mos["media_objects"][0], _client=self.client)
        self.media_objects.setdefault(ref, []).append(media_object)
        return media_object


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
        metadata: dict[str, Any] | None = None,
        _client: "client.Client | None",
    ):
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
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.metadata = metadata or {}

    @classmethod
    def from_dict(
        cls: Type["Show"], data: models.Show, *, into: "Show | None" = None, _client: "client.Client | None"
    ) -> "Show":
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
        into.metadata = data.get("metadata") or {}
        into.hidden = data.get("hidden", False)
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
            metadata=self.metadata,
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
        path = f"{self.path_prefix()}/sequences"
        params = _params(
            display_hidden="true" if include_hidden else None,
            page=page,
            per_page=per_page,
        )
        all_sequences_model = TypedDict("all_sequences_model", {"sequences": list[models.Sequence]})
        all_sequences = cast(all_sequences_model, await self.client.get(path, params=params))
        return [
            Sequence.from_dict(sequence, _show=self, _episode=None, _client=self.client)
            for sequence in all_sequences["sequences"]
        ]

    async def get_episode(self, episode_id: int) -> Episode:
        path = f"{self.path_prefix()}/episode/{episode_id}"
        episode = cast(models.Episode, await self.client.get(path))
        return Episode.from_dict(episode, _show=self, _client=self.client)

    async def get_all_episodes(self) -> list[Episode]:
        path = f"{self.path_prefix()}/episodes"
        all_episodes_model = TypedDict("all_episodes_model", {"episodes": list[models.Episode]})
        all_episodes = cast(all_episodes_model, await self.client.get(path))
        return [Episode.from_dict(episode, _show=self, _client=self.client) for episode in all_episodes["episodes"]]

    async def create_assets(self, num_assets: int) -> list[Asset]:
        path = f"{self.path_prefix()}/asset"
        body = {"asset_count": num_assets}
        assets_model = TypedDict("assets_model", {"assets": list[models.Asset]})
        assets = cast(assets_model, await self.client.post(path, body=body))
        return [Asset.from_dict(asset, _client=self.client) for asset in assets["assets"]]

    async def create_media_objects(self, assets: list[Asset], ref: str) -> list[MediaObject]:
        path = f"{self.path_prefix()}/media_object/{ref}"
        body = {"asset_ids": [asset.asset_id for asset in assets]}
        mos_model = TypedDict("mos_model", {"media_objects": list[models.MediaObject]})
        mos = cast(mos_model, await self.client.post(path, body=body))
        media_objects = [MediaObject.from_dict(mo, _client=self.client) for mo in mos["media_objects"]]

        asset_by_id: dict[int, Asset] = {asset.asset_id: asset for asset in assets}
        for mo in media_objects:
            if asset := asset_by_id.get(mo.asset_id):
                asset.media_objects.setdefault(ref, []).append(mo)

        return media_objects

    async def upload_file(self, f: BinaryIO, ref: str) -> Asset:
        asset = (await self.create_assets(1))[0]
        mo = await asset.create_media_object(ref)
        await mo.upload(f)
        return asset

    def new_episode(
        self,
        episode_number: int,
        tracking_code: str,
        title: str = "",
        description: str = "",
    ) -> Episode:
        if not self.episodic:
            raise RuntimeError("cannot create an episode in a non-episodic show")
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

    async def save(self, force_create_new: bool = False) -> None:
        if self.show_id is None or force_create_new:
            path = "/show"
            result = cast(models.Show, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.Show, await self.client.patch(path, body=self.to_dict()))
        self.from_dict(result, into=self, _client=self.client)


@dataclasses.dataclass
class Keyframe:
    start_key: int
    scale: float = 100
    rotation: float = 0
    center_horiz: float = 0
    center_vert: float = 0
    anchor_point_horiz: float = 0
    anchor_point_vert: float = 0
    show_id: int | None = None
    sequence_id: int | None = None
    panel_id: int | None = None
    panel_revision: int | None = None

    @staticmethod
    def from_dict(data: models.Keyframe) -> "Keyframe":
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
    def from_dict(data: models.PanelComment, *, _client: "client.Client | None") -> "PanelComment":
        return PanelComment(
            comment_id=data["id"],
            body=data.get("body", ""),
            panel_id=data["panel_id"],
            revision_id=data["revision_id"],
            closer_user_id=data.get("closer_user_id"),
            closed_date=dateutil.parser.parse(data["closed_date"]) if data.get("closed_date") else None,
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
    def from_dict(data: models.OriginSBP) -> "OriginSBP":
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
    def from_dict(data: models.OriginAvid) -> "OriginAvid":
        return OriginAvid(
            effects_hash=data.get("effects_hash") or None,
        )

    def to_dict(self) -> models.OriginAvid:
        return models.OriginAvid(
            effects_hash=self.effects_hash or "",
        )


@dataclasses.dataclass
class DuplicateRef:
    panel_id: int
    panel_revision: int
    sequence_id: int

    @staticmethod
    def from_dict(data: models.DuplicateRef) -> "DuplicateRef":
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


class PanelRevision(FlixType):
    def __init__(
        self,
        origin: str = "Manual Import",
        asset: Asset | None = None,
        is_ref: bool = False,
        keyframes: list[Keyframe] | None = None,
        related_panels: list["PanelRevision"] | None = None,
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
        layer_transform: bool = False,
        duplicate: DuplicateRef | None = None,
        metadata: dict[str, Any] | None = None,
        _sequence: Sequence | None,
        _client: "client.Client | None",
    ):
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
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.modified_date: datetime.datetime = modified_date or datetime.datetime.utcnow()
        self.owner = owner
        self.published = published
        self.latest_open_comment = latest_open_comment
        self.origin_sbp = origin_sbp
        self.origin_avid = origin_avid
        self.layer_transform = layer_transform
        self.duplicate = duplicate
        self.metadata: dict[str, Any] = metadata or {}

    @classmethod
    def from_dict(
        cls: Type["PanelRevision"],
        data: models.PanelRevision,
        *,
        into: "PanelRevision | None" = None,
        _sequence: Sequence | None,
        _client: "client.Client | None",
    ) -> "PanelRevision":
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
        into.revision_counter = data.get("revision_counter", 0)
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.modified_date = dateutil.parser.parse(data["modified_date"])
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.published = data.get("published", None)
        into.latest_open_comment = (
            PanelComment.from_dict(data["latest_open_comment"], _client=_client)
            if data.get("latest_open_comment")
            else None
        )
        into.origin_sbp = OriginSBP.from_dict(data["origin_sbp"]) if data.get("origin_sbp") else None
        into.origin_avid = OriginAvid.from_dict(data["origin_avid"]) if data.get("origin_avid") else None
        into.layer_transform = data.get("layer_transform", False)
        into.duplicate = DuplicateRef.from_dict(data["duplicate"]) if data.get("duplicate") else None
        into.metadata = data.get("metadata") or {}
        return into

    def to_dict(self) -> models.PanelRevision:
        pr = models.PanelRevision(
            origin=self.origin,
            is_ref=self.is_ref,
            keyframes=[keyframe.to_dict() for keyframe in self.keyframes],
            related_panels=[panel.to_dict() for panel in self.related_panels],
            published=self.published,
            metadata=self.metadata,
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

    def path_prefix(self, include_episode: bool = False) -> str:
        if self._sequence is None:
            raise RuntimeError("sequence is not set")
        return f"{self._sequence.path_prefix(include_episode)}/panel/{self.panel_id}"

    def new_sequence_panel(
        self,
        duration: int = 12,
        trim_in_frame: int | None = None,
        trim_out_frame: int | None = None,
    ) -> "SequencePanel":
        return SequencePanel(
            panel=self,
            duration=duration,
            trim_in_frame=trim_in_frame or 0,
            trim_out_frame=trim_out_frame or 0,
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
    ) -> Keyframe:
        kf = Keyframe(
            start_key=start_key,
            scale=scale,
            rotation=rotation,
            center_horiz=center_horiz,
            center_vert=center_vert,
            anchor_point_horiz=anchor_point_horiz,
            anchor_point_vert=anchor_point_vert,
        )
        self.keyframes.append(kf)
        return kf

    async def save(self, force_create_new_panel: bool = False) -> None:
        if self._sequence is None:
            raise RuntimeError("sequence is not set")

        if self.panel_id is None or force_create_new_panel:
            path = f"{self._sequence.path_prefix()}/panel"
            panel = cast(models.Panel, await self.client.post(path, body=self.to_dict()))
            result = panel["revision"]
        else:
            path = f"{self.path_prefix()}/revision"
            result = cast(models.PanelRevision, await self.client.post(path, body=self.to_dict()))
        self.from_dict(result, into=self, _sequence=self._sequence, _client=self.client)


@dataclasses.dataclass
class SequencePanel:
    panel: PanelRevision
    duration: int
    trim_in_frame: int
    trim_out_frame: int

    @classmethod
    def from_dict(
        cls, data: models.PanelRevision, *, _sequence: Sequence | None, _client: "client.Client | None"
    ) -> "SequencePanel":
        return cls(
            panel=PanelRevision.from_dict(data, _sequence=_sequence, _client=_client),
            duration=data.get("duration") or 12,
            trim_in_frame=data.get("trim_in_frame") or 0,
            trim_out_frame=data.get("trim_out_frame") or 0,
        )

    def to_dict(self) -> models.RevisionedPanel:
        pr = models.RevisionedPanel(
            duration=self.duration,
            trim_in_frame=self.trim_in_frame,
            trim_out_frame=self.trim_out_frame,
        )
        if self.panel.panel_id is not None:
            pr["id"] = self.panel.panel_id
        if self.panel.revision_number is not None:
            pr["revision_number"] = self.panel.revision_number
        return pr


class SequenceRevision(FlixType):
    def __init__(
        self,
        panels: list[SequencePanel] | None = None,
        comment: str = "",
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
        metadata: dict[str, Any] | None = None,
        _sequence: Sequence | None,
        _client: "client.Client | None",
    ):
        super().__init__(_client)
        self._sequence = _sequence
        self.sequence_id = sequence_id
        self.episode_id = episode_id
        self.show_id = show_id
        self.revision_number = revision_number
        self.panels = panels or []
        self.comment = comment
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.published = published
        self.imported = imported
        self.task_id = task_id
        self.source_files = source_files or []
        self.metadata: dict[str, Any] = metadata or {}

    @classmethod
    def from_dict(
        cls,
        data: models.SequenceRevision,
        *,
        into: "SequenceRevision | None" = None,
        _sequence: Sequence | None,
        _client: "client.Client | None",
    ) -> "SequenceRevision":
        if into is None:
            into = cls(_sequence=_sequence, _client=_client)
        into.revision_number = data["revision"]
        into.sequence_id = data["sequence_id"]
        into.episode_id = data.get("episode_id", 0)
        into.show_id = data["show_id"]
        into.comment = data.get("comment", "")
        into.owner = User.from_dict(data["owner"], _client=_client) if data.get("owner") else None
        into.created_date = dateutil.parser.parse(data["created_date"])
        into.published = data.get("published", False)
        into.imported = data.get("imported", False)
        into.task_id = data.get("task_id")
        into.source_files = [Asset.from_dict(asset, _client=_client) for asset in data.get("source_files") or []]
        into.metadata = data.get("meta_data") or {}
        return into

    def to_dict(self) -> models.SequenceRevision:
        revision = models.SequenceRevision(
            comment=self.comment,
            revisioned_panels=[panel.to_dict() for panel in self.panels],
            source_files=[asset.to_dict() for asset in self.source_files],
            meta_data=self.metadata,
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
        if self._sequence is None:
            raise RuntimeError("sequence is not set")
        return f"{self._sequence.path_prefix(include_episode)}/revision/{self.revision_number}"

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
            )
        )

    def add_sequence_panel(self, sequence_panel: SequencePanel) -> None:
        self.panels.append(sequence_panel)

    async def get_all_panel_revisions(self) -> list[SequencePanel]:
        path = f"{self.path_prefix()}/panels"
        all_panels_model = TypedDict("all_panels_model", {"panels": list[models.PanelRevision]})
        all_panels = cast(all_panels_model, await self.client.get(path))
        return [
            SequencePanel.from_dict(panel, _sequence=self._sequence, _client=self.client)
            for panel in all_panels["panels"]
        ]

    async def save(self, force_create_new: bool = False) -> None:
        if self._sequence is None:
            raise RuntimeError("sequence is not set")

        if self.revision_number is None or force_create_new:
            path = f"{self._sequence.path_prefix()}/revision"
            result = cast(models.SequenceRevision, await self.client.post(path, body=self.to_dict()))
        else:
            path = self.path_prefix()
            result = cast(models.SequenceRevision, await self.client.patch(path, body=self.to_dict()))
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
    def from_dict(cls, data: models.Server) -> "Server":
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
