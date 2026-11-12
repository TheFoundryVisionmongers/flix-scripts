from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.panel_selection_response import PanelSelectionResponse


T = TypeVar("T", bound="RevisionStatusResponse")


@_attrs_define
class RevisionStatusResponse:
    """
    Attributes:
        selected_panels (List[int]): A list of the currently selected panel IDs.
        can_save (bool): Whether the current revision can be saved.
        can_publish (bool): Whether the user has permission to publish the current revision.
        can_export (bool): Whether the user has permission to export files from the current revision.
        panel_selection (List['PanelSelectionResponse']): A list of the currently selected panel details, including ID.
    """

    selected_panels: List[int]
    can_save: bool
    can_publish: bool
    can_export: bool
    panel_selection: List["PanelSelectionResponse"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selected_panels = self.selected_panels

        can_save = self.can_save
        can_publish = self.can_publish
        can_export = self.can_export
        panel_selection = []
        for panel_selection_item_data in self.panel_selection:
            panel_selection_item = panel_selection_item_data.to_dict()

            panel_selection.append(panel_selection_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "selectedPanels": selected_panels,
                "canSave": can_save,
                "canPublish": can_publish,
                "canExport": can_export,
                "panelSelection": panel_selection,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_selection_response import PanelSelectionResponse

        d = src_dict.copy()
        selected_panels = cast(List[int], d.pop("selectedPanels"))

        can_save = d.pop("canSave")

        can_publish = d.pop("canPublish")

        can_export = d.pop("canExport")

        panel_selection = []
        _panel_selection = d.pop("panelSelection")
        for panel_selection_item_data in _panel_selection:
            panel_selection_item = PanelSelectionResponse.from_dict(
                panel_selection_item_data
            )

            panel_selection.append(panel_selection_item)

        revision_status_response = cls(
            selected_panels=selected_panels,
            can_save=can_save,
            can_publish=can_publish,
            can_export=can_export,
            panel_selection=panel_selection,
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
