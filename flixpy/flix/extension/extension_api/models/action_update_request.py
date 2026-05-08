from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.registration_request_action import RegistrationRequestAction


T = TypeVar("T", bound="ActionUpdateRequest")


@_attrs_define
class ActionUpdateRequest:
    """
    Attributes:
        actions (List['RegistrationRequestAction']): The actions available for this API consumer.
    """

    actions: List["RegistrationRequestAction"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        actions = []
        for actions_item_data in self.actions:
            actions_item = actions_item_data.to_dict()

            actions.append(actions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actions": actions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.registration_request_action import RegistrationRequestAction

        d = src_dict.copy()
        actions = []
        _actions = d.pop("actions")
        for actions_item_data in _actions:
            actions_item = RegistrationRequestAction.from_dict(actions_item_data)

            actions.append(actions_item)

        action_update_request = cls(
            actions=actions,
        )

        action_update_request.additional_properties = d
        return action_update_request

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
