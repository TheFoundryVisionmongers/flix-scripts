from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistrationRequest")


@_attrs_define
class RegistrationRequest:
    """
    Attributes:
        name (str): The name for this API client
        client_uid (str): The API client-specified identifier for this API client
        version (Union[Unset, str]): The version of this API client (Optional)
        log_paths (list of str): Paths to the Maya log file
    """

    name: str
    client_uid: str
    version: Union[Unset, str] = UNSET
    log_paths: List[str] = None
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        client_uid = self.client_uid
        version = self.version
        log_paths = self.log_paths

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "clientUid": client_uid,
                "logPaths": log_paths
            }
        )
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        client_uid = d.pop("clientUid")

        version = d.pop("version", UNSET)

        log_paths = d.pop("logPaths")

        registration_request = cls(
            name=name,
            client_uid=client_uid,
            version=version,
            log_paths=log_paths,
        )

        registration_request.additional_properties = d
        return registration_request

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
