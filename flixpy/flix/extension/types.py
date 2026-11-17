"""Pythonic abstractions of the types use by the General Remote Client API."""

from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import Self

from ..lib import types as flix_types
from .extension_api import models
from .extension_api.models import (
    ActionState,
    ActionType,
    AssetType,
    ClientEventType,
    SourceFilePreviewMode,
    SourceFileType,
)
from .extension_api.types import UNSET, Unset

if TYPE_CHECKING:
    import datetime

__all__ = [
    "ActionEvent",
    "ActionEventPanel",
    "ActionRegistrationResponse",
    "ActionState",
    "ActionType",
    "ActionsInProgress",
    "AssetType",
    "ClientEvent",
    "ClientEventType",
    "ClientPingEvent",
    "ConnectionEvent",
    "CustomActionRegistrationRequest",
    "DownloadResponse",
    "Event",
    "OpenEvent",
    "OpenPanelData",
    "OpenShot",
    "OpenSourceFileEvent",
    "PanelBrowserStatus",
    "PanelMetadataUpdate",
    "PanelMetadataUpdateEvent",
    "PanelRequestResponse",
    "PanelRevisionDetails",
    "PanelSelection",
    "ProjectDetails",
    "ProjectEvent",
    "ProjectIds",
    "ProjectMetadata",
    "ProjectMetadataUpdateEvent",
    "RevisionStatus",
    "SourceFile",
    "SourceFilePreviewMode",
    "SourceFileType",
    "Status",
    "StatusEvent",
    "VersionEvent",
    "VersionResponse",
]

_T = TypeVar("_T")


def _or_unset(value: _T | None) -> _T | Unset:
    """Convert an optional value into the Unset sentinel used by the generated models."""
    return UNSET if value is None else value


def _none_if_unset(value: _T | Unset) -> _T | None:
    """Convert the Unset sentinel used by the generated models into None."""
    return None if isinstance(value, Unset) else value


@dataclasses.dataclass
class SourceFile:
    path: str
    preview_mode: SourceFilePreviewMode
    source_file_type: SourceFileType


class Status(enum.IntFlag):
    ONLINE = enum.auto()
    READY_TO_SEND = enum.auto()
    NO_REVISION = enum.auto()
    NO_PERMISSION = enum.auto()
    MULTIPLE_PANELS_SELECTED = enum.auto()


@dataclasses.dataclass
class ProjectDetails:
    show: flix_types.Show | None = None
    episode: flix_types.Episode | None = None
    sequence: flix_types.Sequence | None = None
    sequence_revision: flix_types.SequenceRevision | None = None

    @classmethod
    def from_model(cls, data: models.ProjectDetailsDto) -> Self:
        show: flix_types.Show | None = None
        episode: flix_types.Episode | None = None
        sequence: flix_types.Sequence | None = None
        sequence_revision: flix_types.SequenceRevision | None = None

        if data.show is not None:
            show = flix_types.Show(
                show_id=data.show.id,
                tracking_code=data.show.tracking_code,
                aspect_ratio=data.show.aspect_ratio,
                title=data.show.title or "",
                metadata=data.show.metadata.to_dict(),
                _client=None,
            )

            if data.episode is not None:
                episode = flix_types.Episode(
                    episode_id=data.episode.id,
                    tracking_code=data.episode.tracking_code,
                    created_date=data.episode.created_date,
                    title=data.episode.title or "",
                    owner=flix_types.User(data.episode.owner, _client=None),
                    metadata=data.episode.metadata.to_dict(),
                    _show=show,
                    _client=None,
                )

            if data.sequence is not None:
                sequence = flix_types.Sequence(
                    sequence_id=data.sequence.id,
                    tracking_code=data.sequence.tracking_code,
                    created_date=data.sequence.created_date,
                    description=data.sequence.title or "",
                    owner=flix_types.User(data.sequence.owner, _client=None),
                    metadata=data.sequence.metadata.to_dict(),
                    _show=show,
                    _episode=episode,
                    _client=None,
                )

                if (rev := data.sequence_revision) is not None:
                    sequence_revision = flix_types.SequenceRevision(
                        revision_number=rev.id,
                        published=rev.published,
                        comment=rev.comment or "",
                        created_date=rev.created_date,
                        metadata=rev.metadata.to_dict(),
                        owner=flix_types.User(rev.owner, _client=None) if rev.owner else None,
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


@dataclasses.dataclass
class ClientEvent(Event):
    type: str
    additional_properties: dict[str, Any]

    @classmethod
    def parse_event(cls, event_data: dict[str, Any]) -> ClientEvent:  # noqa: PLR0911, C901
        try:
            ws_event = models.WebsocketEvent.from_dict(event_data)
        except (ValueError, LookupError, TypeError) as e:
            if (data := event_data.get("data")) and isinstance(data, dict) and "type" in data:
                return cls(type=str(data.pop("type")), additional_properties=data) # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            else:
                raise ValueError("unexpected event format") from e

        data, event_type = ws_event.data.data, ws_event.data.type
        if isinstance(data, models.OpenFileEvent):
            return OpenEvent.from_dict(event_type, data)
        elif isinstance(data, models.OpenSourceFileEvent):
            return OpenSourceFileEvent.from_dict(event_type, data)
        elif isinstance(data, models.ActionEvent):
            return ActionEvent.from_dict(event_type, data)
        elif isinstance(data, models.ProjectDetailsDto):
            return ProjectEvent.from_dict(event_type, data)
        elif isinstance(data, models.VersionEvent):
            return VersionEvent.from_dict(event_type, data)
        elif isinstance(data, models.StatusResponse):
            return StatusEvent.from_dict(event_type, data)
        elif isinstance(data, models.PingEvent):
            return ClientPingEvent.from_dict(event_type, data)
        elif isinstance(data, models.PanelMetadataUpdateEvent):
            return PanelMetadataUpdateEvent.from_dict(event_type, data)
        elif isinstance(data, models.ProjectMetadataUpdateEvent):
            return ProjectMetadataUpdateEvent.from_dict(event_type, data)

        return cls(
            type=event_type,
            additional_properties=data.to_dict(),
        )


@dataclasses.dataclass
class ClientPingEvent(ClientEvent):
    api_client_id: int

    @classmethod
    def from_dict(cls, event_type: str, data: models.PingEvent) -> Self:
        return cls(
            type=event_type,
            api_client_id=data.api_client_id,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ActionEventPanel:
    panel_id: int
    panel_revision: int
    path: str
    metadata: dict[str, str]

    @classmethod
    def from_dict(cls, data: models.ActionEventPanelResponse) -> Self:
        return cls(
            panel_id=data.panel_id,
            panel_revision=data.panel_revision,
            path=data.path,
            metadata={} if isinstance(data.metadata, Unset) else data.metadata.to_dict(),
        )


@dataclasses.dataclass
class ActionEvent(ClientEvent):
    state: ActionState
    action: ActionType
    action_id: int
    api_client_id: int | None
    panels: list[ActionEventPanel]

    @classmethod
    def from_dict(cls, event_type: str, data: models.ActionEvent) -> Self:
        return cls(
            type=event_type,
            state=data.state,
            action=data.action,
            action_id=data.action_id,
            api_client_id=data.api_client_id,
            panels=[ActionEventPanel.from_dict(panel) for panel in data.panels]
            if not isinstance(data.panels, Unset)
            else [],
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class VersionEvent(ClientEvent):
    latest_version: str

    @classmethod
    def from_dict(cls, event_type: str, data: models.VersionEvent) -> Self:
        return cls(
            type=event_type,
            latest_version=data.latest_version,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ProjectEvent(ProjectDetails, ClientEvent):
    @classmethod
    def from_dict(cls, event_type: str, data: models.ProjectDetailsDto) -> Self:
        project_details = ProjectDetails.from_model(data)
        return cls(
            type=event_type,
            show=project_details.show,
            episode=project_details.episode,
            sequence=project_details.sequence,
            sequence_revision=project_details.sequence_revision,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class PanelMetadataUpdate:
    """The metadata of a single panel, as returned after it was updated."""

    panel_id: int
    metadata: dict[str, str]

    @classmethod
    def from_model(
        cls,
        data: models.UpdatedPanelMetadataDto | models.PanelUpdateMetadataResponseItem,
    ) -> Self:
        return cls(panel_id=data.id, metadata=data.metadata.to_dict())


@dataclasses.dataclass
class PanelMetadataUpdateEvent(ClientEvent):
    panels: list[PanelMetadataUpdate]

    @classmethod
    def from_dict(cls, event_type: str, data: models.PanelMetadataUpdateEvent) -> Self:
        return cls(
            type=event_type,
            panels=[PanelMetadataUpdate.from_model(panel) for panel in data.panels],
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ProjectMetadata:
    """Custom metadata for the entities in the currently open project.

    Each field maps metadata keys to values. A field that is None is not present:
    it is left out of an update, or was not included in an event from the Flix Client.
    When updating, a value of None deletes that key.
    """

    show: dict[str, str | None] | None = None
    episode: dict[str, str | None] | None = None
    sequence: dict[str, str | None] | None = None
    sequence_revision: dict[str, str | None] | None = None

    @classmethod
    def from_model(cls, data: models.ProjectDetailsMetadataDto) -> Self:
        return cls(
            show=None if isinstance(data.show, Unset) else data.show.to_dict(),
            episode=None if isinstance(data.episode, Unset) else data.episode.to_dict(),
            sequence=None if isinstance(data.sequence, Unset) else data.sequence.to_dict(),
            sequence_revision=None
            if isinstance(data.sequence_revision, Unset)
            else data.sequence_revision.to_dict(),
        )

    def to_model(self) -> models.ProjectDetailsMetadataDto:
        return models.ProjectDetailsMetadataDto(
            show=UNSET
            if self.show is None
            else models.ProjectDetailsMetadataDtoShow.from_dict(self.show),
            episode=UNSET
            if self.episode is None
            else models.ProjectDetailsMetadataDtoEpisode.from_dict(self.episode),
            sequence=UNSET
            if self.sequence is None
            else models.ProjectDetailsMetadataDtoSequence.from_dict(self.sequence),
            sequence_revision=UNSET
            if self.sequence_revision is None
            else models.ProjectDetailsMetadataDtoSequenceRevision.from_dict(self.sequence_revision),
        )


@dataclasses.dataclass
class ProjectMetadataUpdateEvent(ClientEvent):
    success: bool
    metadata: ProjectMetadata

    @classmethod
    def from_dict(cls, event_type: str, data: models.ProjectMetadataUpdateEvent) -> Self:
        return cls(
            type=event_type,
            success=data.success,
            metadata=ProjectMetadata(
                show=None if isinstance(data.show, Unset) else data.show.metadata.to_dict(),
                episode=None
                if isinstance(data.episode, Unset)
                else data.episode.metadata.to_dict(),
                sequence=None
                if isinstance(data.sequence, Unset)
                else data.sequence.metadata.to_dict(),
                sequence_revision=None
                if isinstance(data.sequence_revision, Unset)
                else data.sequence_revision.metadata.to_dict(),
            ),
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class ProjectIds:
    show_id: int | None
    episode_id: int | None
    sequence_id: int | None
    sequence_revision_number: int | None

    @classmethod
    def from_dict(cls, data: models.ProjectIdsDto) -> Self:
        return cls(
            show_id=data.show_id if data.show_id else None,
            episode_id=data.episode_id if data.episode_id else None,
            sequence_id=data.sequence_id if data.sequence_id else None,
            sequence_revision_number=data.sequence_revision_id
            if data.sequence_revision_id
            else None,
        )


@dataclasses.dataclass
class PanelSelection:
    id: int
    revision_id: int
    index: int

    @classmethod
    def from_dict(cls, data: models.PanelSelectionResponse) -> Self:
        return cls(
            id=data.id,
            revision_id=data.revision_id,
            index=data.index,
        )


@dataclasses.dataclass
class RevisionStatus:
    can_save: bool = False
    can_publish: bool = False
    can_export: bool = False
    selected_panels: list[int] = dataclasses.field(default_factory=list[int])
    panel_selection: list[PanelSelection] = dataclasses.field(default_factory=list[PanelSelection])


@dataclasses.dataclass
class ActionsInProgress:
    is_saving: bool = False
    is_publishing: bool = False
    is_exporting: bool = False


@dataclasses.dataclass
class PanelBrowserStatus:
    can_create: bool = False
    revision_status: RevisionStatus = dataclasses.field(default_factory=RevisionStatus)
    actions_in_progress: ActionsInProgress = dataclasses.field(default_factory=ActionsInProgress)

    @classmethod
    def from_model(cls, data: models.StatusResponse) -> Self:
        return cls(
            can_create=data.can_create,
            revision_status=RevisionStatus(
                can_save=data.revision_status.can_save,
                can_publish=data.revision_status.can_publish,
                can_export=data.revision_status.can_export,
                selected_panels=data.revision_status.selected_panels,
                panel_selection=[
                    PanelSelection.from_dict(panel)
                    for panel in data.revision_status.panel_selection
                ]
                if not isinstance(data.revision_status.panel_selection, Unset)
                else [],
            ),
            actions_in_progress=ActionsInProgress(
                is_saving=data.actions_in_progress.is_saving,
                is_publishing=data.actions_in_progress.is_publishing,
                is_exporting=data.actions_in_progress.is_exporting,
            ),
        )


@dataclasses.dataclass
class StatusEvent(PanelBrowserStatus, ClientEvent):
    @classmethod
    def from_dict(cls, event_type: str, data: models.StatusResponse) -> Self:
        status = PanelBrowserStatus.from_model(data)
        return cls(
            type=event_type,
            can_create=status.can_create,
            revision_status=status.revision_status,
            actions_in_progress=status.actions_in_progress,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class OpenPanelData:
    panel_id: int
    asset_id: int
    is_animated: bool
    source_file_asset_id: int | None
    annotation_asset_id: int | None
    shot_id: int | None

    @classmethod
    def from_dict(cls, data: models.OpenFilePanelData) -> Self:
        return cls(
            panel_id=data.id,
            asset_id=data.asset_id,
            is_animated=data.is_animated,
            source_file_asset_id=data.source_file.asset_id if data.source_file else None,
            annotation_asset_id=data.annotation_asset_id if data.annotation_asset_id else None,
            shot_id=_none_if_unset(data.shot_id),
        )


@dataclasses.dataclass
class OpenShot:
    shot_id: int
    index: int
    name: str
    start_panel_index: int
    end_panel_index: int

    @classmethod
    def from_dict(cls, data: models.OpenFileShotData) -> Self:
        return cls(
            shot_id=data.id,
            index=data.index,
            name=data.name,
            start_panel_index=data.start_panel_index,
            end_panel_index=data.end_panel_index,
        )


@dataclasses.dataclass
class OpenEvent(ClientEvent):
    project: ProjectIds
    panels: list[OpenPanelData]
    shots: list[OpenShot]
    action_id: str | None

    @classmethod
    def from_dict(cls, event_type: str, data: models.OpenFileEvent) -> Self:
        return cls(
            type=event_type,
            project=ProjectIds.from_dict(data.project),
            panels=[OpenPanelData.from_dict(panel) for panel in data.panels],
            shots=[OpenShot.from_dict(shot) for shot in data.shots],
            additional_properties=data.additional_properties,
            action_id=_none_if_unset(data.action_id),
        )


@dataclasses.dataclass
class OpenSourceFileEvent(ClientEvent):
    asset_id: int

    @classmethod
    def from_dict(cls, event_type: str, data: models.OpenSourceFileEvent) -> Self:
        return cls(
            type=event_type,
            asset_id=data.source_file.asset_id
            if data.source_file and data.source_file.asset_id
            else 0,
            additional_properties=data.additional_properties,
        )


@dataclasses.dataclass
class DownloadResponse:
    file_name: str
    file_path: str
    asset_id: int
    media_object_id: int

    @classmethod
    def from_dict(cls, data: models.DownloadResponse) -> Self:
        return cls(
            file_name=data.file_name,
            file_path=data.file_path,
            asset_id=data.asset_id,
            media_object_id=data.media_object_id,
        )


@dataclasses.dataclass
class PanelRequestResponse:
    message: str
    action_id: int

    @classmethod
    def from_dict(cls, data: models.PanelRequestResponse) -> Self:
        return cls(
            message=data.message,
            action_id=data.action_id,
        )


@dataclasses.dataclass
class VersionResponse:
    flix_version: str
    supported_api_versions: list[str]

    @classmethod
    def from_model(cls, data: models.InfoResponse) -> Self:
        return cls(
            flix_version=data.flix_version,
            supported_api_versions=data.supported_api_versions,
        )


@dataclasses.dataclass
class CustomActionRegistrationRequest:
    """An action that an extension asks the Flix Client to show in the Panel Browser."""

    id: str
    name: str
    description: str | None = None
    icon_svg: str | None = None
    type: models.CustomActionRegistrationRequestType | None = None

    def to_model(self) -> models.CustomActionRegistrationRequest:
        return models.CustomActionRegistrationRequest(
            id=self.id,
            name=self.name,
            description=_or_unset(self.description),
            icon_svg=_or_unset(self.icon_svg),
            type=_or_unset(self.type),
        )


@dataclasses.dataclass
class ActionRegistrationResponse:
    """An action as registered with the Flix Client."""

    id: str
    name: str
    description: str | None
    icon_svg: str | None
    type: models.ActionRegistrationResponseType | None

    @classmethod
    def from_dict(cls, data: models.ActionRegistrationResponse) -> Self:
        return cls(
            id=data.id,
            name=data.name,
            description=_none_if_unset(data.description),
            icon_svg=_none_if_unset(data.icon_svg),
            type=_none_if_unset(data.type),
        )


@dataclasses.dataclass
class PanelRevisionDetails:
    """A panel revision in the sequence revision currently open in the Panel Browser."""

    panel_id: int
    revision_id: int
    panel_position: int
    asset_id: int
    created_date: datetime.datetime
    revision_date: datetime.datetime
    owner: str
    show_id: int
    sequence_id: int
    hidden: bool
    duration: int
    trim_in_frame: int
    trim_out_frame: int
    layer_transform: bool
    dialogue: str
    origin_sbp: dict[str, str]
    keyframes: list[dict[str, Any]]
    origin: str
    shot_name: str
    metadata: dict[str, str]

    @classmethod
    def from_dict(cls, data: models.PanelRevisionDetailsDto) -> Self:
        return cls(
            panel_id=data.panel_id,
            revision_id=data.revision_id,
            panel_position=data.panel_position,
            asset_id=data.asset_id,
            created_date=data.created_date,
            revision_date=data.revision_date,
            owner=data.owner,
            show_id=data.show_id,
            sequence_id=data.sequence_id,
            hidden=data.hidden,
            duration=int(data.duration),
            trim_in_frame=data.trim_in_frame,
            trim_out_frame=data.trim_out_frame,
            layer_transform=data.layer_transform,
            dialogue=data.dialogue,
            origin_sbp=data.origin_sbp.to_dict(),
            keyframes=[keyframe.to_dict() for keyframe in data.keyframes],
            origin=data.origin,
            shot_name=data.shot_name,
            metadata=data.metadata.to_dict(),
        )
