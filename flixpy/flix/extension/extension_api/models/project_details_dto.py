from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.episode_details_dto import EpisodeDetailsDto
  from ..models.sequence_details_dto import SequenceDetailsDto
  from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto
  from ..models.show_details_dto import ShowDetailsDto





T = TypeVar("T", bound="ProjectDetailsDto")



@_attrs_define
class ProjectDetailsDto:
    """ 
        Attributes:
            show (None | ShowDetailsDto): Details of the currently opened show.
            episode (EpisodeDetailsDto | None): Details of the currently opened episode, if in an episodic show.
            sequence (None | SequenceDetailsDto): Details of the currently opened sequence.
            sequence_revision (None | SequenceRevisionDetailsDto): Details of the currently opened sequence revision.
     """

    show: None | ShowDetailsDto
    episode: EpisodeDetailsDto | None
    sequence: None | SequenceDetailsDto
    sequence_revision: None | SequenceRevisionDetailsDto
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.episode_details_dto import EpisodeDetailsDto # noqa: PLC0415
        from ..models.sequence_details_dto import SequenceDetailsDto # noqa: PLC0415
        from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto # noqa: PLC0415
        from ..models.show_details_dto import ShowDetailsDto # noqa: PLC0415
        show: dict[str, Any] | None
        if isinstance(self.show, ShowDetailsDto):
            show = self.show.to_dict()
        else:
            show = self.show

        episode: dict[str, Any] | None
        if isinstance(self.episode, EpisodeDetailsDto):
            episode = self.episode.to_dict()
        else:
            episode = self.episode

        sequence: dict[str, Any] | None
        if isinstance(self.sequence, SequenceDetailsDto):
            sequence = self.sequence.to_dict()
        else:
            sequence = self.sequence

        sequence_revision: dict[str, Any] | None
        if isinstance(self.sequence_revision, SequenceRevisionDetailsDto):
            sequence_revision = self.sequence_revision.to_dict()
        else:
            sequence_revision = self.sequence_revision


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "show": show,
            "episode": episode,
            "sequence": sequence,
            "sequenceRevision": sequence_revision,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_details_dto import EpisodeDetailsDto # noqa: PLC0415
        from ..models.sequence_details_dto import SequenceDetailsDto # noqa: PLC0415
        from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto # noqa: PLC0415
        from ..models.show_details_dto import ShowDetailsDto # noqa: PLC0415
        d = dict(src_dict)
        def _parse_show(data: object) -> None | ShowDetailsDto:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                show_type_1 = ShowDetailsDto.from_dict(data)



                return show_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ShowDetailsDto, data)

        show = _parse_show(d.pop("show"))


        def _parse_episode(data: object) -> EpisodeDetailsDto | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                episode_type_1 = EpisodeDetailsDto.from_dict(data)



                return episode_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EpisodeDetailsDto | None, data)

        episode = _parse_episode(d.pop("episode"))


        def _parse_sequence(data: object) -> None | SequenceDetailsDto:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sequence_type_1 = SequenceDetailsDto.from_dict(data)



                return sequence_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SequenceDetailsDto, data)

        sequence = _parse_sequence(d.pop("sequence"))


        def _parse_sequence_revision(data: object) -> None | SequenceRevisionDetailsDto:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sequence_revision_type_1 = SequenceRevisionDetailsDto.from_dict(data)



                return sequence_revision_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SequenceRevisionDetailsDto, data)

        sequence_revision = _parse_sequence_revision(d.pop("sequenceRevision"))


        project_details_dto = cls(
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )


        project_details_dto.additional_properties = d
        return project_details_dto

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
