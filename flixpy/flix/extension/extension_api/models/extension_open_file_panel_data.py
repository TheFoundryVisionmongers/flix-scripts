from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_source_file_data import OpenSourceFileData


T = TypeVar("T", bound="ExtensionOpenFilePanelData")


@_attrs_define
class ExtensionOpenFilePanelData:
    """
    Attributes:
        id (int):
        asset_id (int):
        is_animated (bool):
        source_file (Union[Unset, None, OpenSourceFileData]):
        annotation_asset_id (Union[Unset, None, int]):
    """

    id: int
    asset_id: int
    is_animated: bool
    source_file: Union[Unset, None, "OpenSourceFileData"] = UNSET
    annotation_asset_id: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        asset_id = self.asset_id
        is_animated = self.is_animated
        source_file: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.source_file, Unset):
            source_file = self.source_file.to_dict() if self.source_file else None

        annotation_asset_id = self.annotation_asset_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "assetId": asset_id,
                "isAnimated": is_animated,
            }
        )
        if source_file is not UNSET:
            field_dict["sourceFile"] = source_file
        if annotation_asset_id is not UNSET:
            field_dict["annotationAssetId"] = annotation_asset_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.open_source_file_data import OpenSourceFileData

        d = src_dict.copy()
        id = d.pop("id")

        asset_id = d.pop("assetId")

        is_animated = d.pop("isAnimated")

        _source_file = d.pop("sourceFile", UNSET)
        source_file: Union[Unset, None, OpenSourceFileData]
        if _source_file is None:
            source_file = None
        elif isinstance(_source_file, Unset):
            source_file = UNSET
        else:
            source_file = OpenSourceFileData.from_dict(_source_file)

        annotation_asset_id = d.pop("annotationAssetId", UNSET)

        extension_open_file_panel_data = cls(
            id=id,
            asset_id=asset_id,
            is_animated=is_animated,
            source_file=source_file,
            annotation_asset_id=annotation_asset_id,
        )

        extension_open_file_panel_data.additional_properties = d
        return extension_open_file_panel_data

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
