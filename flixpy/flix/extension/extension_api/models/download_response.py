from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DownloadResponse")


@_attrs_define
class DownloadResponse:
    """
    Attributes:
        asset_id (int): The identifier of the downloaded asset.
        media_object_id (int): The identifier of the specific media object that was downloaded.
        file_name (str): The name of the downloaded file on disk.
        file_path (str): The final path of the downloaded file on disk. This should just be
            `${targetFolder}/${fileName}`.
    """

    asset_id: int
    media_object_id: int
    file_name: str
    file_path: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        asset_id = self.asset_id
        media_object_id = self.media_object_id
        file_name = self.file_name
        file_path = self.file_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assetId": asset_id,
                "mediaObjectId": media_object_id,
                "fileName": file_name,
                "filePath": file_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        asset_id = d.pop("assetId")

        media_object_id = d.pop("mediaObjectId")

        file_name = d.pop("fileName")

        file_path = d.pop("filePath")

        download_response = cls(
            asset_id=asset_id,
            media_object_id=media_object_id,
            file_name=file_name,
            file_path=file_path,
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
