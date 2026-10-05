from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.registration_response_action import RegistrationResponseAction


T = TypeVar("T", bound="ActionsUpdateResponse")


@_attrs_define
class ActionsUpdateResponse:
    """
    Attributes:
        actions (List['RegistrationResponseAction']): The actions registered for this API consumer.
    """

    actions: List["RegistrationResponseAction"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.registration_response_action import RegistrationResponseAction

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
        from ..models.registration_response_action import RegistrationResponseAction

        d = src_dict.copy()
        actions = []
        _actions = d.pop("actions")
        for actions_item_data in _actions:
            actions_item = RegistrationResponseAction.from_dict(actions_item_data)

            actions.append(actions_item)

        actions_update_response = cls(
            actions=actions,
        )

        actions_update_response.additional_properties = d
        return actions_update_response

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
