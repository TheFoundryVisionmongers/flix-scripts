from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.extension_open_file_panel_data import ExtensionOpenFilePanelData
    from ..models.project_ids import ProjectIds


T = TypeVar("T", bound="ExtensionOpenFileData")


@_attrs_define
class ExtensionOpenFileData:
    """
    Attributes:
        project (ProjectIds):
        panels (ExtensionOpenFilePanelData):
    """

    project: "ProjectIds"
    panels: "ExtensionOpenFilePanelData"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project.to_dict()

        panels = self.panels.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "panels": panels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.extension_open_file_panel_data import ExtensionOpenFilePanelData
        from ..models.project_ids import ProjectIds

        d = src_dict.copy()
        project = ProjectIds.from_dict(d.pop("project"))

        panels = ExtensionOpenFilePanelData.from_dict(d.pop("panels"))

        extension_open_file_data = cls(
            project=project,
            panels=panels,
        )

        extension_open_file_data.additional_properties = d
        return extension_open_file_data

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
