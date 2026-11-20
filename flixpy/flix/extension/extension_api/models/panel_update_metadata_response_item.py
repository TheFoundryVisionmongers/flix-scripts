from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.panel_update_metadata_response_item_metadata import (
        PanelUpdateMetadataResponseItemMetadata,
    )


T = TypeVar("T", bound="PanelUpdateMetadataResponseItem")


@_attrs_define
class PanelUpdateMetadataResponseItem:
    """
    Attributes:
        id (int): The panel ID against which this metadata item is associated.
        metadata (PanelUpdateMetadataResponseItemMetadata): Arbitrary key-value metadata to merge into the entity. Each
            value must be a string, or `null` to delete that key.

            **Note:** Keys in this dictionary are **case-sensitive**.

            Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
            Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
    """

    id: int
    metadata: "PanelUpdateMetadataResponseItemMetadata"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_update_metadata_response_item_metadata import (
            PanelUpdateMetadataResponseItemMetadata,
        )

        d = src_dict.copy()
        id = d.pop("id")

        metadata = PanelUpdateMetadataResponseItemMetadata.from_dict(d.pop("metadata"))

        panel_update_metadata_response_item = cls(
            id=id,
            metadata=metadata,
        )

        panel_update_metadata_response_item.additional_properties = d
        return panel_update_metadata_response_item

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
