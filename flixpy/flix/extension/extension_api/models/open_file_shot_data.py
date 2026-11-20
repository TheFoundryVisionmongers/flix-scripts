from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OpenFileShotData")


@_attrs_define
class OpenFileShotData:
    """
    Attributes:
        id (int):
        index (int):
        start_panel_index (int):
        end_panel_index (int):
        name (str):
    """

    id: int
    index: int
    start_panel_index: int
    end_panel_index: int
    name: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        index = self.index
        start_panel_index = self.start_panel_index
        end_panel_index = self.end_panel_index
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "index": index,
                "startPanelIndex": start_panel_index,
                "endPanelIndex": end_panel_index,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        index = d.pop("index")

        start_panel_index = d.pop("startPanelIndex")

        end_panel_index = d.pop("endPanelIndex")

        name = d.pop("name")

        open_file_shot_data = cls(
            id=id,
            index=index,
            start_panel_index=start_panel_index,
            end_panel_index=end_panel_index,
            name=name,
        )

        open_file_shot_data.additional_properties = d
        return open_file_shot_data

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
