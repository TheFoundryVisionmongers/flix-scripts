from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.sse_event_data_type_0 import SSEEventDataType0
    from ..models.sse_event_data_type_1 import SSEEventDataType1
    from ..models.sse_event_data_type_2 import SSEEventDataType2
    from ..models.sse_event_data_type_3 import SSEEventDataType3
    from ..models.sse_event_data_type_4 import SSEEventDataType4
    from ..models.sse_event_data_type_5 import SSEEventDataType5
    from ..models.sse_event_data_type_6 import SSEEventDataType6


T = TypeVar("T", bound="SSEEvent")


@_attrs_define
class SSEEvent:
    """
    Attributes:
        data (Union['SSEEventDataType0', 'SSEEventDataType1', 'SSEEventDataType2', 'SSEEventDataType3',
            'SSEEventDataType4', 'SSEEventDataType5', 'SSEEventDataType6']):
    """

    data: Union[
        "SSEEventDataType0",
        "SSEEventDataType1",
        "SSEEventDataType2",
        "SSEEventDataType3",
        "SSEEventDataType4",
        "SSEEventDataType5",
        "SSEEventDataType6",
    ]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.sse_event_data_type_0 import SSEEventDataType0
        from ..models.sse_event_data_type_1 import SSEEventDataType1
        from ..models.sse_event_data_type_2 import SSEEventDataType2
        from ..models.sse_event_data_type_3 import SSEEventDataType3
        from ..models.sse_event_data_type_4 import SSEEventDataType4
        from ..models.sse_event_data_type_5 import SSEEventDataType5

        data: Dict[str, Any]

        if isinstance(self.data, SSEEventDataType0):
            data = self.data.to_dict()

        elif isinstance(self.data, SSEEventDataType1):
            data = self.data.to_dict()

        elif isinstance(self.data, SSEEventDataType2):
            data = self.data.to_dict()

        elif isinstance(self.data, SSEEventDataType3):
            data = self.data.to_dict()

        elif isinstance(self.data, SSEEventDataType4):
            data = self.data.to_dict()

        elif isinstance(self.data, SSEEventDataType5):
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
        from ..models.sse_event_data_type_0 import SSEEventDataType0
        from ..models.sse_event_data_type_1 import SSEEventDataType1
        from ..models.sse_event_data_type_2 import SSEEventDataType2
        from ..models.sse_event_data_type_3 import SSEEventDataType3
        from ..models.sse_event_data_type_4 import SSEEventDataType4
        from ..models.sse_event_data_type_5 import SSEEventDataType5
        from ..models.sse_event_data_type_6 import SSEEventDataType6

        d = src_dict.copy()

        def _parse_data(
            data: object,
        ) -> Union[
            "SSEEventDataType0",
            "SSEEventDataType1",
            "SSEEventDataType2",
            "SSEEventDataType3",
            "SSEEventDataType4",
            "SSEEventDataType5",
            "SSEEventDataType6",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = SSEEventDataType0.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = SSEEventDataType1.from_dict(data)

                return data_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_2 = SSEEventDataType2.from_dict(data)

                return data_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_3 = SSEEventDataType3.from_dict(data)

                return data_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_4 = SSEEventDataType4.from_dict(data)

                return data_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_5 = SSEEventDataType5.from_dict(data)

                return data_type_5
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_6 = SSEEventDataType6.from_dict(data)

            return data_type_6

        data = _parse_data(d.pop("data"))

        sse_event = cls(
            data=data,
        )

        sse_event.additional_properties = d
        return sse_event

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
