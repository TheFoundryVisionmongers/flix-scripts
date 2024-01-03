from typing import Any, Dict, List, Optional, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.action_state import ActionState
from ..models.action_type import ActionType

T = TypeVar("T", bound="ActionEvent")


@_attrs_define
class ActionEvent:
    """
    Attributes:
        action_id (int):
        state (ActionState):
        action (ActionType):
        api_client_id (Optional[int]):
    """

    action_id: int
    state: ActionState
    action: ActionType
    api_client_id: Optional[int]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        action_id = self.action_id
        state = self.state.value

        action = self.action.value

        api_client_id = self.api_client_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actionId": action_id,
                "state": state,
                "action": action,
                "apiClientId": api_client_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        action_id = d.pop("actionId")

        state = ActionState(d.pop("state"))

        action = ActionType(d.pop("action"))

        api_client_id = d.pop("apiClientId")

        action_event = cls(
            action_id=action_id,
            state=state,
            action=action,
            api_client_id=api_client_id,
        )

        action_event.additional_properties = d
        return action_event

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
