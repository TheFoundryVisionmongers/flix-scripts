from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="PanelSelectionResponse")



@_attrs_define
class PanelSelectionResponse:
    """ 
        Attributes:
            id (int): The ID of the selected panel.
            revision_id (int): The revision of the selected panel.
            index (int): The current index in the panel browser of the selected panel.
     """

    id: int
    revision_id: int
    index: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        revision_id = self.revision_id

        index = self.index


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "revisionId": revision_id,
            "index": index,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        revision_id = d.pop("revisionId")

        index = d.pop("index")

        panel_selection_response = cls(
            id=id,
            revision_id=revision_id,
            index=index,
        )


        panel_selection_response.additional_properties = d
        return panel_selection_response

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
