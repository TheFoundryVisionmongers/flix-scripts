from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.source_file_preview_mode import SourceFilePreviewMode
from ..models.source_file_type import SourceFileType

T = TypeVar("T", bound="PanelRequestSourceFile")


@_attrs_define
class PanelRequestSourceFile:
    """
    Attributes:
        path (str): The path to the source file. Example: /path/to/source/file.psd.
        preview_mode (SourceFilePreviewMode): The mode to use to generate the source file preview. Example: source_file.
        source_file_type (SourceFileType): The extension type that the source file is coming from. Example: Sketch.
    """

    path: str
    preview_mode: SourceFilePreviewMode
    source_file_type: SourceFileType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        preview_mode = self.preview_mode.value

        source_file_type = self.source_file_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "previewMode": preview_mode,
                "sourceFileType": source_file_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        preview_mode = SourceFilePreviewMode(d.pop("previewMode"))

        source_file_type = SourceFileType(d.pop("sourceFileType"))

        panel_request_source_file = cls(
            path=path,
            preview_mode=preview_mode,
            source_file_type=source_file_type,
        )

        panel_request_source_file.additional_properties = d
        return panel_request_source_file

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
