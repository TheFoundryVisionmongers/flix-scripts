from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.extension_custom_action_type import ExtensionCustomActionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistrationRequestAction")


@_attrs_define
class RegistrationRequestAction:
    """
    Attributes:
        id (str): The unique identifier for this action.
        name (str): The user-friendly name for this action to be displayed in the UI.
        description (Union[Unset, str]): The user-friendly description for this action to be displayed in the UI.
        icon_svg (Union[Unset, str]): A simple SVG icon for this specific action when displayed in the UI.
        type (Union[Unset, ExtensionCustomActionType]):
    """

    id: str
    name: str
    description: Union[Unset, str] = UNSET
    icon_svg: Union[Unset, str] = UNSET
    type: Union[Unset, ExtensionCustomActionType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        description = self.description
        icon_svg = self.icon_svg
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if icon_svg is not UNSET:
            field_dict["iconSvg"] = icon_svg
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        icon_svg = d.pop("iconSvg", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, ExtensionCustomActionType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = ExtensionCustomActionType(_type)

        registration_request_action = cls(
            id=id,
            name=name,
            description=description,
            icon_svg=icon_svg,
            type=type,
        )

        registration_request_action.additional_properties = d
        return registration_request_action

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
