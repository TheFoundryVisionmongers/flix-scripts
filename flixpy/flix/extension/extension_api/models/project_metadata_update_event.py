from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.episode_details_dto import EpisodeDetailsDto
  from ..models.sequence_details_dto import SequenceDetailsDto
  from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto
  from ..models.show_details_dto import ShowDetailsDto





T = TypeVar("T", bound="ProjectMetadataUpdateEvent")



@_attrs_define
class ProjectMetadataUpdateEvent:
    """ 
        Attributes:
            success (bool):
            show (ShowDetailsDto | Unset):
            episode (EpisodeDetailsDto | Unset):
            sequence (SequenceDetailsDto | Unset):
            sequence_revision (SequenceRevisionDetailsDto | Unset):
     """

    success: bool
    show: ShowDetailsDto | Unset = UNSET
    episode: EpisodeDetailsDto | Unset = UNSET
    sequence: SequenceDetailsDto | Unset = UNSET
    sequence_revision: SequenceRevisionDetailsDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.episode_details_dto import EpisodeDetailsDto # noqa: PLC0415
        from ..models.sequence_details_dto import SequenceDetailsDto # noqa: PLC0415
        from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto # noqa: PLC0415
        from ..models.show_details_dto import ShowDetailsDto # noqa: PLC0415
        success = self.success

        show: dict[str, Any] | Unset = UNSET
        if not isinstance(self.show, Unset):
            show = self.show.to_dict()

        episode: dict[str, Any] | Unset = UNSET
        if not isinstance(self.episode, Unset):
            episode = self.episode.to_dict()

        sequence: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sequence, Unset):
            sequence = self.sequence.to_dict()

        sequence_revision: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sequence_revision, Unset):
            sequence_revision = self.sequence_revision.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "success": success,
        })
        if show is not UNSET:
            field_dict["show"] = show
        if episode is not UNSET:
            field_dict["episode"] = episode
        if sequence is not UNSET:
            field_dict["sequence"] = sequence
        if sequence_revision is not UNSET:
            field_dict["sequenceRevision"] = sequence_revision

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_details_dto import EpisodeDetailsDto # noqa: PLC0415
        from ..models.sequence_details_dto import SequenceDetailsDto # noqa: PLC0415
        from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto # noqa: PLC0415
        from ..models.show_details_dto import ShowDetailsDto # noqa: PLC0415
        d = dict(src_dict)
        success = d.pop("success")

        _show = d.pop("show", UNSET)
        show: ShowDetailsDto | Unset
        if isinstance(_show,  Unset):
            show = UNSET
        else:
            show = ShowDetailsDto.from_dict(_show)




        _episode = d.pop("episode", UNSET)
        episode: EpisodeDetailsDto | Unset
        if isinstance(_episode,  Unset):
            episode = UNSET
        else:
            episode = EpisodeDetailsDto.from_dict(_episode)




        _sequence = d.pop("sequence", UNSET)
        sequence: SequenceDetailsDto | Unset
        if isinstance(_sequence,  Unset):
            sequence = UNSET
        else:
            sequence = SequenceDetailsDto.from_dict(_sequence)




        _sequence_revision = d.pop("sequenceRevision", UNSET)
        sequence_revision: SequenceRevisionDetailsDto | Unset
        if isinstance(_sequence_revision,  Unset):
            sequence_revision = UNSET
        else:
            sequence_revision = SequenceRevisionDetailsDto.from_dict(_sequence_revision)




        project_metadata_update_event = cls(
            success=success,
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )


        project_metadata_update_event.additional_properties = d
        return project_metadata_update_event

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
