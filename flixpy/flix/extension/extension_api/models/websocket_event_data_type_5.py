from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.websocket_event_data_type_5_type import WebsocketEventDataType5Type

if TYPE_CHECKING:
    from ..models.version_event import VersionEvent


T = TypeVar("T", bound="WebsocketEventDataType5")


@_attrs_define
class WebsocketEventDataType5:
    """
    Attributes:
        type (WebsocketEventDataType5Type):
        data (VersionEvent):
    """

    type: WebsocketEventDataType5Type
    data: "VersionEvent"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        data = self.data.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.version_event import VersionEvent

        d = src_dict.copy()
        type = WebsocketEventDataType5Type(d.pop("type"))

        data = VersionEvent.from_dict(d.pop("data"))

        websocket_event_data_type_5 = cls(
            type=type,
            data=data,
        )

        websocket_event_data_type_5.additional_properties = d
        return websocket_event_data_type_5

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
