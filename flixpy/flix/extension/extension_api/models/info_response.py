from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast






T = TypeVar("T", bound="InfoResponse")



@_attrs_define
class InfoResponse:
    """ 
        Attributes:
            flix_version (str): Current Flix Client version.
            supported_api_versions (list[str]): Supported GRC API versions.
     """

    flix_version: str
    supported_api_versions: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        flix_version = self.flix_version

        supported_api_versions = self.supported_api_versions




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "flixVersion": flix_version,
            "supportedApiVersions": supported_api_versions,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        flix_version = d.pop("flixVersion")

        supported_api_versions = cast(list[str], d.pop("supportedApiVersions"))


        info_response = cls(
            flix_version=flix_version,
            supported_api_versions=supported_api_versions,
        )


        info_response.additional_properties = d
        return info_response

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
