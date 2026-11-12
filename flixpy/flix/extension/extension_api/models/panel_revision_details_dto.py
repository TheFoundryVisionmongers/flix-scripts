import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.keyframe import Keyframe
    from ..models.panel_revision_details_dto_metadata import (
        PanelRevisionDetailsDtoMetadata,
    )
    from ..models.panel_revision_details_dto_origin_sbp import (
        PanelRevisionDetailsDtoOriginSbp,
    )


T = TypeVar("T", bound="PanelRevisionDetailsDto")


@_attrs_define
class PanelRevisionDetailsDto:
    """
    Attributes:
        panel_id (float): The identifier of this panel.
        revision_id (float): The panel revision of this panel instance.
        panel_position (float): The position of the panel in the sequence revision it belongs to.
        asset_id (float): The identifier for the asset associated with this panel.
        created_date (datetime.datetime): The date the panel was created.
        revision_date (datetime.datetime): The date at which this panel revision was created.
        owner (str): The user that originally created this "panel revision".
        show_id (float): The show this panel belongs to.
        sequence_id (float): The sequence this panel belongs to.
        hidden (bool): Flag that indicates if a panel has been hidden in a sequence revision.
        duration (float): The duration of the panel in frames.
        trim_in_frame (float): TrimInFrame is the trim in of this panel revision in a given sequence revision if this is
            an animated panel.
        trim_out_frame (float): TrimOutFrame is the trim out of this panel revision in a given sequence revision if this
            is an animated panel.
        in_ (float): The sequence frame in which this panel begins.
        out (float): The sequence frame in which this panel ends.
        layer_transform (bool): Whether the panel revision had a layer transform applied to it in Storyboard Pro.
        dialogue (str): This dialogue associated with this panel.
        origin_sbp (PanelRevisionDetailsDtoOriginSbp): Contains information about panel revisions imported from
            Storyboard Pro.
            This is for internal use by the Storyboard Pro extension and might be removed in the future without notice.
        keyframes (List['Keyframe']): The camera move keyframes on this panel revisions.
        origin (str): Where the panel comes from e.g. "manual import".
        shot_name (str): Sequence Revision shot this panel belongs to.
        metadata (PanelRevisionDetailsDtoMetadata): Metadata of the panel revision. Can be updated via GRC API by
            extensions.
    """

    panel_id: float
    revision_id: float
    panel_position: float
    asset_id: float
    created_date: datetime.datetime
    revision_date: datetime.datetime
    owner: str
    show_id: float
    sequence_id: float
    hidden: bool
    duration: float
    trim_in_frame: float
    trim_out_frame: float
    in_: float
    out: float
    layer_transform: bool
    dialogue: str
    origin_sbp: "PanelRevisionDetailsDtoOriginSbp"
    keyframes: List["Keyframe"]
    origin: str
    shot_name: str
    metadata: "PanelRevisionDetailsDtoMetadata"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        panel_id = self.panel_id
        revision_id = self.revision_id
        panel_position = self.panel_position
        asset_id = self.asset_id
        created_date = self.created_date.isoformat()

        revision_date = self.revision_date.isoformat()

        owner = self.owner
        show_id = self.show_id
        sequence_id = self.sequence_id
        hidden = self.hidden
        duration = self.duration
        trim_in_frame = self.trim_in_frame
        trim_out_frame = self.trim_out_frame
        in_ = self.in_
        out = self.out
        layer_transform = self.layer_transform
        dialogue = self.dialogue
        origin_sbp = self.origin_sbp.to_dict()

        keyframes = []
        for keyframes_item_data in self.keyframes:
            keyframes_item = keyframes_item_data.to_dict()

            keyframes.append(keyframes_item)

        origin = self.origin
        shot_name = self.shot_name
        metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "panelId": panel_id,
                "revisionId": revision_id,
                "panelPosition": panel_position,
                "assetId": asset_id,
                "createdDate": created_date,
                "revisionDate": revision_date,
                "owner": owner,
                "showId": show_id,
                "sequenceId": sequence_id,
                "hidden": hidden,
                "duration": duration,
                "trimInFrame": trim_in_frame,
                "trimOutFrame": trim_out_frame,
                "in": in_,
                "out": out,
                "layerTransform": layer_transform,
                "dialogue": dialogue,
                "originSbp": origin_sbp,
                "keyframes": keyframes,
                "origin": origin,
                "shotName": shot_name,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.keyframe import Keyframe
        from ..models.panel_revision_details_dto_metadata import (
            PanelRevisionDetailsDtoMetadata,
        )
        from ..models.panel_revision_details_dto_origin_sbp import (
            PanelRevisionDetailsDtoOriginSbp,
        )

        d = src_dict.copy()
        panel_id = d.pop("panelId")

        revision_id = d.pop("revisionId")

        panel_position = d.pop("panelPosition")

        asset_id = d.pop("assetId")

        created_date = isoparse(d.pop("createdDate"))

        revision_date = isoparse(d.pop("revisionDate"))

        owner = d.pop("owner")

        show_id = d.pop("showId")

        sequence_id = d.pop("sequenceId")

        hidden = d.pop("hidden")

        duration = d.pop("duration")

        trim_in_frame = d.pop("trimInFrame")

        trim_out_frame = d.pop("trimOutFrame")

        in_ = d.pop("in")

        out = d.pop("out")

        layer_transform = d.pop("layerTransform")

        dialogue = d.pop("dialogue")

        origin_sbp = PanelRevisionDetailsDtoOriginSbp.from_dict(d.pop("originSbp"))

        keyframes = []
        _keyframes = d.pop("keyframes")
        for keyframes_item_data in _keyframes:
            keyframes_item = Keyframe.from_dict(keyframes_item_data)

            keyframes.append(keyframes_item)

        origin = d.pop("origin")

        shot_name = d.pop("shotName")

        metadata = PanelRevisionDetailsDtoMetadata.from_dict(d.pop("metadata"))

        panel_revision_details_dto = cls(
            panel_id=panel_id,
            revision_id=revision_id,
            panel_position=panel_position,
            asset_id=asset_id,
            created_date=created_date,
            revision_date=revision_date,
            owner=owner,
            show_id=show_id,
            sequence_id=sequence_id,
            hidden=hidden,
            duration=duration,
            trim_in_frame=trim_in_frame,
            trim_out_frame=trim_out_frame,
            in_=in_,
            out=out,
            layer_transform=layer_transform,
            dialogue=dialogue,
            origin_sbp=origin_sbp,
            keyframes=keyframes,
            origin=origin,
            shot_name=shot_name,
            metadata=metadata,
        )

        panel_revision_details_dto.additional_properties = d
        return panel_revision_details_dto

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
