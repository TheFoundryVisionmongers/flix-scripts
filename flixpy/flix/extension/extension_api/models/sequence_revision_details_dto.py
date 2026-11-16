from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.sequence_revision_details_dto_metadata import SequenceRevisionDetailsDtoMetadata





T = TypeVar("T", bound="SequenceRevisionDetailsDto")



@_attrs_define
class SequenceRevisionDetailsDto:
    """ 
        Attributes:
            id (int): The Flix identifier for the sequence revision.
            metadata (SequenceRevisionDetailsDtoMetadata): Arbitrary key-value metadata to merge into the entity. Each value
                must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            created_date (datetime.datetime | None): The date the sequence revision was created.
            owner (str): The user that created the sequence revision.
            published (bool): Whether this sequence revision has been published to editorial.
            comment (str): Any comment added to the sequence revision when saving.
            shot_names (list[str]): The list of shot names included in the sequence revision, derived from the named shots
                of the panels in the sequence revision.
     """

    id: int
    metadata: SequenceRevisionDetailsDtoMetadata
    created_date: datetime.datetime | None
    owner: str
    published: bool
    comment: str
    shot_names: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.sequence_revision_details_dto_metadata import SequenceRevisionDetailsDtoMetadata # noqa: PLC0415
        id = self.id

        metadata = self.metadata.to_dict()

        created_date: None | str
        if isinstance(self.created_date, datetime.datetime):
            created_date = self.created_date.isoformat()
        else:
            created_date = self.created_date

        owner = self.owner

        published = self.published

        comment = self.comment

        shot_names = self.shot_names




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "metadata": metadata,
            "createdDate": created_date,
            "owner": owner,
            "published": published,
            "comment": comment,
            "shotNames": shot_names,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sequence_revision_details_dto_metadata import SequenceRevisionDetailsDtoMetadata # noqa: PLC0415
        d = dict(src_dict)
        id = d.pop("id")

        metadata = SequenceRevisionDetailsDtoMetadata.from_dict(d.pop("metadata"))




        def _parse_created_date(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_date_type_0 = datetime.datetime.fromisoformat(data)



                return created_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        created_date = _parse_created_date(d.pop("createdDate"))


        owner = d.pop("owner")

        published = d.pop("published")

        comment = d.pop("comment")

        shot_names = cast(list[str], d.pop("shotNames"))


        sequence_revision_details_dto = cls(
            id=id,
            metadata=metadata,
            created_date=created_date,
            owner=owner,
            published=published,
            comment=comment,
            shot_names=shot_names,
        )


        sequence_revision_details_dto.additional_properties = d
        return sequence_revision_details_dto

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
