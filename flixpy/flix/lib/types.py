import dataclasses
import datetime
import enum
from typing import Any

import dateutil.parser

from . import models

__all__ = [
    "Group",
    "Permission",
    "Role",
    "GroupRolePair",
    "User",
    "MediaObjectStatus",
    "MediaObject",
    "Sequence",
    "RevisionedDialogue",
    "RevisionedPanel",
    "Asset",
    "SequenceRevision",
    "Show",
    "Keyframe",
    "PanelComment",
    "OriginSBP",
    "DuplicateRef",
    "PanelRevision",
]


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


class User:
    def __init__(
        self,
        username: str,
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
    ):
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

    @staticmethod
    def from_dict(data: models.User) -> "User":
        return User(
            user_id=data["id"],
            username=data.get("username", ""),
            email=data.get("email", ""),
            groups=[GroupRolePair.from_dict(group) for group in data.get("groups") or []],
            created_date=dateutil.parser.parse(data["created_date"]),
            user_type=data.get("type", ""),
            is_admin=data.get("is_admin", False),
            is_system=data.get("is_system", False),
            is_third_party=data.get("is_third_party", False),
            deleted=data.get("deleted", False),
        )


class MediaObjectStatus(enum.Enum):
    INITIALIZED = 0
    UPLOADED = 1
    ERRORED = 2


@dataclasses.dataclass
class MediaObject:
    media_object_id: int
    asset_id: int
    filename: str
    content_type: str
    content_length: int
    content_hash: str
    created_date: datetime.datetime
    status: MediaObjectStatus
    owner: User | None
    asset_type: str
    show_id: int

    @staticmethod
    def from_dict(data: models.MediaObject) -> "MediaObject":
        return MediaObject(
            media_object_id=data["id"],
            asset_id=data["asset_id"],
            filename=data.get("name", ""),
            content_type=data.get("content_type", ""),
            content_length=data.get("content_length", 0),
            content_hash=data.get("content_hash", ""),
            created_date=dateutil.parser.parse(data["created_date"]),
            status=MediaObjectStatus(data["status"]) if data.get("status") else MediaObjectStatus.INITIALIZED,
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
            asset_type=data.get("asset_type", ""),
            show_id=data.get("show_id", 0),
        )


@dataclasses.dataclass
class Sequence:
    def __init__(
        self,
        tracking_code: str = "",
        description: str = "",
        *,
        sequence_id: int | None = None,
        created_date: datetime.datetime | None = None,
        owner: User | None = None,
        revision_count: int = 0,
        panel_revision_count: int = 0,
        metadata: dict[str, Any] | None = None,
    ):
        self.sequence_id = sequence_id
        self.tracking_code = tracking_code
        self.description = description
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.owner = owner
        self.revision_count = revision_count
        self.panel_revision_count = panel_revision_count
        self.metadata: dict[str, Any] = metadata or {}

    @staticmethod
    def from_dict(data: models.Sequence) -> "Sequence":
        return Sequence(
            sequence_id=data["id"],
            tracking_code=data.get("tracking_code", ""),
            description=data.get("description", ""),
            created_date=dateutil.parser.parse(data["created_date"]),
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
            revision_count=data.get("revisions_count", 0),
            panel_revision_count=data.get("panel_revision_count", 0),
            metadata=data.get("meta_data"),
        )


@dataclasses.dataclass
class RevisionedDialogue:
    dialogue_id: int

    @staticmethod
    def from_dict(data: models.RevisionedDialogue) -> "RevisionedDialogue":
        return RevisionedDialogue(dialogue_id=data["id"])


@dataclasses.dataclass
class RevisionedPanel:
    panel_id: int
    revision_number: int
    duration: int
    dialogue: RevisionedDialogue | None = None
    trim_in_frame: int = 0
    trim_out_frame: int = 0

    @staticmethod
    def from_dict(data: models.RevisionedPanel) -> "RevisionedPanel":
        return RevisionedPanel(
            panel_id=data["id"],
            revision_number=data["revision_number"],
            duration=data["duration"],
            dialogue=RevisionedDialogue.from_dict(data["dialogue"]) if "dialogue" in data else None,
            trim_in_frame=data.get("trim_in_frame", 0),
            trim_out_frame=data.get("trim_out_frame", 0),
        )


@dataclasses.dataclass
class Asset:
    asset_id: int
    show_id: int
    created_date: datetime.datetime
    owner: User | None
    media_objects: dict[str, list[MediaObject]]

    @staticmethod
    def from_dict(data: models.Asset) -> "Asset":
        return Asset(
            asset_id=data["asset_id"],
            show_id=data["show_id"],
            created_date=dateutil.parser.parse(data["created_date"]),
            owner=User.from_dict(data["owner_id"]) if data.get("owner_id") else None,
            media_objects={
                ref: [MediaObject.from_dict(mo) for mo in mos] for ref, mos in (data.get("media_objects") or {}).items()
            },
        )


class SequenceRevision:
    def __init__(
        self,
        sequence_id: int,
        episode_id: int,
        show_id: int,
        panels: list[RevisionedPanel] | None = None,
        comment: str = "",
        *,
        revision: int | None = None,
        owner: User | None = None,
        created_date: datetime.datetime | None = None,
        published: bool = False,
        imported: bool = False,
        task_id: str | None = None,
        source_files: list[Asset] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.sequence_id = sequence_id
        self.episode_id = episode_id
        self.show_id = show_id
        self.revision = revision
        self.panels = panels or []
        self.comment = comment
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.published = published
        self.imported = imported
        self.task_id = task_id
        self.source_files = source_files or []
        self.metadata: dict[str, Any] = metadata or {}

    @staticmethod
    def from_dict(data: models.SequenceRevision) -> "SequenceRevision":
        return SequenceRevision(
            revision=data["revision"],
            sequence_id=data["sequence_id"],
            episode_id=data.get("episode_id", 0),
            show_id=data["show_id"],
            panels=[RevisionedPanel.from_dict(panel) for panel in data.get("revisioned_panels") or []],
            comment=data.get("comment", ""),
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
            created_date=dateutil.parser.parse(data["created_date"]),
            published=data.get("published", False),
            imported=data.get("imported", False),
            task_id=data.get("task_id"),
            source_files=[Asset.from_dict(asset) for asset in data.get("source_files") or []],
            metadata=data.get("meta_data"),
        )


class Show:
    def __init__(
        self,
        tracking_code: str,
        aspect_ratio: float,
        frame_rate: float,
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
    ):
        self.show_id = show_id
        self.tracking_code = tracking_code
        self.aspect_ratio = aspect_ratio
        self.frame_rate = frame_rate
        self.title = title
        self.description = description
        self.episodic = episodic
        self.groups = groups or []
        self.show_thumbnail_id = show_thumbnail_id
        self.hidden = hidden
        self.owner = owner
        self.created_date: datetime.datetime = created_date or datetime.datetime.utcnow()
        self.metadata: dict[str, Any] = metadata or {}

    @staticmethod
    def from_dict(data: models.Show) -> "Show":
        return Show(
            show_id=data["id"],
            tracking_code=data.get("tracking_code", ""),
            aspect_ratio=data["aspect_ratio"],
            frame_rate=data["frame_rate"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            groups=[Group.from_dict(group) for group in data.get("groups") or []],
            episodic=data.get("episodic", False),
            show_thumbnail_id=data.get("show_thumbnail_id"),
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
            created_date=dateutil.parser.parse(data["created_date"]),
            metadata=data.get("metadata"),
            hidden=data.get("hidden", False),
        )


@dataclasses.dataclass
class Keyframe:
    show_id: int
    sequence_id: int
    panel_id: int
    panel_revision: int
    start_key: int
    scale: float = 100
    rotation: float = 0
    center_horiz: float = 0
    center_vert: float = 0
    anchor_point_horiz: float = 0
    anchor_point_vert: float = 0

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
    def from_dict(data: models.PanelComment) -> "PanelComment":
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
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
        )


@dataclasses.dataclass
class OriginSBP:
    project_path: str

    @staticmethod
    def from_dict(data: models.OriginSBP) -> "OriginSBP":
        return OriginSBP(project_path=data.get("project_path", ""))


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


class PanelRevision:
    def __init__(
        self,
        sequence_id: int,
        show_id: int,
        panel_id: int,
        duration: int,
        origin: str,
        trim_in_frame: int = 0,
        trim_out_frame: int = 0,
        asset: Asset | None = None,
        is_ref: bool = False,
        keyframes: list[Keyframe] | None = None,
        related_panels: list["PanelRevision"] | None = None,
        *,
        revision_number: int | None = None,
        revision_counter: int = 0,
        created_date: datetime.datetime | None = None,
        modified_date: datetime.datetime | None = None,
        owner: User | None = None,
        published: bool = False,
        latest_open_comment: PanelComment | None = None,
        origin_sbp: OriginSBP | None = None,
        layer_transform: bool = False,
        duplicate: DuplicateRef | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.sequence_id = sequence_id
        self.show_id = show_id
        self.panel_id = panel_id
        self.revision_number = revision_number
        self.duration = duration
        self.origin = origin
        self.trim_in_frame = trim_in_frame
        self.trim_out_frame = trim_out_frame
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
        self.layer_transform = layer_transform
        self.duplicate = duplicate
        self.metadata: dict[str, Any] = metadata or {}

    @staticmethod
    def from_dict(data: models.PanelRevision) -> "PanelRevision":
        return PanelRevision(
            sequence_id=data["sequence_id"],
            show_id=data["show_id"],
            panel_id=data["panel_id"],
            revision_number=data["revision_number"],
            duration=data.get("duration", 0),
            origin=data.get("origin", ""),
            trim_in_frame=data.get("trim_in_frame", 0),
            trim_out_frame=data.get("trim_out_frame", 0),
            asset=Asset.from_dict(data["asset"]) if data.get("asset") else None,
            is_ref=data.get("is_ref", False),
            keyframes=[Keyframe.from_dict(keyframe) for keyframe in data.get("keyframes") or []],
            related_panels=[PanelRevision.from_dict(panel) for panel in data.get("related_panels") or []],
            revision_counter=data.get("revision_counter", 0),
            created_date=dateutil.parser.parse(data["created_date"]),
            modified_date=dateutil.parser.parse(data["modified_date"]),
            owner=User.from_dict(data["owner"]) if data.get("owner") else None,
            published=data.get("published", False),
            latest_open_comment=PanelComment.from_dict(data["latest_open_comment"])
            if data.get("latest_open_comment")
            else None,
            origin_sbp=OriginSBP.from_dict(data["origin_sbp"]) if data.get("origin_sbp") else None,
            layer_transform=data.get("layer_transform", False),
            duplicate=DuplicateRef.from_dict(data["duplicate"]) if data.get("duplicate") else None,
            metadata=data.get("metadata"),
        )
