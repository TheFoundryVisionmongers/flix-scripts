from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.extension_source_file_data import ExtensionSourceFileData


T = TypeVar("T", bound="OpenSourceFileEvent")


@_attrs_define
class OpenSourceFileEvent:
    """
    Attributes:
        source_file (ExtensionSourceFileData):
    """

    source_file: "ExtensionSourceFileData"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source_file = self.source_file.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceFile": source_file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.extension_source_file_data import ExtensionSourceFileData

        d = src_dict.copy()
        source_file = ExtensionSourceFileData.from_dict(d.pop("sourceFile"))

        open_source_file_event = cls(
            source_file=source_file,
        )

        open_source_file_event.additional_properties = d
        return open_source_file_event

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
