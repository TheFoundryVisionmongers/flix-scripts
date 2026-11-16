from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.custom_action_registration_request_type import CustomActionRegistrationRequestType
from ..types import UNSET, Unset






T = TypeVar("T", bound="CustomActionRegistrationRequest")



@_attrs_define
class CustomActionRegistrationRequest:
    """ 
        Attributes:
            id (str): Unique identifier for this action.
            name (str): The user-friendly name for this action to be displayed in the UI.
            description (str | Unset): The user-friendly description for this action to be displayed in the UI.
            icon_svg (str | Unset): A simple SVG icon for this specific action when displayed in the UI.
                This value will be processed upon registration and may display incorrectly if unsupported SVG features are used.
            type_ (CustomActionRegistrationRequestType | Unset): Context/location of the action within the application.
                For now only PanelBrowserAction is supported and will be set regardless of provided value.
     """

    id: str
    name: str
    description: str | Unset = UNSET
    icon_svg: str | Unset = UNSET
    type_: CustomActionRegistrationRequestType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        icon_svg = self.icon_svg

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if icon_svg is not UNSET:
            field_dict["iconSvg"] = icon_svg
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        icon_svg = d.pop("iconSvg", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: CustomActionRegistrationRequestType | Unset
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = CustomActionRegistrationRequestType(_type_)




        custom_action_registration_request = cls(
            id=id,
            name=name,
            description=description,
            icon_svg=icon_svg,
            type_=type_,
        )


        custom_action_registration_request.additional_properties = d
        return custom_action_registration_request

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
