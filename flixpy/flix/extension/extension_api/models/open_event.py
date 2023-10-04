from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.extension_open_file_panel_data import ExtensionOpenFilePanelData
    from ..models.project_ids import ProjectIds


T = TypeVar("T", bound="OpenEvent")


@_attrs_define
class OpenEvent:
    """
    Attributes:
        project (ProjectIds):
        panels (List['ExtensionOpenFilePanelData']):
    """

    project: "ProjectIds"
    panels: List["ExtensionOpenFilePanelData"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project.to_dict()

        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()

            panels.append(panels_item)

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

        panels = []
        _panels = d.pop("panels")
        for panels_item_data in _panels:
            panels_item = ExtensionOpenFilePanelData.from_dict(panels_item_data)

            panels.append(panels_item)

        open_event = cls(
            project=project,
            panels=panels,
        )

        open_event.additional_properties = d
        return open_event

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
