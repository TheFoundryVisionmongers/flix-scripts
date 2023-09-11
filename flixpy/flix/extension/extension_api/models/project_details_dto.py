from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

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
        show (Optional[ShowDetailsDto]):
        episode (Optional[EpisodeDetailsDto]):
        sequence (Optional[SequenceDetailsDto]):
        sequence_revision (Optional[SequenceRevisionDetailsDto]):
    """

    show: Optional["ShowDetailsDto"]
    episode: Optional["EpisodeDetailsDto"]
    sequence: Optional["SequenceDetailsDto"]
    sequence_revision: Optional["SequenceRevisionDetailsDto"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        show = self.show.to_dict() if self.show else None

        episode = self.episode.to_dict() if self.episode else None

        sequence = self.sequence.to_dict() if self.sequence else None

        sequence_revision = self.sequence_revision.to_dict() if self.sequence_revision else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "show": show,
                "episode": episode,
                "sequence": sequence,
                "sequenceRevision": sequence_revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.episode_details_dto import EpisodeDetailsDto
        from ..models.sequence_details_dto import SequenceDetailsDto
        from ..models.sequence_revision_details_dto import SequenceRevisionDetailsDto
        from ..models.show_details_dto import ShowDetailsDto

        d = src_dict.copy()
        _show = d.pop("show")
        show: Optional[ShowDetailsDto]
        if _show is None:
            show = None
        else:
            show = ShowDetailsDto.from_dict(_show)

        _episode = d.pop("episode")
        episode: Optional[EpisodeDetailsDto]
        if _episode is None:
            episode = None
        else:
            episode = EpisodeDetailsDto.from_dict(_episode)

        _sequence = d.pop("sequence")
        sequence: Optional[SequenceDetailsDto]
        if _sequence is None:
            sequence = None
        else:
            sequence = SequenceDetailsDto.from_dict(_sequence)

        _sequence_revision = d.pop("sequenceRevision")
        sequence_revision: Optional[SequenceRevisionDetailsDto]
        if _sequence_revision is None:
            sequence_revision = None
        else:
            sequence_revision = SequenceRevisionDetailsDto.from_dict(_sequence_revision)

        project_details_dto = cls(
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )

        project_details_dto.additional_properties = d
        return project_details_dto

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
