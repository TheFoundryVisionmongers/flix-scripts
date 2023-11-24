from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ActionsInProgress")


@_attrs_define
class ActionsInProgress:
    """
    Attributes:
        is_saving (bool):
        is_publishing (bool):
        is_exporting (bool):
    """

    is_saving: bool
    is_publishing: bool
    is_exporting: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_saving = self.is_saving
        is_publishing = self.is_publishing
        is_exporting = self.is_exporting

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isSaving": is_saving,
                "isPublishing": is_publishing,
                "isExporting": is_exporting,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_saving = d.pop("isSaving")

        is_publishing = d.pop("isPublishing")

        is_exporting = d.pop("isExporting")

        actions_in_progress = cls(
            is_saving=is_saving,
            is_publishing=is_publishing,
            is_exporting=is_exporting,
        )

        actions_in_progress.additional_properties = d
        return actions_in_progress

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
