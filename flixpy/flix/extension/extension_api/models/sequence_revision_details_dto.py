import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="SequenceRevisionDetailsDto")


@_attrs_define
class SequenceRevisionDetailsDto:
    """
    Attributes:
        id (int):
        owner (str):
        published (bool):
        comment (str):
        created_date (Optional[datetime.datetime]):
    """

    id: int
    owner: str
    published: bool
    comment: str
    created_date: Optional[datetime.datetime]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        owner = self.owner
        published = self.published
        comment = self.comment
        created_date = self.created_date.isoformat() if self.created_date else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "owner": owner,
                "published": published,
                "comment": comment,
                "createdDate": created_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        owner = d.pop("owner")

        published = d.pop("published")

        comment = d.pop("comment")

        _created_date = d.pop("createdDate")
        created_date: Optional[datetime.datetime]
        if _created_date is None:
            created_date = None
        else:
            created_date = isoparse(_created_date)

        sequence_revision_details_dto = cls(
            id=id,
            owner=owner,
            published=published,
            comment=comment,
            created_date=created_date,
        )

        sequence_revision_details_dto.additional_properties = d
        return sequence_revision_details_dto

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
