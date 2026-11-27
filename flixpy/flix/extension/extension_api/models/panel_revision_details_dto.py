from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.keyframe_dto import KeyframeDto
  from ..models.panel_revision_details_dto_metadata import PanelRevisionDetailsDtoMetadata
  from ..models.panel_revision_details_dto_origin_sbp_type_0 import PanelRevisionDetailsDtoOriginSbpType0





T = TypeVar("T", bound="PanelRevisionDetailsDto")



@_attrs_define
class PanelRevisionDetailsDto:
    """ 
        Attributes:
            panel_id (int): The identifier of this panel.
            revision_id (int): The panel revision of this panel instance.
            panel_position (int): The position of the panel in the sequence revision it belongs to.
            asset_id (int): The identifier for the asset associated with this panel.
            show_id (int): The show this panel belongs to.
            sequence_id (int): The sequence this panel belongs to.
            trim_in_frame (int): TrimInFrame is the trim in of this panel revision in a given sequence revision if this is
                an animated panel.
            trim_out_frame (int): TrimOutFrame is the trim out of this panel revision in a given sequence revision if this
                is an animated panel.
            metadata (PanelRevisionDetailsDtoMetadata): Arbitrary key-value metadata to merge into the entity. Each value
                must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            created_date (datetime.datetime): The date the panel was created.
            revision_date (datetime.datetime): The date at which this panel revision was created.
            owner (str): The user that originally created this "panel revision".
            hidden (bool): Flag that indicates if a panel has been hidden in a sequence revision.
            duration (float): The duration of the panel in frames.
            layer_transform (bool): Whether the panel revision had a layer transform applied to it in Storyboard Pro.
            dialogue (str): This dialogue associated with this panel.
            keyframes (list[KeyframeDto]): The camera move keyframes on this panel revisions.
            origin (str): Where the panel comes from e.g. "manual import".
            shot_name (str): Sequence Revision shot this panel belongs to.
            origin_sbp (None | PanelRevisionDetailsDtoOriginSbpType0 | Unset): Contains information about panel revisions
                imported from Storyboard Pro.
                This is for internal use by the Storyboard Pro extension and might be removed in the future without notice.
     """

    panel_id: int
    revision_id: int
    panel_position: int
    asset_id: int
    show_id: int
    sequence_id: int
    trim_in_frame: int
    trim_out_frame: int
    metadata: PanelRevisionDetailsDtoMetadata
    created_date: datetime.datetime
    revision_date: datetime.datetime
    owner: str
    hidden: bool
    duration: float
    layer_transform: bool
    dialogue: str
    keyframes: list[KeyframeDto]
    origin: str
    shot_name: str
    origin_sbp: None | PanelRevisionDetailsDtoOriginSbpType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.keyframe_dto import KeyframeDto # noqa: PLC0415
        from ..models.panel_revision_details_dto_metadata import PanelRevisionDetailsDtoMetadata # noqa: PLC0415
        from ..models.panel_revision_details_dto_origin_sbp_type_0 import PanelRevisionDetailsDtoOriginSbpType0 # noqa: PLC0415
        panel_id = self.panel_id

        revision_id = self.revision_id

        panel_position = self.panel_position

        asset_id = self.asset_id

        show_id = self.show_id

        sequence_id = self.sequence_id

        trim_in_frame = self.trim_in_frame

        trim_out_frame = self.trim_out_frame

        metadata = self.metadata.to_dict()

        created_date = self.created_date.isoformat()

        revision_date = self.revision_date.isoformat()

        owner = self.owner

        hidden = self.hidden

        duration = self.duration

        layer_transform = self.layer_transform

        dialogue = self.dialogue

        keyframes = []
        for keyframes_item_data in self.keyframes:
            keyframes_item = keyframes_item_data.to_dict()
            keyframes.append(keyframes_item)



        origin = self.origin

        shot_name = self.shot_name

        origin_sbp: dict[str, Any] | None | Unset
        if isinstance(self.origin_sbp, Unset):
            origin_sbp = UNSET
        elif isinstance(self.origin_sbp, PanelRevisionDetailsDtoOriginSbpType0):
            origin_sbp = self.origin_sbp.to_dict()
        else:
            origin_sbp = self.origin_sbp


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "panelId": panel_id,
            "revisionId": revision_id,
            "panelPosition": panel_position,
            "assetId": asset_id,
            "showId": show_id,
            "sequenceId": sequence_id,
            "trimInFrame": trim_in_frame,
            "trimOutFrame": trim_out_frame,
            "metadata": metadata,
            "createdDate": created_date,
            "revisionDate": revision_date,
            "owner": owner,
            "hidden": hidden,
            "duration": duration,
            "layerTransform": layer_transform,
            "dialogue": dialogue,
            "keyframes": keyframes,
            "origin": origin,
            "shotName": shot_name,
        })
        if origin_sbp is not UNSET:
            field_dict["originSbp"] = origin_sbp

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.keyframe_dto import KeyframeDto # noqa: PLC0415
        from ..models.panel_revision_details_dto_metadata import PanelRevisionDetailsDtoMetadata # noqa: PLC0415
        from ..models.panel_revision_details_dto_origin_sbp_type_0 import PanelRevisionDetailsDtoOriginSbpType0 # noqa: PLC0415
        d = dict(src_dict)
        panel_id = d.pop("panelId")

        revision_id = d.pop("revisionId")

        panel_position = d.pop("panelPosition")

        asset_id = d.pop("assetId")

        show_id = d.pop("showId")

        sequence_id = d.pop("sequenceId")

        trim_in_frame = d.pop("trimInFrame")

        trim_out_frame = d.pop("trimOutFrame")

        metadata = PanelRevisionDetailsDtoMetadata.from_dict(d.pop("metadata"))




        created_date = datetime.datetime.fromisoformat(d.pop("createdDate"))




        revision_date = datetime.datetime.fromisoformat(d.pop("revisionDate"))




        owner = d.pop("owner")

        hidden = d.pop("hidden")

        duration = d.pop("duration")

        layer_transform = d.pop("layerTransform")

        dialogue = d.pop("dialogue")

        keyframes = []
        _keyframes = d.pop("keyframes")
        for keyframes_item_data in (_keyframes):
            keyframes_item = KeyframeDto.from_dict(keyframes_item_data)



            keyframes.append(keyframes_item)


        origin = d.pop("origin")

        shot_name = d.pop("shotName")

        def _parse_origin_sbp(data: object) -> None | PanelRevisionDetailsDtoOriginSbpType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                origin_sbp_type_0 = PanelRevisionDetailsDtoOriginSbpType0.from_dict(data)



                return origin_sbp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PanelRevisionDetailsDtoOriginSbpType0 | Unset, data)

        origin_sbp = _parse_origin_sbp(d.pop("originSbp", UNSET))


        panel_revision_details_dto = cls(
            panel_id=panel_id,
            revision_id=revision_id,
            panel_position=panel_position,
            asset_id=asset_id,
            show_id=show_id,
            sequence_id=sequence_id,
            trim_in_frame=trim_in_frame,
            trim_out_frame=trim_out_frame,
            metadata=metadata,
            created_date=created_date,
            revision_date=revision_date,
            owner=owner,
            hidden=hidden,
            duration=duration,
            layer_transform=layer_transform,
            dialogue=dialogue,
            keyframes=keyframes,
            origin=origin,
            shot_name=shot_name,
            origin_sbp=origin_sbp,
        )


        panel_revision_details_dto.additional_properties = d
        return panel_revision_details_dto

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
