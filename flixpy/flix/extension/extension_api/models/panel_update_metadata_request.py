from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.panel_update_metadata_request_metadata import (
        PanelUpdateMetadataRequestMetadata,
    )


T = TypeVar("T", bound="PanelUpdateMetadataRequest")


@_attrs_define
class PanelUpdateMetadataRequest:
    """
    Attributes:
        metadata (PanelUpdateMetadataRequestMetadata): Arbitrary key-value metadata to merge into the entity. Each value
            must be a string, or `null` to delete that key.

            **Note:** Keys in this dictionary are **case-sensitive**.

            Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
            Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
    """

    metadata: "PanelUpdateMetadataRequestMetadata"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_update_metadata_request_metadata import (
            PanelUpdateMetadataRequestMetadata,
        )

        d = src_dict.copy()
        metadata = PanelUpdateMetadataRequestMetadata.from_dict(d.pop("metadata"))

        panel_update_metadata_request = cls(
            metadata=metadata,
        )

        panel_update_metadata_request.additional_properties = d
        return panel_update_metadata_request

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
