from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectIdsDto")


@_attrs_define
class ProjectIdsDto:
    """
    Attributes:
        show_id (Union[Unset, int]):
        episode_id (Union[Unset, int]):
        sequence_id (Union[Unset, int]):
        sequence_revision_id (Union[Unset, int]):
    """

    show_id: Union[Unset, int] = UNSET
    episode_id: Union[Unset, int] = UNSET
    sequence_id: Union[Unset, int] = UNSET
    sequence_revision_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        show_id = self.show_id
        episode_id = self.episode_id
        sequence_id = self.sequence_id
        sequence_revision_id = self.sequence_revision_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_id is not UNSET:
            field_dict["showId"] = show_id
        if episode_id is not UNSET:
            field_dict["episodeId"] = episode_id
        if sequence_id is not UNSET:
            field_dict["sequenceId"] = sequence_id
        if sequence_revision_id is not UNSET:
            field_dict["sequenceRevisionId"] = sequence_revision_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        show_id = d.pop("showId", UNSET)

        episode_id = d.pop("episodeId", UNSET)

        sequence_id = d.pop("sequenceId", UNSET)

        sequence_revision_id = d.pop("sequenceRevisionId", UNSET)

        project_ids_dto = cls(
            show_id=show_id,
            episode_id=episode_id,
            sequence_id=sequence_id,
            sequence_revision_id=sequence_revision_id,
        )

        project_ids_dto.additional_properties = d
        return project_ids_dto

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
