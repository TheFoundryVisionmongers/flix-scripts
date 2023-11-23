from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RevisionStatus")


@_attrs_define
class RevisionStatus:
    """
    Attributes:
        can_save (bool):
        can_publish (bool):
        can_export (bool):
        selected_panels (List[int]):
    """

    can_save: bool
    can_publish: bool
    can_export: bool
    selected_panels: List[int]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        can_save = self.can_save
        can_publish = self.can_publish
        can_export = self.can_export
        selected_panels = self.selected_panels

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "canSave": can_save,
                "canPublish": can_publish,
                "canExport": can_export,
                "selectedPanels": selected_panels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        can_save = d.pop("canSave")

        can_publish = d.pop("canPublish")

        can_export = d.pop("canExport")

        selected_panels = cast(List[int], d.pop("selectedPanels"))

        revision_status = cls(
            can_save=can_save,
            can_publish=can_publish,
            can_export=can_export,
            selected_panels=selected_panels,
        )

        revision_status.additional_properties = d
        return revision_status

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
