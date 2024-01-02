import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="EpisodeDetailsDto")


@_attrs_define
class EpisodeDetailsDto:
    """
    Attributes:
        id (int):
        tracking_code (str):
        created_date (datetime.datetime):
        owner (str):
        title (Optional[str]):
    """

    id: int
    tracking_code: str
    created_date: datetime.datetime
    owner: str
    title: Optional[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        tracking_code = self.tracking_code
        created_date = self.created_date.isoformat()

        owner = self.owner
        title = self.title

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "trackingCode": tracking_code,
                "createdDate": created_date,
                "owner": owner,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        tracking_code = d.pop("trackingCode")

        created_date = isoparse(d.pop("createdDate"))

        owner = d.pop("owner")

        title = d.pop("title")

        episode_details_dto = cls(
            id=id,
            tracking_code=tracking_code,
            created_date=created_date,
            owner=owner,
            title=title,
        )

        episode_details_dto.additional_properties = d
        return episode_details_dto

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
