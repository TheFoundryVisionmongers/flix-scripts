from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.custom_action_registration_request import CustomActionRegistrationRequest





T = TypeVar("T", bound="ActionsUpdateRequest")



@_attrs_define
class ActionsUpdateRequest:
    """ 
        Attributes:
            actions (list[CustomActionRegistrationRequest]): List of actions to be updated for this API client.
     """

    actions: list[CustomActionRegistrationRequest]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_action_registration_request import CustomActionRegistrationRequest # noqa: PLC0415
        actions = []
        for actions_item_data in self.actions:
            actions_item = actions_item_data.to_dict()
            actions.append(actions_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "actions": actions,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_action_registration_request import CustomActionRegistrationRequest # noqa: PLC0415
        d = dict(src_dict)
        actions = []
        _actions = d.pop("actions")
        for actions_item_data in (_actions):
            actions_item = CustomActionRegistrationRequest.from_dict(actions_item_data)



            actions.append(actions_item)


        actions_update_request = cls(
            actions=actions,
        )


        actions_update_request.additional_properties = d
        return actions_update_request

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
