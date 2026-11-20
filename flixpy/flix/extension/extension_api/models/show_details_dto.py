from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.show_details_dto_metadata import ShowDetailsDtoMetadata


T = TypeVar("T", bound="ShowDetailsDto")


@_attrs_define
class ShowDetailsDto:
    """
    Attributes:
        id (int): The Flix identifier for the show.
        tracking_code (str): The show's tracking code.
        aspect_ratio (float): The configured aspect ratio for the active sequence or show.
        default_aspect_ratio (float): The configured default aspect ratio for the sequence.
        metadata (Union[Unset, ShowDetailsDtoMetadata]): Arbitrary key-value metadata to merge into the entity. Each
            value must be a string, or `null` to delete that key.

            **Note:** Keys in this dictionary are **case-sensitive**.

            Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
            Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
        title (Optional[str]): The show's display title.
    """

    id: int
    tracking_code: str
    aspect_ratio: float
    default_aspect_ratio: float
    title: Optional[str]
    metadata: Union[Unset, "ShowDetailsDtoMetadata"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        tracking_code = self.tracking_code
        aspect_ratio = self.aspect_ratio
        default_aspect_ratio = self.default_aspect_ratio
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        title = self.title

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "trackingCode": tracking_code,
                "aspectRatio": aspect_ratio,
                "defaultAspectRatio": default_aspect_ratio,
                "title": title,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.show_details_dto_metadata import ShowDetailsDtoMetadata

        d = src_dict.copy()
        id = d.pop("id")

        tracking_code = d.pop("trackingCode")

        aspect_ratio = d.pop("aspectRatio")

        default_aspect_ratio = d.pop("defaultAspectRatio")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ShowDetailsDtoMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ShowDetailsDtoMetadata.from_dict(_metadata)

        title = d.pop("title")

        show_details_dto = cls(
            id=id,
            tracking_code=tracking_code,
            aspect_ratio=aspect_ratio,
            default_aspect_ratio=default_aspect_ratio,
            metadata=metadata,
            title=title,
        )

        show_details_dto.additional_properties = d
        return show_details_dto

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
