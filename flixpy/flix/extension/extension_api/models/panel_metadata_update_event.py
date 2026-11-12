from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.updated_panel_metadata_dto import UpdatedPanelMetadataDto


T = TypeVar("T", bound="PanelMetadataUpdateEvent")


@_attrs_define
class PanelMetadataUpdateEvent:
    """
    Attributes:
        panels (List['UpdatedPanelMetadataDto']):
    """

    panels: List["UpdatedPanelMetadataDto"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        panels = []
        for panels_item_data in self.panels:
            panels_item = panels_item_data.to_dict()

            panels.append(panels_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "panels": panels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.updated_panel_metadata_dto import UpdatedPanelMetadataDto

        d = src_dict.copy()
        panels = []
        _panels = d.pop("panels")
        for panels_item_data in _panels:
            panels_item = UpdatedPanelMetadataDto.from_dict(panels_item_data)

            panels.append(panels_item)

        panel_metadata_update_event = cls(
            panels=panels,
        )

        panel_metadata_update_event.additional_properties = d
        return panel_metadata_update_event

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
