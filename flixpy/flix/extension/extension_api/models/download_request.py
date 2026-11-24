from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.asset_type import AssetType






T = TypeVar("T", bound="DownloadRequest")



@_attrs_define
class DownloadRequest:
    """ 
        Attributes:
            asset_id (int): The identifier of an asset in Flix. For example, the asset specified in the `OPEN` event.
            target_folder (str): The folder that the requested asset should be downloaded into.
            asset_type (AssetType): The type of media object to download for the specified asset.
     """

    asset_id: int
    target_folder: str
    asset_type: AssetType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        asset_id = self.asset_id

        target_folder = self.target_folder

        asset_type = self.asset_type.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "assetId": asset_id,
            "targetFolder": target_folder,
            "assetType": asset_type,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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
