from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.registration_details_actions_item import (
        RegistrationDetailsActionsItem,
    )


T = TypeVar("T", bound="RegistrationDetails")


@_attrs_define
class RegistrationDetails:
    """
    Attributes:
        flix_id (int): The Flix-maintained identifier for this API consumer.
        name (str): The name for this API consumer.
        client_uid (str): The API client-specified identifier for this API consumer.
        version (Union[Unset, str]): The version of this API consumer (Optional).
        log_paths (Union[Unset, List[str]]): Paths to the location where the extension will write its logs for different
            versions of the app (Optional).
        actions (Union[Unset, List['RegistrationDetailsActionsItem']]): List of actions available for this extension.
        icon_svg (Union[Unset, str]): SVG icon for the default extension button.
        short_name (Union[Unset, str]): Short name for extension to be used in context menu.
    """

    flix_id: int
    name: str
    client_uid: str
    version: Union[Unset, str] = UNSET
    log_paths: Union[Unset, List[str]] = UNSET
    actions: Union[Unset, List["RegistrationDetailsActionsItem"]] = UNSET
    icon_svg: Union[Unset, str] = UNSET
    short_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        flix_id = self.flix_id
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
        short_name = self.short_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "flixId": flix_id,
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
        if short_name is not UNSET:
            field_dict["shortName"] = short_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.registration_details_actions_item import (
            RegistrationDetailsActionsItem,
        )

        d = src_dict.copy()
        flix_id = d.pop("flixId")

        name = d.pop("name")

        client_uid = d.pop("clientUid")

        version = d.pop("version", UNSET)

        log_paths = cast(List[str], d.pop("logPaths", UNSET))

        actions = []
        _actions = d.pop("actions", UNSET)
        for actions_item_data in _actions or []:
            actions_item = RegistrationDetailsActionsItem.from_dict(actions_item_data)

            actions.append(actions_item)

        icon_svg = d.pop("iconSvg", UNSET)

        short_name = d.pop("shortName", UNSET)

        registration_details = cls(
            flix_id=flix_id,
            name=name,
            client_uid=client_uid,
            version=version,
            log_paths=log_paths,
            actions=actions,
            icon_svg=icon_svg,
            short_name=short_name,
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
