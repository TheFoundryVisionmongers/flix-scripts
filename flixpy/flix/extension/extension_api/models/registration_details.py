from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistrationDetails")


@_attrs_define
class RegistrationDetails:
    """
    Attributes:
        name (str): The name for this API client
        client_uid (str): The API client-specified identifier for this API client
        flix_id (float): The Flix-maintained identifier for this API client
        version (Union[Unset, str]): The version of this API client (Optional)
    """

    name: str
    client_uid: str
    flix_id: float
    version: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        client_uid = self.client_uid
        flix_id = self.flix_id
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "clientUid": client_uid,
                "flixId": flix_id,
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

        flix_id = d.pop("flixId")

        version = d.pop("version", UNSET)

        registration_details = cls(
            name=name,
            client_uid=client_uid,
            flix_id=flix_id,
            version=version,
        )

        registration_details.additional_properties = d
        return registration_details

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
