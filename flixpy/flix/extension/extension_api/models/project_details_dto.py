from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

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
        show (ShowDetailsDto):
        episode (EpisodeDetailsDto):
        sequence (SequenceDetailsDto):
        sequence_revision (SequenceRevisionDetailsDto):
    """

    show: "ShowDetailsDto"
    episode: "EpisodeDetailsDto"
    sequence: "SequenceDetailsDto"
    sequence_revision: "SequenceRevisionDetailsDto"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        show = self.show.to_dict()

        episode = self.episode.to_dict()

        sequence = self.sequence.to_dict()

        sequence_revision = self.sequence_revision.to_dict()

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
        show = ShowDetailsDto.from_dict(d.pop("show"))

        episode = EpisodeDetailsDto.from_dict(d.pop("episode"))

        sequence = SequenceDetailsDto.from_dict(d.pop("sequence"))

        sequence_revision = SequenceRevisionDetailsDto.from_dict(
            d.pop("sequenceRevision")
        )

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
