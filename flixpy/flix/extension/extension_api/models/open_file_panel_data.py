from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.keyframe_request import KeyframeRequest
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
        annotation_asset_id (Union[Unset, int]):
        shot_id (Union[Unset, int]):
        source_file (Optional[OpenSourceFileData]):
        dialogue (Union[Unset, str]):
        origin_sbp (Union[Unset, OpenFilePanelDataOriginSbp]):
        keyframes (Union[Unset, List['KeyframeRequest']]):
        shot_name (Union[Unset, str]):
    """

    id: int
    index: int
    revision_id: int
    asset_id: int
    is_animated: bool
    source_file: Optional["OpenSourceFileData"]
    annotation_asset_id: Union[Unset, int] = UNSET
    shot_id: Union[Unset, int] = UNSET
    dialogue: Union[Unset, str] = UNSET
    origin_sbp: Union[Unset, "OpenFilePanelDataOriginSbp"] = UNSET
    keyframes: Union[Unset, List["KeyframeRequest"]] = UNSET
    shot_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        index = self.index
        revision_id = self.revision_id
        asset_id = self.asset_id
        is_animated = self.is_animated
        annotation_asset_id = self.annotation_asset_id
        shot_id = self.shot_id
        source_file = self.source_file.to_dict() if self.source_file else None

        dialogue = self.dialogue
        origin_sbp: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.origin_sbp, Unset):
            origin_sbp = self.origin_sbp.to_dict()

        keyframes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.keyframes, Unset):
            keyframes = []
            for keyframes_item_data in self.keyframes:
                keyframes_item = keyframes_item_data.to_dict()

                keyframes.append(keyframes_item)

        shot_name = self.shot_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "index": index,
                "revisionId": revision_id,
                "assetId": asset_id,
                "isAnimated": is_animated,
                "sourceFile": source_file,
            }
        )
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.keyframe_request import KeyframeRequest
        from ..models.open_file_panel_data_origin_sbp import OpenFilePanelDataOriginSbp
        from ..models.open_source_file_data import OpenSourceFileData

        d = src_dict.copy()
        id = d.pop("id")

        index = d.pop("index")

        revision_id = d.pop("revisionId")

        asset_id = d.pop("assetId")

        is_animated = d.pop("isAnimated")

        annotation_asset_id = d.pop("annotationAssetId", UNSET)

        shot_id = d.pop("shotId", UNSET)

        _source_file = d.pop("sourceFile")
        source_file: Optional[OpenSourceFileData]
        if _source_file is None:
            source_file = None
        else:
            source_file = OpenSourceFileData.from_dict(_source_file)

        dialogue = d.pop("dialogue", UNSET)

        _origin_sbp = d.pop("originSbp", UNSET)
        origin_sbp: Union[Unset, OpenFilePanelDataOriginSbp]
        if isinstance(_origin_sbp, Unset):
            origin_sbp = UNSET
        else:
            origin_sbp = OpenFilePanelDataOriginSbp.from_dict(_origin_sbp)

        keyframes = []
        _keyframes = d.pop("keyframes", UNSET)
        for keyframes_item_data in _keyframes or []:
            keyframes_item = KeyframeRequest.from_dict(keyframes_item_data)

            keyframes.append(keyframes_item)

        shot_name = d.pop("shotName", UNSET)

        open_file_panel_data = cls(
            id=id,
            index=index,
            revision_id=revision_id,
            asset_id=asset_id,
            is_animated=is_animated,
            annotation_asset_id=annotation_asset_id,
            shot_id=shot_id,
            source_file=source_file,
            dialogue=dialogue,
            origin_sbp=origin_sbp,
            keyframes=keyframes,
            shot_name=shot_name,
        )

        open_file_panel_data.additional_properties = d
        return open_file_panel_data

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
