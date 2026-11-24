from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="ProjectIdsDto")



@_attrs_define
class ProjectIdsDto:
    """ 
        Attributes:
            show_id (int | Unset):
            episode_id (int | Unset):
            sequence_id (int | Unset):
            sequence_revision_id (int | Unset):
     """

    show_id: int | Unset = UNSET
    episode_id: int | Unset = UNSET
    sequence_id: int | Unset = UNSET
    sequence_revision_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        show_id = self.show_id

        episode_id = self.episode_id

        sequence_id = self.sequence_id

        sequence_revision_id = self.sequence_revision_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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
