from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ProjectDetailsMetadataDtoSequence")



@_attrs_define
class ProjectDetailsMetadataDtoSequence:
    """ Arbitrary key-value metadata to merge into the entity. Each value must be a string, or `null` to delete that key.

    **Note:** Keys in this dictionary are **case-sensitive**.

    Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).

        Example:
            {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}

     """

    additional_properties: dict[str, str] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_details_metadata_dto_sequence = cls(
        )


        project_details_metadata_dto_sequence.additional_properties = d
        return project_details_metadata_dto_sequence

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> str:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
