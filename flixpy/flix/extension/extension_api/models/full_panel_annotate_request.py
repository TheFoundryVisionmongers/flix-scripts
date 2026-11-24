from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.panel_request_item import PanelRequestItem





T = TypeVar("T", bound="FullPanelAnnotateRequest")



@_attrs_define
class FullPanelAnnotateRequest:
    """ 
        Attributes:
            start_index (int): (Optional) The index from which to annotate panels. Defaults to currently selected panel.
                Example: 3.
            panels (list[PanelRequestItem]): The file paths to upload and the panel IDs that they should annotate.
            origin (str): The origin of the incoming annotation. Example: Photoshop.
     """

    start_index: int
    panels: list[PanelRequestItem]
    origin: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.panel_request_item import PanelRequestItem # noqa: PLC0415
        start_index = self.start_index

        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()
            panels.append(panels_item)



        origin = self.origin


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "startIndex": start_index,
            "panels": panels,
            "origin": origin,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.panel_request_item import PanelRequestItem # noqa: PLC0415
        d = dict(src_dict)
        start_index = d.pop("startIndex")

        panels = []
        _panels = d.pop("panels")
        for panels_item_data in (_panels):
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
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
