from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RevisionStatusResponse")


@_attrs_define
class RevisionStatusResponse:
    """
    Attributes:
        selected_panels (List[int]): A list of the currently selected panels
        can_save (bool): Whether the current revision can be saved
        can_publish (bool): Whether the user has permission to publish the current revision
        can_export (bool): Whether the user has permission to export files from the current revision
    """

    selected_panels: List[int]
    can_save: bool
    can_publish: bool
    can_export: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selected_panels = self.selected_panels

        can_save = self.can_save
        can_publish = self.can_publish
        can_export = self.can_export

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "selectedPanels": selected_panels,
                "canSave": can_save,
                "canPublish": can_publish,
                "canExport": can_export,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        selected_panels = cast(List[int], d.pop("selectedPanels"))

        can_save = d.pop("canSave")

        can_publish = d.pop("canPublish")

        can_export = d.pop("canExport")

        revision_status_response = cls(
            selected_panels=selected_panels,
            can_save=can_save,
            can_publish=can_publish,
            can_export=can_export,
        )

        revision_status_response.additional_properties = d
        return revision_status_response

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
