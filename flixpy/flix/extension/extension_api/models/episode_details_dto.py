import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.episode_details_dto_metadata import EpisodeDetailsDtoMetadata


T = TypeVar("T", bound="EpisodeDetailsDto")


@_attrs_define
class EpisodeDetailsDto:
    """
    Attributes:
        id (int): The Flix identifier for the episode.
        metadata (EpisodeDetailsDtoMetadata): Arbitrary key-value metadata to merge into the entity. Each value must be
            a string, or `null` to delete that key.

            **Note:** Keys in this dictionary are **case-sensitive**.

            Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
            Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
        tracking_code (str): The episode's tracking code.
        created_date (datetime.datetime): The date the episode was created.
        owner (str): The user that created the episode.
        title (Optional[str]): The episode's display title.
    """

    id: int
    metadata: "EpisodeDetailsDtoMetadata"
    tracking_code: str
    created_date: datetime.datetime
    owner: str
    title: Optional[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        metadata = self.metadata.to_dict()

        tracking_code = self.tracking_code
        created_date = self.created_date.isoformat()

        owner = self.owner
        title = self.title

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "metadata": metadata,
                "trackingCode": tracking_code,
                "createdDate": created_date,
                "owner": owner,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.episode_details_dto_metadata import EpisodeDetailsDtoMetadata

        d = src_dict.copy()
        id = d.pop("id")

        metadata = EpisodeDetailsDtoMetadata.from_dict(d.pop("metadata"))

        tracking_code = d.pop("trackingCode")

        created_date = isoparse(d.pop("createdDate"))

        owner = d.pop("owner")

        title = d.pop("title")

        episode_details_dto = cls(
            id=id,
            metadata=metadata,
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
