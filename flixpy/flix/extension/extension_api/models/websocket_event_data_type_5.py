from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.websocket_event_data_type_5_type import WebsocketEventDataType5Type
from typing import cast

if TYPE_CHECKING:
  from ..models.version_event import VersionEvent





T = TypeVar("T", bound="WebsocketEventDataType5")



@_attrs_define
class WebsocketEventDataType5:
    """ 
        Attributes:
            type_ (WebsocketEventDataType5Type):
            data (VersionEvent):
     """

    type_: WebsocketEventDataType5Type
    data: VersionEvent
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.version_event import VersionEvent # noqa: PLC0415
        type_ = self.type_.value

        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.version_event import VersionEvent # noqa: PLC0415
        d = dict(src_dict)
        type_ = WebsocketEventDataType5Type(d.pop("type"))




        data = VersionEvent.from_dict(d.pop("data"))




        websocket_event_data_type_5 = cls(
            type_=type_,
            data=data,
        )


        websocket_event_data_type_5.additional_properties = d
        return websocket_event_data_type_5

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
