from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.action_registration_type import ActionRegistrationType
from ..types import UNSET, Unset






T = TypeVar("T", bound="ActionRegistration")



@_attrs_define
class ActionRegistration:
    """ 
        Attributes:
            id (str): Unique identifier for this action.
            name (str): The user-friendly name for this action to be displayed in the UI.
            type_ (ActionRegistrationType | Unset): Context/location of the action within the application.
                For now only PanelBrowserAction is supported and will be set regardless of provided value.
            description (str | Unset): The user-friendly description for this action to be displayed in the UI.
            icon_svg (str | Unset): A simple SVG icon for this specific action when displayed in the UI.
                This value will be processed upon registration and may display incorrectly if unsupported SVG features are used.
     """

    id: str
    name: str
    type_: ActionRegistrationType | Unset = UNSET
    description: str | Unset = UNSET
    icon_svg: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        description = self.description

        icon_svg = self.icon_svg


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if description is not UNSET:
            field_dict["description"] = description
        if icon_svg is not UNSET:
            field_dict["iconSvg"] = icon_svg

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        _type_ = d.pop("type", UNSET)
        type_: ActionRegistrationType | Unset
        if isinstance(_type_,  Unset) or _type_ is None:
            type_ = UNSET
        else:
            type_ = ActionRegistrationType(_type_)




        description = d.pop("description", UNSET)

        icon_svg = d.pop("iconSvg", UNSET)

        action_registration = cls(
            id=id,
            name=name,
            type_=type_,
            description=description,
            icon_svg=icon_svg,
        )


        action_registration.additional_properties = d
        return action_registration

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
