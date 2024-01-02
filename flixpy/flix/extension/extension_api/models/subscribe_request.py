from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.client_event_type import ClientEventType

T = TypeVar("T", bound="SubscribeRequest")


@_attrs_define
class SubscribeRequest:
    """
    Attributes:
        event_types (List[ClientEventType]):
    """

    event_types: List[ClientEventType]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        event_types = []
        for event_types_item_data in self.event_types:
            event_types_item = event_types_item_data.value

            event_types.append(event_types_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventTypes": event_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        event_types = []
        _event_types = d.pop("eventTypes")
        for event_types_item_data in _event_types:
            event_types_item = ClientEventType(event_types_item_data)

            event_types.append(event_types_item)

        subscribe_request = cls(
            event_types=event_types,
        )

        subscribe_request.additional_properties = d
        return subscribe_request

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
