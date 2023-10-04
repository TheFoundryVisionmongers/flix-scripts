import dataclasses
from typing import Any, Protocol

from .extension_api import models
from .extension_api.models import EventType as ClientEventType, ActionType, ActionState, AssetType

from ..lib import types as flix_types


__all__ = [
    "SourceFile",
    "ProjectDetails",
    "Event",
    "ClientEvent",
    "OpenEvent",
    "ClientPingEvent",
    "ActionEvent",
    "ConnectionEvent",
    "OpenPanelData",
    "ProjectEvent",
    "ProjectIds",
    "ClientEventType",
    "ActionState",
    "ActionType",
    "AssetType",
]


@dataclasses.dataclass
class SourceFile:
    id: str
    path: str


@dataclasses.dataclass
class ProjectDetails:
    show: flix_types.Show | None
    episode: flix_types.Episode | None
    sequence: flix_types.Sequence | None
    sequence_revision: flix_types.SequenceRevision | None

    @classmethod
    def from_model(cls, data: models.ProjectDetailsDto) -> "ProjectDetails":
        show: flix_types.Show | None = None
        episode: flix_types.Episode | None = None
        sequence: flix_types.Sequence | None = None
        sequence_revision: flix_types.SequenceRevision | None = None

        if data.show is not None:
            show = flix_types.Show(
                show_id=int(data.show.id),
                tracking_code=data.show.tracking_code,
                aspect_ratio=data.show.aspect_ratio,
                title=data.show.title or "",
                _client=None,
            )

            if data.episode is not None:
                episode = flix_types.Episode(
                    episode_id=int(data.episode.id),
                    tracking_code=data.episode.tracking_code,
                    created_date=data.episode.created_date,
                    title=data.episode.title or "",
                    owner=flix_types.User(data.episode.owner, _client=None),
                    _show=show,
                    _client=None,
                )

            if data.sequence is not None:
                sequence = flix_types.Sequence(
                    sequence_id=int(data.sequence.id),
                    tracking_code=data.sequence.tracking_code,
                    created_date=data.sequence.created_date,
                    description=data.sequence.title or "",
                    owner=flix_types.User(data.sequence.owner, _client=None),
                    _show=show,
                    _episode=episode,
                    _client=None,
                )

                if data.sequence_revision is not None:
                    sequence_revision = flix_types.SequenceRevision(
                        revision_number=int(data.sequence_revision.id),
                        published=data.sequence_revision.published,
                        comment=data.sequence_revision.comment or "",
                        created_date=data.sequence_revision.created_date,
                        owner=flix_types.User(data.sequence_revision.owner or "", _client=None),
                        _sequence=sequence,
                        _client=None,
                    )

        return cls(
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )


@dataclasses.dataclass
class Event:
    pass


@dataclasses.dataclass
class ConnectionEvent(Event):
    online: bool


class _BaseEvent(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


@dataclasses.dataclass
class ClientEvent(Event):
    type: ClientEventType
    additional_properties: dict[str, Any]

    @classmethod
    def parse_event(cls, type: ClientEventType, data: _BaseEvent) -> "ClientEvent":
        if isinstance(data, models.OpenEvent):
            return OpenEvent.from_dict(type, data)
        elif isinstance(data, models.ActionEvent):
            return ActionEvent.from_dict(type, data)
        elif isinstance(data, models.ProjectDetailsDto):
            return ProjectEvent.from_dict(type, data)
        elif isinstance(data, models.PingEvent):
            return ClientPingEvent.from_dict(type, data)
        return cls(
            type=type,
            additional_properties=data.to_dict(),
        )


@dataclasses.dataclass
class ClientPingEvent(ClientEvent):
    api_client_id: int

    @classmethod
    def from_dict(cls, type: ClientEventType, data: models.PingEvent) -> "ClientPingEvent":
        return cls(
            type=type,
            api_client_id=data.api_client_id,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ActionEvent(ClientEvent):
    state: ActionState
    action: ActionType
    action_id: int
    api_client_id: int | None

    @classmethod
    def from_dict(cls, type: ClientEventType, data: models.ActionEvent) -> "ActionEvent":
        return cls(
            type=type,
            state=data.state,
            action=data.action,
            action_id=data.action_id,
            api_client_id=data.api_client_id,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ProjectEvent(ProjectDetails, ClientEvent):
    @classmethod
    def from_dict(cls, type: ClientEventType, data: models.ProjectDetailsDto) -> "ProjectEvent":
        project_details = ProjectDetails.from_model(data)
        return cls(
            type=type,
            show=project_details.show,
            episode=project_details.episode,
            sequence=project_details.sequence,
            sequence_revision=project_details.sequence_revision,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ProjectIds:
    show_id: int | None
    episode_id: int | None
    sequence_id: int | None
    sequence_revision_number: int | None

    @classmethod
    def from_dict(cls, data: models.ProjectIds) -> "ProjectIds":
        return cls(
            show_id=data.show_id if data.show_id else None,
            episode_id=data.episode_id if data.episode_id else None,
            sequence_id=data.sequence_id if data.sequence_id else None,
            sequence_revision_number=data.sequence_revision_id if data.sequence_revision_id else None,
        )


@dataclasses.dataclass
class OpenPanelData:
    panel_id: int
    asset_id: int
    is_animated: bool
    has_source_file: bool
    annotation_asset_id: int | None

    @classmethod
    def from_dict(cls, data: models.ExtensionOpenFilePanelData) -> "OpenPanelData":
        return cls(
            panel_id=data.id,
            asset_id=data.asset_id,
            is_animated=data.is_animated,
            has_source_file=data.has_source_file,
            annotation_asset_id=data.annotation_asset_id if data.annotation_asset_id else None,
        )


@dataclasses.dataclass
class OpenEvent(ClientEvent):
    project: ProjectIds
    panels: list[OpenPanelData]

    @classmethod
    def from_dict(cls, type: ClientEventType, data: models.OpenEvent) -> "OpenEvent":
        return cls(
            type=type,
            project=ProjectIds.from_dict(data.project),
            panels=[OpenPanelData.from_dict(panel) for panel in data.panels],
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class DownloadResponse:
    file_name: str
    file_path: str
    asset_id: int
    media_object_id: int

    @classmethod
    def from_dict(cls, data: models.DownloadResponse) -> "DownloadResponse":
        return cls(
            file_name=data.file_name,
            file_path=data.file_path,
            asset_id=data.asset_id,
            media_object_id=data.media_object_id,
        )
