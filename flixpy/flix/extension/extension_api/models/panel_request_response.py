from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="PanelRequestResponse")



@_attrs_define
class PanelRequestResponse:
    """ 
        Attributes:
            action_id (int): The ID of the action scheduled by the panel request.
            message (str): A summary message of the scheduled panel action.
     """

    action_id: int
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        action_id = self.action_id

        message = self.message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "actionId": action_id,
            "message": message,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_id = d.pop("actionId")

        message = d.pop("message")

        panel_request_response = cls(
            action_id=action_id,
            message=message,
        )


        panel_request_response.additional_properties = d
        return panel_request_response

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
