from typing import TypedDict, Any


class Group(TypedDict, total=False):
    id: int
    title: str


class Permission(TypedDict, total=False):
    name: str
    mask: int


class Role(TypedDict, total=False):
    id: int
    name: str
    permissions: list[Permission]


class GroupRolePair(TypedDict, total=False):
    group: Group
    role: Role


class User(TypedDict, total=False):
    created_date: str
    deleted: bool
    email: str
    groups: list[GroupRolePair]
    id: int
    is_admin: bool
    is_system: bool
    is_third_party: bool
    type: str
    username: str


class MediaObject(TypedDict, total=False):
    id: int
    asset_id: int
    name: str
    content_type: str
    content_length: int
    content_hash: str
    created_date: str
    status: int
    owner: User
    asset_type: str
    show_id: int


class Asset(TypedDict, total=False):
    asset_id: int
    show_id: int
    created_date: str
    owner_id: User
    source_id: str
    media_objects: dict[str, list[MediaObject]]


class Sequence(TypedDict, total=False):
    id: int
    description: str
    created_date: str
    owner: User
    revisions_count: int
    panel_revision_count: int
    deleted: bool
    hidden: bool
    meta_data: dict[str, Any]
    tracking_code: str


class Episode(TypedDict, total=False):
    id: int
    created_date: str
    episode_number: int
    owner: User
    description: str
    title: str
    meta_data: dict[str, Any]
    tracking_code: str
    sequences: list[Sequence]


class RevisionedDialogue(TypedDict, total=False):
    id: int


class RevisionedPanel(TypedDict, total=False):
    id: int
    revision_number: int
    duration: int
    dialogue: RevisionedDialogue
    trim_in_frame: int
    trim_out_frame: int


class SequenceRevision(TypedDict, total=False):
    revision: int
    owner: User
    created_date: str
    meta_data: dict[str, Any]
    revisioned_panels: list[RevisionedPanel]
    comment: str
    published: bool
    imported: bool
    sequence_id: int
    episode_id: int
    show_id: int
    task_id: str
    source_files: list[Asset]


class Show(TypedDict, total=False):
    id: int
    aspect_ratio: float
    created_date: str
    description: str
    episodic: bool
    frame_rate: float
    groups: list[Group]
    hidden: bool
    metadata: dict[str, Any]
    owner: User
    show_thumbnail_id: int
    title: str
    tracking_code: str


class PanelComment(TypedDict, total=False):
    body: str
    closer_user_id: int
    closed_date: str
    created_date: str
    closed: bool
    deleted: bool
    id: int
    owner: User
    panel_id: int
    revision_id: int


class OriginAvid(TypedDict, total=False):
    effects_hash: str


class OriginSBP(TypedDict, total=False):
    project_path: str
    sbp_id: str
    mastercomment2: str
    layer_transform_hash: str | None


class DuplicateRef(TypedDict, total=False):
    panel_id: int
    panel_revision: int
    sequence_id: int


class Keyframe(TypedDict, total=False):
    show_id: int
    sequence_id: int
    panel_id: int
    panel_revision: int
    start_key: int
    scale: float
    rotation: float
    center_horiz: float
    center_vert: float
    anchor_point_horiz: float
    anchor_point_vert: float


class PanelRevision(TypedDict, total=False):
    sequence_id: int
    show_id: int
    panel_id: int
    revision_number: int
    created_date: str
    modified_date: str
    metadata: dict[str, Any]
    asset: Asset
    owner: User
    published: int | None
    revision_counter: int
    is_ref: bool
    latest_open_comment: PanelComment
    origin: str
    origin_avid: OriginAvid
    origin_sbp: OriginSBP
    keyframes: list[Keyframe]
    layer_transform: bool
    duplicate: DuplicateRef
    related_panels: list["PanelRevision"]

    # only present when fetching panel in sequence revision
    duration: int
    trim_in_frame: int
    trim_out_frame: int


class Panel(TypedDict):
    id: int
    sequence_id: int
    show_id: int
    created_date: str
    revision_count: int
    owner: User
    deleted: bool
    metadata: dict[str, Any]
    asset: Asset
    revision: PanelRevision


class PageSize(TypedDict):
    width: int
    height: int


class ContactSheet(TypedDict, total=False):
    id: int
    name: str
    created_date: str
    modified_date: str
    owner: User
    shows: list[Show]
    orientation: int
    page_size: PageSize
    style: int
    columns: int
    rows: int
    panel_options: list[str]
    show_header: bool
    show_comments: bool
    show_watermark: bool
    show_company: bool
    show_cover: bool
    cover_options: list[str]
    cover_description: str


class Event(TypedDict, total=False):
    event_type: str


class PublishToEditorialEvent(Event):
    created_media_objects: list[MediaObject]
    sequence: Sequence
    sequence_revision: SequenceRevision
    show: Show
    target_app: str
    user: User


class PublishToFlixEvent(Event):
    sequence: Sequence
    new_sequence_revision: SequenceRevision
    show: Show
    source_app: str
    user: User


class ExportToSBPEvent(Event):
    sequence_revision: SequenceRevision


class ErrorEvent(Event):
    message: str
    fields: dict[str, Any]


class PanelRevisionCreatedEvent(Event):
    panel_revision: PanelRevision


class SequenceRevisionCreatedEvent(Event):
    sequence_revision: SequenceRevision


class ContactSheetCreatedEvent(Event):
    asset: Asset
    sequence: Sequence
    sequence_revision: SequenceRevision
    show: Show
    user: User


class PingEvent(Event):
    event_time: str
    user: User


class WebhookEvent(TypedDict):
    name: str


class Webhook(TypedDict):
    id: int
    name: str
    events: list[WebhookEvent]
    protocol: str
    url: str
    user: User
    skip_tls: bool
    retry_count: int
    email_on_failure: bool
    disabled: bool


class Server(TypedDict):
    id: str
    region: str
    ip: str
    port: int
    running: bool
    start_date: str
    hostname: str
    db_ident: str
    is_ssl: bool
    transfer_port: int
