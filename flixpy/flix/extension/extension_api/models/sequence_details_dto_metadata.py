from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SequenceDetailsDtoMetadata")


@_attrs_define
class SequenceDetailsDtoMetadata:
    """Arbitrary key-value metadata to merge into the entity. Each value must be a string, or `null` to delete that key.

    **Note:** Keys in this dictionary are **case-sensitive**.

    Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).

        Example:
            {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}

    """

    additional_properties: Dict[str, str] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sequence_details_dto_metadata = cls()

        sequence_details_dto_metadata.additional_properties = d
        return sequence_details_dto_metadata

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> str:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
