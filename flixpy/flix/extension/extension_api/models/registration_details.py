from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.registration_details_actions_item import RegistrationDetailsActionsItem





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
            actions (list[RegistrationDetailsActionsItem] | Unset): List of actions available for this extension.
            icon_svg (str | Unset): SVG icon for the default extension button.
            short_name (str | Unset): Short name for extension to be used in context menu.
     """

    flix_id: int
    name: str
    client_uid: str
    version: str | Unset = UNSET
    log_paths: list[str] | Unset = UNSET
    actions: list[RegistrationDetailsActionsItem] | Unset = UNSET
    icon_svg: str | Unset = UNSET
    short_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.registration_details_actions_item import RegistrationDetailsActionsItem # noqa: PLC0415
        flix_id = self.flix_id

        name = self.name

        client_uid = self.client_uid

        version = self.version

        log_paths: list[str] | Unset = UNSET
        if not isinstance(self.log_paths, Unset):
            log_paths = self.log_paths



        actions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)



        icon_svg = self.icon_svg

        short_name = self.short_name


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
        if actions is not UNSET:
            field_dict["actions"] = actions
        if icon_svg is not UNSET:
            field_dict["iconSvg"] = icon_svg
        if short_name is not UNSET:
            field_dict["shortName"] = short_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.registration_details_actions_item import RegistrationDetailsActionsItem # noqa: PLC0415
        d = dict(src_dict)
        flix_id = d.pop("flixId")

        name = d.pop("name")

        client_uid = d.pop("clientUid")

        version = d.pop("version", UNSET)

        log_paths = cast(list[str], d.pop("logPaths", UNSET))


        _actions = d.pop("actions", UNSET)
        actions: list[RegistrationDetailsActionsItem] | Unset = UNSET
        if _actions is not UNSET:
            actions = []
            for actions_item_data in _actions:
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
