from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="RegistrationDetails")



@_attrs_define
class RegistrationDetails:
    """ 
        Attributes:
            flix_id (int): The Flix-maintained identifier for this API consumer.
            name (str): The name for this API consumer.
            client_uid (str): The API client-specified identifier for this API consumer.
            version (str | Unset): The version of this API consumer (Optional).
            log_paths (list[str] | Unset): Paths to the location where the extension will write its logs for different
                versions of the app (Optional).
     """

    flix_id: int
    name: str
    client_uid: str
    version: str | Unset = UNSET
    log_paths: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        flix_id = self.flix_id

        name = self.name

        client_uid = self.client_uid

        version = self.version

        log_paths: list[str] | Unset = UNSET
        if not isinstance(self.log_paths, Unset):
            log_paths = self.log_paths




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "flixId": flix_id,
            "name": name,
            "clientUid": client_uid,
        })
        if version is not UNSET:
            field_dict["version"] = version
        if log_paths is not UNSET:
            field_dict["logPaths"] = log_paths

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        flix_id = d.pop("flixId")

        name = d.pop("name")

        client_uid = d.pop("clientUid")

        version = d.pop("version", UNSET)

        log_paths = cast(list[str], d.pop("logPaths", UNSET))


        registration_details = cls(
            flix_id=flix_id,
            name=name,
            client_uid=client_uid,
            version=version,
            log_paths=log_paths,
        )


        registration_details.additional_properties = d
        return registration_details

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
