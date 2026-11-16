from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.action_state import ActionState
from ..models.action_type import ActionType
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.action_event_panel_response import ActionEventPanelResponse





T = TypeVar("T", bound="ActionEvent")



@_attrs_define
class ActionEvent:
    """ 
        Attributes:
            api_client_id (int | None):
            action_id (int):
            state (ActionState):
            action (ActionType):
            panels (list[ActionEventPanelResponse] | Unset):
     """

    api_client_id: int | None
    action_id: int
    state: ActionState
    action: ActionType
    panels: list[ActionEventPanelResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.action_event_panel_response import ActionEventPanelResponse # noqa: PLC0415
        api_client_id: int | None
        api_client_id = self.api_client_id

        action_id = self.action_id

        state = self.state.value

        action = self.action.value

        panels: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.panels, Unset):
            panels = []
            for panels_item_data in self.panels:
                panels_item = panels_item_data.to_dict()
                panels.append(panels_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "apiClientId": api_client_id,
            "actionId": action_id,
            "state": state,
            "action": action,
        })
        if panels is not UNSET:
            field_dict["panels"] = panels

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_event_panel_response import ActionEventPanelResponse # noqa: PLC0415
        d = dict(src_dict)
        def _parse_api_client_id(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        api_client_id = _parse_api_client_id(d.pop("apiClientId"))


        action_id = d.pop("actionId")

        state = ActionState(d.pop("state"))




        action = ActionType(d.pop("action"))




        _panels = d.pop("panels", UNSET)
        panels: list[ActionEventPanelResponse] | Unset = UNSET
        if _panels is not UNSET:
            panels = []
            for panels_item_data in _panels:
                panels_item = ActionEventPanelResponse.from_dict(panels_item_data)



                panels.append(panels_item)


        action_event = cls(
            api_client_id=api_client_id,
            action_id=action_id,
            state=state,
            action=action,
            panels=panels,
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
