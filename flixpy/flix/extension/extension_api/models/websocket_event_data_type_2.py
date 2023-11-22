from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.websocket_event_data_type_2_type import WebsocketEventDataType2Type

if TYPE_CHECKING:
    from ..models.open_event import OpenEvent
    from ..models.open_source_file_event import OpenSourceFileEvent


T = TypeVar("T", bound="WebsocketEventDataType2")


@_attrs_define
class WebsocketEventDataType2:
    """
    Attributes:
        type (WebsocketEventDataType2Type):
        data (Union['OpenEvent', 'OpenSourceFileEvent']):
    """

    type: WebsocketEventDataType2Type
    data: Union["OpenEvent", "OpenSourceFileEvent"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.open_event import OpenEvent

        type = self.type.value

        data: Dict[str, Any]

        if isinstance(self.data, OpenEvent):
            data = self.data.to_dict()

        else:
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
        from ..models.open_event import OpenEvent
        from ..models.open_source_file_event import OpenSourceFileEvent

        d = src_dict.copy()
        type = WebsocketEventDataType2Type(d.pop("type"))

        def _parse_data(data: object) -> Union["OpenEvent", "OpenSourceFileEvent"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = OpenEvent.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_1 = OpenSourceFileEvent.from_dict(data)

            return data_type_1

        data = _parse_data(d.pop("data"))

        websocket_event_data_type_2 = cls(
            type=type,
            data=data,
        )

        websocket_event_data_type_2.additional_properties = d
        return websocket_event_data_type_2

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
