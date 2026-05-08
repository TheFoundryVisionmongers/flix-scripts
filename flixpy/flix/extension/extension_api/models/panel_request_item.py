from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.keyframe_request import KeyframeRequest
    from ..models.panel_request_item_origin_sbp import PanelRequestItemOriginSbp


T = TypeVar("T", bound="PanelRequestItem")


@_attrs_define
class PanelRequestItem:
    """
    Attributes:
        path (str): The file path to upload. Example: /path/to/file/1.psd.
        panel_id (Union[Unset, int]): The ID of the panel that should be updated. Example: 15.
        duration (Union[Unset, int]): Duration is the number of frames this instance of [PanelRevision] has, within this
            [Shot].
        trim_in_frame (Union[Unset, int]): TrimInFrame is the trim in of this panel revision in a given sequence
            revision if this is an animated panel.
        trim_out_frame (Union[Unset, int]): TrimOutFrame is the trim out of this panel revision in a given sequence
            revision if this is an animated panel.
        keyframes (Union[Unset, List['KeyframeRequest']]): The camera move keyframes on this panel revisions.
        origin_sbp (Union[Unset, PanelRequestItemOriginSbp]): Contains information about panel revisions imported from
            Storyboard Pro.
            This is for internal use by the Storyboard Pro extension and might be removed in the future without notice.
        source_media (Union[Unset, str]): This is used to upload a MOV file that will be used as the source media for
            the panel preview.
        dialogue (Union[Unset, str]): This is dialogue text that will be associated with the panel.
        layer_transform (Union[Unset, bool]): This indicates whether panel has layer transform.
        shot_name (Union[Unset, str]): The name of the shot this panel belongs to.
            When specified, a shot with the given name will be created and this panel will be added to it.
            If the name already exists within the sequence, the request will be rejected with a 400 Bad Request response.
            If not provided, the panel will be added to an existing shot based on the target insert index. Example: Shot
            001.
    """

    path: str
    panel_id: Union[Unset, int] = UNSET
    duration: Union[Unset, int] = UNSET
    trim_in_frame: Union[Unset, int] = UNSET
    trim_out_frame: Union[Unset, int] = UNSET
    keyframes: Union[Unset, List["KeyframeRequest"]] = UNSET
    origin_sbp: Union[Unset, "PanelRequestItemOriginSbp"] = UNSET
    source_media: Union[Unset, str] = UNSET
    dialogue: Union[Unset, str] = UNSET
    layer_transform: Union[Unset, bool] = UNSET
    shot_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        panel_id = self.panel_id
        duration = self.duration
        trim_in_frame = self.trim_in_frame
        trim_out_frame = self.trim_out_frame
        keyframes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.keyframes, Unset):
            keyframes = []
            for keyframes_item_data in self.keyframes:
                keyframes_item = keyframes_item_data.to_dict()

                keyframes.append(keyframes_item)

        origin_sbp: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.origin_sbp, Unset):
            origin_sbp = self.origin_sbp.to_dict()

        source_media = self.source_media
        dialogue = self.dialogue
        layer_transform = self.layer_transform
        shot_name = self.shot_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
            }
        )
        if panel_id is not UNSET:
            field_dict["panelId"] = panel_id
        if duration is not UNSET:
            field_dict["duration"] = duration
        if trim_in_frame is not UNSET:
            field_dict["trimInFrame"] = trim_in_frame
        if trim_out_frame is not UNSET:
            field_dict["trimOutFrame"] = trim_out_frame
        if keyframes is not UNSET:
            field_dict["keyframes"] = keyframes
        if origin_sbp is not UNSET:
            field_dict["originSbp"] = origin_sbp
        if source_media is not UNSET:
            field_dict["sourceMedia"] = source_media
        if dialogue is not UNSET:
            field_dict["dialogue"] = dialogue
        if layer_transform is not UNSET:
            field_dict["layerTransform"] = layer_transform
        if shot_name is not UNSET:
            field_dict["shotName"] = shot_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.keyframe_request import KeyframeRequest
        from ..models.panel_request_item_origin_sbp import PanelRequestItemOriginSbp

        d = src_dict.copy()
        path = d.pop("path")

        panel_id = d.pop("panelId", UNSET)

        duration = d.pop("duration", UNSET)

        trim_in_frame = d.pop("trimInFrame", UNSET)

        trim_out_frame = d.pop("trimOutFrame", UNSET)

        keyframes = []
        _keyframes = d.pop("keyframes", UNSET)
        for keyframes_item_data in _keyframes or []:
            keyframes_item = KeyframeRequest.from_dict(keyframes_item_data)

            keyframes.append(keyframes_item)

        _origin_sbp = d.pop("originSbp", UNSET)
        origin_sbp: Union[Unset, PanelRequestItemOriginSbp]
        if isinstance(_origin_sbp, Unset):
            origin_sbp = UNSET
        else:
            origin_sbp = PanelRequestItemOriginSbp.from_dict(_origin_sbp)

        source_media = d.pop("sourceMedia", UNSET)

        dialogue = d.pop("dialogue", UNSET)

        layer_transform = d.pop("layerTransform", UNSET)

        shot_name = d.pop("shotName", UNSET)

        panel_request_item = cls(
            path=path,
            panel_id=panel_id,
            duration=duration,
            trim_in_frame=trim_in_frame,
            trim_out_frame=trim_out_frame,
            keyframes=keyframes,
            origin_sbp=origin_sbp,
            source_media=source_media,
            dialogue=dialogue,
            layer_transform=layer_transform,
            shot_name=shot_name,
        )

        panel_request_item.additional_properties = d
        return panel_request_item

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
