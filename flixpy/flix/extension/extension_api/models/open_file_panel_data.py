from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.open_source_file_data import OpenSourceFileData





T = TypeVar("T", bound="OpenFilePanelData")



@_attrs_define
class OpenFilePanelData:
    """ 
        Attributes:
            id (int):
            asset_id (int):
            is_animated (bool):
            source_file (None | OpenSourceFileData):
            annotation_asset_id (int | Unset):
     """

    id: int
    asset_id: int
    is_animated: bool
    source_file: None | OpenSourceFileData
    annotation_asset_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        id = self.id

        asset_id = self.asset_id

        is_animated = self.is_animated

        source_file: dict[str, Any] | None
        if isinstance(self.source_file, OpenSourceFileData):
            source_file = self.source_file.to_dict()
        else:
            source_file = self.source_file

        annotation_asset_id = self.annotation_asset_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "assetId": asset_id,
            "isAnimated": is_animated,
            "sourceFile": source_file,
        })
        if annotation_asset_id is not UNSET:
            field_dict["annotationAssetId"] = annotation_asset_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        d = dict(src_dict)
        id = d.pop("id")

        asset_id = d.pop("assetId")

        is_animated = d.pop("isAnimated")

        def _parse_source_file(data: object) -> None | OpenSourceFileData:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_file_type_1 = OpenSourceFileData.from_dict(data)



                return source_file_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenSourceFileData, data)

        source_file = _parse_source_file(d.pop("sourceFile"))


        annotation_asset_id = d.pop("annotationAssetId", UNSET)

        open_file_panel_data = cls(
            id=id,
            asset_id=asset_id,
            is_animated=is_animated,
            source_file=source_file,
            annotation_asset_id=annotation_asset_id,
        )


        open_file_panel_data.additional_properties = d
        return open_file_panel_data

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
