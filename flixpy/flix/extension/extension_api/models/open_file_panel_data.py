from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.keyframe_dto import KeyframeDto
  from ..models.open_file_panel_data_origin_sbp import OpenFilePanelDataOriginSbp
  from ..models.open_source_file_data import OpenSourceFileData





T = TypeVar("T", bound="OpenFilePanelData")



@_attrs_define
class OpenFilePanelData:
    """ 
        Attributes:
            id (int):
            index (int):
            revision_id (int):
            asset_id (int):
            is_animated (bool):
            source_file (OpenSourceFileData | Unset):
            annotation_asset_id (int | Unset):
            shot_id (int | Unset):
            dialogue (str | Unset):
            origin_sbp (OpenFilePanelDataOriginSbp | Unset):
            keyframes (list[KeyframeDto] | Unset):
            shot_name (str | Unset):
     """

    id: int
    index: int
    revision_id: int
    asset_id: int
    is_animated: bool
    source_file: OpenSourceFileData | Unset = UNSET
    annotation_asset_id: int | Unset = UNSET
    shot_id: int | Unset = UNSET
    dialogue: str | Unset = UNSET
    origin_sbp: OpenFilePanelDataOriginSbp | Unset = UNSET
    keyframes: list[KeyframeDto] | Unset = UNSET
    shot_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.keyframe_dto import KeyframeDto # noqa: PLC0415
        from ..models.open_file_panel_data_origin_sbp import OpenFilePanelDataOriginSbp # noqa: PLC0415
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        id = self.id

        index = self.index

        revision_id = self.revision_id

        asset_id = self.asset_id

        is_animated = self.is_animated

        source_file: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_file, Unset):
            source_file = self.source_file.to_dict()

        annotation_asset_id = self.annotation_asset_id

        shot_id = self.shot_id

        dialogue = self.dialogue

        origin_sbp: dict[str, Any] | Unset = UNSET
        if not isinstance(self.origin_sbp, Unset):
            origin_sbp = self.origin_sbp.to_dict()

        keyframes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.keyframes, Unset):
            keyframes = []
            for keyframes_item_data in self.keyframes:
                keyframes_item = keyframes_item_data.to_dict()
                keyframes.append(keyframes_item)



        shot_name = self.shot_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "index": index,
            "revisionId": revision_id,
            "assetId": asset_id,
            "isAnimated": is_animated,
        })
        if source_file is not UNSET:
            field_dict["sourceFile"] = source_file
        if annotation_asset_id is not UNSET:
            field_dict["annotationAssetId"] = annotation_asset_id
        if shot_id is not UNSET:
            field_dict["shotId"] = shot_id
        if dialogue is not UNSET:
            field_dict["dialogue"] = dialogue
        if origin_sbp is not UNSET:
            field_dict["originSbp"] = origin_sbp
        if keyframes is not UNSET:
            field_dict["keyframes"] = keyframes
        if shot_name is not UNSET:
            field_dict["shotName"] = shot_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.keyframe_dto import KeyframeDto # noqa: PLC0415
        from ..models.open_file_panel_data_origin_sbp import OpenFilePanelDataOriginSbp # noqa: PLC0415
        from ..models.open_source_file_data import OpenSourceFileData # noqa: PLC0415
        d = dict(src_dict)
        id = d.pop("id")

        index = d.pop("index")

        revision_id = d.pop("revisionId")

        asset_id = d.pop("assetId")

        is_animated = d.pop("isAnimated")

        _source_file = d.pop("sourceFile", UNSET)
        source_file: OpenSourceFileData | Unset
        if isinstance(_source_file,  Unset) or _source_file is None:
            source_file = UNSET
        else:
            source_file = OpenSourceFileData.from_dict(_source_file)




        annotation_asset_id = d.pop("annotationAssetId", UNSET)

        shot_id = d.pop("shotId", UNSET)

        dialogue = d.pop("dialogue", UNSET)

        _origin_sbp = d.pop("originSbp", UNSET)
        origin_sbp: OpenFilePanelDataOriginSbp | Unset
        if isinstance(_origin_sbp,  Unset) or _origin_sbp is None:
            origin_sbp = UNSET
        else:
            origin_sbp = OpenFilePanelDataOriginSbp.from_dict(_origin_sbp)




        _keyframes = d.pop("keyframes", UNSET)
        keyframes: list[KeyframeDto] | Unset = UNSET
        if _keyframes is not UNSET:
            keyframes = []
            for keyframes_item_data in _keyframes:
                keyframes_item = KeyframeDto.from_dict(keyframes_item_data)



                keyframes.append(keyframes_item)


        shot_name = d.pop("shotName", UNSET)

        open_file_panel_data = cls(
            id=id,
            index=index,
            revision_id=revision_id,
            asset_id=asset_id,
            is_animated=is_animated,
            source_file=source_file,
            annotation_asset_id=annotation_asset_id,
            shot_id=shot_id,
            dialogue=dialogue,
            origin_sbp=origin_sbp,
            keyframes=keyframes,
            shot_name=shot_name,
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
