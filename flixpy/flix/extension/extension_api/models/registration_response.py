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


T = TypeVar("T", bound="RegistrationResponse")


@_attrs_define
class RegistrationResponse:
    """
    Attributes:
        flix_id (int): The Flix-maintained identifier for this API consumer.
        token (str): The generated access token that the API consumer can use to access the rest of the API.
        actions (List['RegistrationResponseAction']): The actions registered for this API consumer.
    """

    flix_id: int
    token: str
    actions: List["RegistrationResponseAction"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.registration_response_action import RegistrationResponseAction

        flix_id = self.flix_id
        token = self.token
        actions = []
        for actions_item_data in self.actions:
            actions_item = actions_item_data.to_dict()

            actions.append(actions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "flixId": flix_id,
                "token": token,
                "actions": actions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.registration_response_action import RegistrationResponseAction

        d = src_dict.copy()
        flix_id = d.pop("flixId")

        token = d.pop("token")

        actions = []
        _actions = d.pop("actions")
        for actions_item_data in _actions:
            actions_item = RegistrationResponseAction.from_dict(actions_item_data)

            actions.append(actions_item)

        registration_response = cls(
            flix_id=flix_id,
            token=token,
            actions=actions,
        )

        registration_response.additional_properties = d
        return registration_response

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
