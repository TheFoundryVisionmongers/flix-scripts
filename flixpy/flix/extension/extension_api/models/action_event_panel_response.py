from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.action_event_panel_response_metadata import (
        ActionEventPanelResponseMetadata,
    )


T = TypeVar("T", bound="ActionEventPanelResponse")


@_attrs_define
class ActionEventPanelResponse:
    """
    Attributes:
        panel_id (int):
        panel_revision (int):
        path (str):
        metadata (Union[Unset, ActionEventPanelResponseMetadata]): Arbitrary key-value metadata for the panel. Example:
            {'ftrack:sequence_id': 9402}.
    """

    panel_id: int
    panel_revision: int
    path: str
    metadata: Union[Unset, "ActionEventPanelResponseMetadata"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        panel_id = self.panel_id
        panel_revision = self.panel_revision
        path = self.path
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "panelId": panel_id,
                "panelRevision": panel_revision,
                "path": path,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.action_event_panel_response_metadata import (
            ActionEventPanelResponseMetadata,
        )

        d = src_dict.copy()
        panel_id = d.pop("panelId")

        panel_revision = d.pop("panelRevision")

        path = d.pop("path")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ActionEventPanelResponseMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ActionEventPanelResponseMetadata.from_dict(_metadata)

        action_event_panel_response = cls(
            panel_id=panel_id,
            panel_revision=panel_revision,
            path=path,
            metadata=metadata,
        )

        action_event_panel_response.additional_properties = d
        return action_event_panel_response

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
