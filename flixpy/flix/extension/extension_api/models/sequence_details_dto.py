from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.sequence_details_dto_metadata import SequenceDetailsDtoMetadata





T = TypeVar("T", bound="SequenceDetailsDto")



@_attrs_define
class SequenceDetailsDto:
    """ 
        Attributes:
            id (int): The Flix identifier for the sequence.
            tracking_code (str): The sequence's tracking code.
            created_date (datetime.datetime): The date the sequence was created.
            owner (str): The user that created the sequence.
            title (None | str): The sequence's display title.
            aspect_ratio (float): The aspect ratio used by the sequence.
            metadata (SequenceDetailsDtoMetadata | Unset): Arbitrary key-value metadata to merge into the entity. Each value
                must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
     """

    id: int
    tracking_code: str
    created_date: datetime.datetime
    owner: str
    title: None | str
    aspect_ratio: float
    metadata: SequenceDetailsDtoMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.sequence_details_dto_metadata import SequenceDetailsDtoMetadata # noqa: PLC0415
        id = self.id

        tracking_code = self.tracking_code

        created_date = self.created_date.isoformat()

        owner = self.owner

        title: None | str
        title = self.title

        aspect_ratio = self.aspect_ratio

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "trackingCode": tracking_code,
            "createdDate": created_date,
            "owner": owner,
            "title": title,
            "aspectRatio": aspect_ratio,
        })
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sequence_details_dto_metadata import SequenceDetailsDtoMetadata # noqa: PLC0415
        d = dict(src_dict)
        id = d.pop("id")

        tracking_code = d.pop("trackingCode")

        created_date = datetime.datetime.fromisoformat(d.pop("createdDate"))




        owner = d.pop("owner")

        def _parse_title(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        title = _parse_title(d.pop("title"))


        aspect_ratio = d.pop("aspectRatio")

        _metadata = d.pop("metadata", UNSET)
        metadata: SequenceDetailsDtoMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = SequenceDetailsDtoMetadata.from_dict(_metadata)




        sequence_details_dto = cls(
            id=id,
            tracking_code=tracking_code,
            created_date=created_date,
            owner=owner,
            title=title,
            aspect_ratio=aspect_ratio,
            metadata=metadata,
        )


        sequence_details_dto.additional_properties = d
        return sequence_details_dto

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
