from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.registration_request_action import RegistrationRequestAction


T = TypeVar("T", bound="RegistrationRequest")


@_attrs_define
class RegistrationRequest:
    """
    Attributes:
        name (str): The name of this API consumer.
        client_uid (str): A unique identifier for this API consumer.
        version (Union[Unset, str]): The version of this API consumer (Optional).
        log_paths (Union[Unset, List[str]]): Paths to the extension's log files.
        actions (Union[Unset, List['RegistrationRequestAction']]): The actions available for this API consumer.
        icon_svg (Union[Unset, str]): The SVG icon for this API consumer.
    """

    name: str
    client_uid: str
    version: Union[Unset, str] = UNSET
    log_paths: Union[Unset, List[str]] = UNSET
    actions: Union[Unset, List["RegistrationRequestAction"]] = UNSET
    icon_svg: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        client_uid = self.client_uid
        version = self.version
        log_paths: Union[Unset, List[str]] = UNSET
        if not isinstance(self.log_paths, Unset):
            log_paths = self.log_paths

        actions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()

                actions.append(actions_item)

        icon_svg = self.icon_svg

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "clientUid": client_uid,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if log_paths is not UNSET:
            field_dict["logPaths"] = log_paths
        if actions is not UNSET:
            field_dict["actions"] = actions
        if icon_svg is not UNSET:
            field_dict["iconSvg"] = icon_svg

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.registration_request_action import RegistrationRequestAction

        d = src_dict.copy()
        name = d.pop("name")

        client_uid = d.pop("clientUid")

        version = d.pop("version", UNSET)

        log_paths = cast(List[str], d.pop("logPaths", UNSET))

        actions = []
        _actions = d.pop("actions", UNSET)
        for actions_item_data in _actions or []:
            actions_item = RegistrationRequestAction.from_dict(actions_item_data)

            actions.append(actions_item)

        icon_svg = d.pop("iconSvg", UNSET)

        registration_request = cls(
            name=name,
            client_uid=client_uid,
            version=version,
            log_paths=log_paths,
            actions=actions,
            icon_svg=icon_svg,
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
