from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.asset_type import AssetType

T = TypeVar("T", bound="DownloadRequest")


@_attrs_define
class DownloadRequest:
    """
    Attributes:
        asset_id (int): The identifier of an asset in Flix. For example, the asset specified in the `OPEN` event
        target_folder (str): The folder that the requested asset should be downloaded into
        asset_type (AssetType): The type of media object to download for the specified asset
    """

    asset_id: int
    target_folder: str
    asset_type: AssetType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        asset_id = self.asset_id
        target_folder = self.target_folder
        asset_type = self.asset_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assetId": asset_id,
                "targetFolder": target_folder,
                "assetType": asset_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        asset_id = d.pop("assetId")

        target_folder = d.pop("targetFolder")

        asset_type = AssetType(d.pop("assetType"))

        download_request = cls(
            asset_id=asset_id,
            target_folder=target_folder,
            asset_type=asset_type,
        )

        download_request.additional_properties = d
        return download_request

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
