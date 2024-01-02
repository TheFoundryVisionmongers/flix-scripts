from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.panel_request_item import PanelRequestItem
    from ..models.panel_request_source_file import PanelRequestSourceFile


T = TypeVar("T", bound="FullPanelRequest")


@_attrs_define
class FullPanelRequest:
    """
    Attributes:
        panels (List['PanelRequestItem']): The file paths to upload and the panel IDs they should link to
        origin (str):
        start_index (Union[Unset, int]): the index at which to insert the created panels Example: 3.
        source_file (Union[Unset, PanelRequestSourceFile]):
    """

    panels: List["PanelRequestItem"]
    origin: str
    start_index: Union[Unset, int] = UNSET
    source_file: Union[Unset, "PanelRequestSourceFile"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()

            panels.append(panels_item)

        origin = self.origin
        start_index = self.start_index
        source_file: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.source_file, Unset):
            source_file = self.source_file.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "panels": panels,
                "origin": origin,
            }
        )
        if start_index is not UNSET:
            field_dict["startIndex"] = start_index
        if source_file is not UNSET:
            field_dict["sourceFile"] = source_file

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_request_item import PanelRequestItem
        from ..models.panel_request_source_file import PanelRequestSourceFile

        d = src_dict.copy()
        panels = []
        _panels = d.pop("panels")
        for panels_item_data in _panels:
            panels_item = PanelRequestItem.from_dict(panels_item_data)

            panels.append(panels_item)

        origin = d.pop("origin")

        start_index = d.pop("startIndex", UNSET)

        _source_file = d.pop("sourceFile", UNSET)
        source_file: Union[Unset, PanelRequestSourceFile]
        if isinstance(_source_file, Unset):
            source_file = UNSET
        else:
            source_file = PanelRequestSourceFile.from_dict(_source_file)

        full_panel_request = cls(
            panels=panels,
            origin=origin,
            start_index=start_index,
            source_file=source_file,
        )

        full_panel_request.additional_properties = d
        return full_panel_request

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
