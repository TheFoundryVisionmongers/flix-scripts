from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.action_state import ActionState
from ..models.action_type import ActionType
from typing import cast






T = TypeVar("T", bound="ActionEvent")



@_attrs_define
class ActionEvent:
    """ 
        Attributes:
            api_client_id (int | None):
            action_id (int):
            state (ActionState):
            action (ActionType):
     """

    api_client_id: int | None
    action_id: int
    state: ActionState
    action: ActionType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        api_client_id: int | None
        api_client_id = self.api_client_id

        action_id = self.action_id

        state = self.state.value

        action = self.action.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "apiClientId": api_client_id,
            "actionId": action_id,
            "state": state,
            "action": action,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_api_client_id(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        api_client_id = _parse_api_client_id(d.pop("apiClientId"))


        action_id = d.pop("actionId")

        state = ActionState(d.pop("state"))




        action = ActionType(d.pop("action"))




        action_event = cls(
            api_client_id=api_client_id,
            action_id=action_id,
            state=state,
            action=action,
        )


        action_event.additional_properties = d
        return action_event

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
