from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_file_panel_data import OpenFilePanelData
    from ..models.open_file_shot_data import OpenFileShotData
    from ..models.project_ids_dto import ProjectIdsDto
    from ..models.ps_configuration import PsConfiguration


T = TypeVar("T", bound="OpenFileEvent")


@_attrs_define
class OpenFileEvent:
    """
    Attributes:
        project (ProjectIdsDto):
        panels (List['OpenFilePanelData']):
        shots (List['OpenFileShotData']):
        sketching_tool_configuration (Union[Unset, PsConfiguration]):
        action_id (Union[Unset, str]):
    """

    project: "ProjectIdsDto"
    panels: List["OpenFilePanelData"]
    shots: List["OpenFileShotData"]
    sketching_tool_configuration: Union[Unset, "PsConfiguration"] = UNSET
    action_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project.to_dict()

        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()

            panels.append(panels_item)

        shots = []
        for shots_item_data in self.shots:
            shots_item = shots_item_data.to_dict()

            shots.append(shots_item)

        sketching_tool_configuration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.sketching_tool_configuration, Unset):
            sketching_tool_configuration = self.sketching_tool_configuration.to_dict()

        action_id = self.action_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "panels": panels,
                "shots": shots,
            }
        )
        if sketching_tool_configuration is not UNSET:
            field_dict["sketchingToolConfiguration"] = sketching_tool_configuration
        if action_id is not UNSET:
            field_dict["actionId"] = action_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.open_file_panel_data import OpenFilePanelData
        from ..models.open_file_shot_data import OpenFileShotData
        from ..models.project_ids_dto import ProjectIdsDto
        from ..models.ps_configuration import PsConfiguration

        d = src_dict.copy()
        project = ProjectIdsDto.from_dict(d.pop("project"))

        panels = []
        _panels = d.pop("panels")
        for panels_item_data in _panels:
            panels_item = OpenFilePanelData.from_dict(panels_item_data)

            panels.append(panels_item)

        shots = []
        _shots = d.pop("shots")
        for shots_item_data in _shots:
            shots_item = OpenFileShotData.from_dict(shots_item_data)

            shots.append(shots_item)

        _sketching_tool_configuration = d.pop("sketchingToolConfiguration", UNSET)
        sketching_tool_configuration: Union[Unset, PsConfiguration]
        if isinstance(_sketching_tool_configuration, Unset):
            sketching_tool_configuration = UNSET
        else:
            sketching_tool_configuration = PsConfiguration.from_dict(
                _sketching_tool_configuration
            )

        action_id = d.pop("actionId", UNSET)

        open_file_event = cls(
            project=project,
            panels=panels,
            shots=shots,
            sketching_tool_configuration=sketching_tool_configuration,
            action_id=action_id,
        )

        open_file_event.additional_properties = d
        return open_file_event

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
