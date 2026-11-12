from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.updated_panel_metadata_dto_metadata import (
        UpdatedPanelMetadataDtoMetadata,
    )


T = TypeVar("T", bound="UpdatedPanelMetadataDto")


@_attrs_define
class UpdatedPanelMetadataDto:
    """
    Attributes:
        id (int):
        metadata (UpdatedPanelMetadataDtoMetadata): Arbitrary key-value metadata for the panel. Example:
            {'ftrack:sequence_id': '9402'}.
    """

    id: int
    metadata: "UpdatedPanelMetadataDtoMetadata"
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
        from ..models.updated_panel_metadata_dto_metadata import (
            UpdatedPanelMetadataDtoMetadata,
        )

        d = src_dict.copy()
        id = d.pop("id")

        metadata = UpdatedPanelMetadataDtoMetadata.from_dict(d.pop("metadata"))

        updated_panel_metadata_dto = cls(
            id=id,
            metadata=metadata,
        )

        updated_panel_metadata_dto.additional_properties = d
        return updated_panel_metadata_dto

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
