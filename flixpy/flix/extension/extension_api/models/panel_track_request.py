from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PanelTrackRequest")


@_attrs_define
class PanelTrackRequest:
    """
    Attributes:
        show_id (int): The ID of the show the tracked panel belongs to. Example: 1.
        sequence_id (int): The ID of the sequence the tracked panel belongs to. Example: 12.
        panel_id (int): The ID of the panel that is being tracked. Example: 1234.
    """

    show_id: int
    sequence_id: int
    panel_id: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        show_id = self.show_id
        sequence_id = self.sequence_id
        panel_id = self.panel_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "showId": show_id,
                "sequenceId": sequence_id,
                "panelId": panel_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        show_id = d.pop("showId")

        sequence_id = d.pop("sequenceId")

        panel_id = d.pop("panelId")

        panel_track_request = cls(
            show_id=show_id,
            sequence_id=sequence_id,
            panel_id=panel_id,
        )

        panel_track_request.additional_properties = d
        return panel_track_request

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
