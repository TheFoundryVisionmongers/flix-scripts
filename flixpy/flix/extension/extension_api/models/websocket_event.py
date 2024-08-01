from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.websocket_event_data_type_0 import WebsocketEventDataType0
    from ..models.websocket_event_data_type_1 import WebsocketEventDataType1
    from ..models.websocket_event_data_type_2 import WebsocketEventDataType2
    from ..models.websocket_event_data_type_3 import WebsocketEventDataType3
    from ..models.websocket_event_data_type_4 import WebsocketEventDataType4
    from ..models.websocket_event_data_type_5 import WebsocketEventDataType5
    from ..models.websocket_event_data_type_6 import WebsocketEventDataType6


T = TypeVar("T", bound="WebsocketEvent")


@_attrs_define
class WebsocketEvent:
    """
    Attributes:
        data (Union['WebsocketEventDataType0', 'WebsocketEventDataType1', 'WebsocketEventDataType2',
            'WebsocketEventDataType3', 'WebsocketEventDataType4', 'WebsocketEventDataType5', 'WebsocketEventDataType6']):
    """

    data: Union[
        "WebsocketEventDataType0",
        "WebsocketEventDataType1",
        "WebsocketEventDataType2",
        "WebsocketEventDataType3",
        "WebsocketEventDataType4",
        "WebsocketEventDataType5",
        "WebsocketEventDataType6",
    ]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.websocket_event_data_type_0 import WebsocketEventDataType0
        from ..models.websocket_event_data_type_1 import WebsocketEventDataType1
        from ..models.websocket_event_data_type_2 import WebsocketEventDataType2
        from ..models.websocket_event_data_type_3 import WebsocketEventDataType3
        from ..models.websocket_event_data_type_4 import WebsocketEventDataType4
        from ..models.websocket_event_data_type_5 import WebsocketEventDataType5

        data: Dict[str, Any]

        if isinstance(self.data, WebsocketEventDataType0):
            data = self.data.to_dict()

        elif isinstance(self.data, WebsocketEventDataType1):
            data = self.data.to_dict()

        elif isinstance(self.data, WebsocketEventDataType2):
            data = self.data.to_dict()

        elif isinstance(self.data, WebsocketEventDataType3):
            data = self.data.to_dict()

        elif isinstance(self.data, WebsocketEventDataType4):
            data = self.data.to_dict()

        elif isinstance(self.data, WebsocketEventDataType5):
            data = self.data.to_dict()

        else:
            data = self.data.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.websocket_event_data_type_0 import WebsocketEventDataType0
        from ..models.websocket_event_data_type_1 import WebsocketEventDataType1
        from ..models.websocket_event_data_type_2 import WebsocketEventDataType2
        from ..models.websocket_event_data_type_3 import WebsocketEventDataType3
        from ..models.websocket_event_data_type_4 import WebsocketEventDataType4
        from ..models.websocket_event_data_type_5 import WebsocketEventDataType5
        from ..models.websocket_event_data_type_6 import WebsocketEventDataType6

        d = src_dict.copy()

        def _parse_data(
            data: object,
        ) -> Union[
            "WebsocketEventDataType0",
            "WebsocketEventDataType1",
            "WebsocketEventDataType2",
            "WebsocketEventDataType3",
            "WebsocketEventDataType4",
            "WebsocketEventDataType5",
            "WebsocketEventDataType6",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = WebsocketEventDataType0.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = WebsocketEventDataType1.from_dict(data)

                return data_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_2 = WebsocketEventDataType2.from_dict(data)

                return data_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_3 = WebsocketEventDataType3.from_dict(data)

                return data_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_4 = WebsocketEventDataType4.from_dict(data)

                return data_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_5 = WebsocketEventDataType5.from_dict(data)

                return data_type_5
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_6 = WebsocketEventDataType6.from_dict(data)

            return data_type_6

        data = _parse_data(d.pop("data"))

        websocket_event = cls(
            data=data,
        )

        websocket_event.additional_properties = d
        return websocket_event

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
