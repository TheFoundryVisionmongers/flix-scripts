from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.panel_request_item import PanelRequestItem


T = TypeVar("T", bound="FullPanelAnnotateRequest")


@_attrs_define
class FullPanelAnnotateRequest:
    """
    Attributes:
        start_index (int): the index at which to insert the created panels
        panels (List['PanelRequestItem']): The file paths to upload and the panel IDs they should link to
        origin (str):
    """

    start_index: int
    panels: List["PanelRequestItem"]
    origin: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start_index = self.start_index
        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()

            panels.append(panels_item)

        origin = self.origin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startIndex": start_index,
                "panels": panels,
                "origin": origin,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_request_item import PanelRequestItem

        d = src_dict.copy()
        start_index = d.pop("startIndex")

        panels = []
        _panels = d.pop("panels")
        for panels_item_data in _panels:
            panels_item = PanelRequestItem.from_dict(panels_item_data)

            panels.append(panels_item)

        origin = d.pop("origin")

        full_panel_annotate_request = cls(
            start_index=start_index,
            panels=panels,
            origin=origin,
        )

        full_panel_annotate_request.additional_properties = d
        return full_panel_annotate_request

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
