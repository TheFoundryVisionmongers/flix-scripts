from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.panel_request_item import PanelRequestItem
  from ..models.panel_request_source_file import PanelRequestSourceFile





T = TypeVar("T", bound="FullPanelRequest")



@_attrs_define
class FullPanelRequest:
    """ 
        Attributes:
            panels (list[PanelRequestItem]): The file paths to upload and the IDs of the panels they should update.
            origin (str): The origin of the incoming panel artwork. Example: Photoshop.
            start_index (int | Unset): (Optional) The index from which to insert or update panels. Defaults to currently
                selected panel. Example: 3.
            source_file (PanelRequestSourceFile | Unset):
            skip_panel_reuse (bool | Unset): Whether panel reuse checks should be skipped. Will always skip if true, and
                always do reuse checks if false. Example: True.
     """

    panels: list[PanelRequestItem]
    origin: str
    start_index: int | Unset = UNSET
    source_file: PanelRequestSourceFile | Unset = UNSET
    skip_panel_reuse: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.panel_request_item import PanelRequestItem # noqa: PLC0415
        from ..models.panel_request_source_file import PanelRequestSourceFile # noqa: PLC0415
        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()
            panels.append(panels_item)



        origin = self.origin

        start_index = self.start_index

        source_file: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_file, Unset):
            source_file = self.source_file.to_dict()

        skip_panel_reuse = self.skip_panel_reuse


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "panels": panels,
            "origin": origin,
        })
        if start_index is not UNSET:
            field_dict["startIndex"] = start_index
        if source_file is not UNSET:
            field_dict["sourceFile"] = source_file
        if skip_panel_reuse is not UNSET:
            field_dict["skipPanelReuse"] = skip_panel_reuse

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.panel_request_item import PanelRequestItem # noqa: PLC0415
        from ..models.panel_request_source_file import PanelRequestSourceFile # noqa: PLC0415
        d = dict(src_dict)
        panels = []
        _panels = d.pop("panels")
        for panels_item_data in (_panels):
            panels_item = PanelRequestItem.from_dict(panels_item_data)



            panels.append(panels_item)


        origin = d.pop("origin")

        start_index = d.pop("startIndex", UNSET)

        _source_file = d.pop("sourceFile", UNSET)
        source_file: PanelRequestSourceFile | Unset
        if isinstance(_source_file,  Unset) or _source_file is None:
            source_file = UNSET
        else:
            source_file = PanelRequestSourceFile.from_dict(_source_file)




        skip_panel_reuse = d.pop("skipPanelReuse", UNSET)

        full_panel_request = cls(
            panels=panels,
            origin=origin,
            start_index=start_index,
            source_file=source_file,
            skip_panel_reuse=skip_panel_reuse,
        )


        full_panel_request.additional_properties = d
        return full_panel_request

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
