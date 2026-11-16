from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.show_details_dto_metadata import ShowDetailsDtoMetadata





T = TypeVar("T", bound="ShowDetailsDto")



@_attrs_define
class ShowDetailsDto:
    """ 
        Attributes:
            id (int): The Flix identifier for the show.
            metadata (ShowDetailsDtoMetadata): Arbitrary key-value metadata to merge into the entity. Each value must be a
                string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            tracking_code (str): The show's tracking code.
            title (None | str): The show's display title.
            aspect_ratio (float): The configured aspect ratio for the active sequence or show.
            default_aspect_ratio (float): The configured default aspect ratio for the sequence.
     """

    id: int
    metadata: ShowDetailsDtoMetadata
    tracking_code: str
    title: None | str
    aspect_ratio: float
    default_aspect_ratio: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.show_details_dto_metadata import ShowDetailsDtoMetadata # noqa: PLC0415
        id = self.id

        metadata = self.metadata.to_dict()

        tracking_code = self.tracking_code

        title: None | str
        title = self.title

        aspect_ratio = self.aspect_ratio

        default_aspect_ratio = self.default_aspect_ratio


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "metadata": metadata,
            "trackingCode": tracking_code,
            "title": title,
            "aspectRatio": aspect_ratio,
            "defaultAspectRatio": default_aspect_ratio,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.show_details_dto_metadata import ShowDetailsDtoMetadata # noqa: PLC0415
        d = dict(src_dict)
        id = d.pop("id")

        metadata = ShowDetailsDtoMetadata.from_dict(d.pop("metadata"))




        tracking_code = d.pop("trackingCode")

        def _parse_title(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        title = _parse_title(d.pop("title"))


        aspect_ratio = d.pop("aspectRatio")

        default_aspect_ratio = d.pop("defaultAspectRatio")

        show_details_dto = cls(
            id=id,
            metadata=metadata,
            tracking_code=tracking_code,
            title=title,
            aspect_ratio=aspect_ratio,
            default_aspect_ratio=default_aspect_ratio,
        )


        show_details_dto.additional_properties = d
        return show_details_dto

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
