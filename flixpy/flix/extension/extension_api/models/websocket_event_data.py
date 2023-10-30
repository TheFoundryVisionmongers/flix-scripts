from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_type import EventType

if TYPE_CHECKING:
    from ..models.action_event import ActionEvent
    from ..models.open_event import OpenEvent
    from ..models.open_source_file_event import OpenSourceFileEvent
    from ..models.ping_event import PingEvent
    from ..models.project_details_dto import ProjectDetailsDto
    from ..models.unknown_event import UnknownEvent


T = TypeVar("T", bound="WebsocketEventData")


@_attrs_define
class WebsocketEventData:
    """
    Attributes:
        type (EventType):
        data (Union['ActionEvent', 'OpenEvent', 'OpenSourceFileEvent', 'PingEvent', 'ProjectDetailsDto',
            'UnknownEvent']):
    """

    type: EventType
    data: Union["ActionEvent", "OpenEvent", "OpenSourceFileEvent", "PingEvent", "ProjectDetailsDto", "UnknownEvent"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.action_event import ActionEvent
        from ..models.open_event import OpenEvent
        from ..models.open_source_file_event import OpenSourceFileEvent
        from ..models.ping_event import PingEvent
        from ..models.project_details_dto import ProjectDetailsDto

        type = self.type.value

        data: Dict[str, Any]

        if isinstance(self.data, ActionEvent):
            data = self.data.to_dict()

        elif isinstance(self.data, ProjectDetailsDto):
            data = self.data.to_dict()

        elif isinstance(self.data, OpenEvent):
            data = self.data.to_dict()

        elif isinstance(self.data, OpenSourceFileEvent):
            data = self.data.to_dict()

        elif isinstance(self.data, PingEvent):
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
        from ..models.action_event import ActionEvent
        from ..models.open_event import OpenEvent
        from ..models.open_source_file_event import OpenSourceFileEvent
        from ..models.ping_event import PingEvent
        from ..models.project_details_dto import ProjectDetailsDto
        from ..models.unknown_event import UnknownEvent

        d = src_dict.copy()
        type = EventType(d.pop("type"))

        def _parse_data(
            data: object,
        ) -> Union["ActionEvent", "OpenEvent", "OpenSourceFileEvent", "PingEvent", "ProjectDetailsDto", "UnknownEvent"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = ActionEvent.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = ProjectDetailsDto.from_dict(data)

                return data_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_2 = OpenEvent.from_dict(data)

                return data_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_3 = OpenSourceFileEvent.from_dict(data)

                return data_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_4 = PingEvent.from_dict(data)

                return data_type_4
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_5 = UnknownEvent.from_dict(data)

            return data_type_5

        data = _parse_data(d.pop("data"))

        websocket_event_data = cls(
            type=type,
            data=data,
        )

        websocket_event_data.additional_properties = d
        return websocket_event_data

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
