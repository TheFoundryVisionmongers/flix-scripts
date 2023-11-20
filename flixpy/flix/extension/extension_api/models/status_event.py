from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.actions_in_progress import ActionsInProgress
    from ..models.revision_status import RevisionStatus


T = TypeVar("T", bound="StatusEvent")


@_attrs_define
class StatusEvent:
    """
    Attributes:
        can_create (bool):
        revision_status (RevisionStatus):
        actions_in_progress (ActionsInProgress):
    """

    can_create: bool
    revision_status: "RevisionStatus"
    actions_in_progress: "ActionsInProgress"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        can_create = self.can_create
        revision_status = self.revision_status.to_dict()

        actions_in_progress = self.actions_in_progress.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "canCreate": can_create,
                "revisionStatus": revision_status,
                "actionsInProgress": actions_in_progress,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.actions_in_progress import ActionsInProgress
        from ..models.revision_status import RevisionStatus

        d = src_dict.copy()
        can_create = d.pop("canCreate")

        revision_status = RevisionStatus.from_dict(d.pop("revisionStatus"))

        actions_in_progress = ActionsInProgress.from_dict(d.pop("actionsInProgress"))

        status_event = cls(
            can_create=can_create,
            revision_status=revision_status,
            actions_in_progress=actions_in_progress,
        )

        status_event.additional_properties = d
        return status_event

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
