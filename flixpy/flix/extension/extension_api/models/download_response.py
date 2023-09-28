from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DownloadResponse")


@_attrs_define
class DownloadResponse:
    """
    Attributes:
        file_name (str):
        file_path (str):
        asset_id (int):
        media_object_id (int):
    """

    file_name: str
    file_path: str
    asset_id: int
    media_object_id: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        file_name = self.file_name
        file_path = self.file_path
        asset_id = self.asset_id
        media_object_id = self.media_object_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fileName": file_name,
                "filePath": file_path,
                "assetId": asset_id,
                "mediaObjectId": media_object_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        file_name = d.pop("fileName")

        file_path = d.pop("filePath")

        asset_id = d.pop("assetId")

        media_object_id = d.pop("mediaObjectId")

        download_response = cls(
            file_name=file_name,
            file_path=file_path,
            asset_id=asset_id,
            media_object_id=media_object_id,
        )

        download_response.additional_properties = d
        return download_response

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
