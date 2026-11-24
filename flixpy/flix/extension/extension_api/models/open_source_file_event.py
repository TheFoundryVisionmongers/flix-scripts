from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.open_source_file_data import OpenSourceFileData





T = TypeVar("T", bound="OpenSourceFileEvent")



@_attrs_define
class OpenSourceFileEvent:
    """ 
        Attributes:
            source_file (OpenSourceFileData):
     """

    source_file: OpenSourceFileData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        source_file = self.source_file.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "sourceFile": source_file,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        d = dict(src_dict)
        source_file = OpenSourceFileData.from_dict(d.pop("sourceFile"))




        open_source_file_event = cls(
            source_file=source_file,
        )


        open_source_file_event.additional_properties = d
        return open_source_file_event

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
