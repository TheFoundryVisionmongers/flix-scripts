from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.viewport_dto import ViewportDto





T = TypeVar("T", bound="KeyframeDto")



@_attrs_define
class KeyframeDto:
    """ 
        Attributes:
            anchor_point_horizontal (int): The horizontal value of the point that CenterHoriz, CenterVert and Rotation are
                applied to,
                specified as an offset from the viewport centre in fractions of the horizontal viewport resolution.
                A value of 0 is the centre of the viewport, while a value of -0.5 is the left edge of the viewport. Default: 0.
            anchor_point_vertical (int): The vertical value of the point that CenterHoriz, CenterVert and Rotation are
                applied to,
                specified as an offset from the viewport centre in fractions of the vertical viewport resolution.
                A value of 0 is the centre of the viewport, while a value of -0.5 is the top edge of the viewport. Default: 0.
            center_horizontal (int): The horizontal position of the camera in fractions of the viewport width, relative to
                the centre of the viewport.
                A positive value means the camera is positioned to the left of the viewport centre. Default: 0.
            center_vertical (int): The vertical position of the camera in fractions of the viewport height, relative to the
                centre of the viewport.
                A positive value means the camera is positioned above the viewport centre. Default: 0.
            rotation (int): How much to rotate the image clockwise in degrees. Default: 0.
            scale (int): A vertical and horizontal scale, 100 meaning no scaling. Default: 0.
            start_key (int): The frame of the panel revision that the information of this keyframe relates to, starting at
                0. Default: 0.
            viewport (ViewportDto | Unset):
     """

    anchor_point_horizontal: int = 0
    anchor_point_vertical: int = 0
    center_horizontal: int = 0
    center_vertical: int = 0
    rotation: int = 0
    scale: int = 0
    start_key: int = 0
    viewport: ViewportDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.viewport_dto import ViewportDto # noqa: PLC0415
        anchor_point_horizontal = self.anchor_point_horizontal

        anchor_point_vertical = self.anchor_point_vertical

        center_horizontal = self.center_horizontal

        center_vertical = self.center_vertical

        rotation = self.rotation

        scale = self.scale

        start_key = self.start_key

        viewport: dict[str, Any] | Unset = UNSET
        if not isinstance(self.viewport, Unset):
            viewport = self.viewport.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "anchorPointHorizontal": anchor_point_horizontal,
            "anchorPointVertical": anchor_point_vertical,
            "centerHorizontal": center_horizontal,
            "centerVertical": center_vertical,
            "rotation": rotation,
            "scale": scale,
            "startKey": start_key,
        })
        if viewport is not UNSET:
            field_dict["viewport"] = viewport

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.viewport_dto import ViewportDto # noqa: PLC0415
        d = dict(src_dict)
        anchor_point_horizontal = d.pop("anchorPointHorizontal")

        anchor_point_vertical = d.pop("anchorPointVertical")

        center_horizontal = d.pop("centerHorizontal")

        center_vertical = d.pop("centerVertical")

        rotation = d.pop("rotation")

        scale = d.pop("scale")

        start_key = d.pop("startKey")

        _viewport = d.pop("viewport", UNSET)
        viewport: ViewportDto | Unset
        if isinstance(_viewport,  Unset) or _viewport is None:
            viewport = UNSET
        else:
            viewport = ViewportDto.from_dict(_viewport)




        keyframe_dto = cls(
            anchor_point_horizontal=anchor_point_horizontal,
            anchor_point_vertical=anchor_point_vertical,
            center_horizontal=center_horizontal,
            center_vertical=center_vertical,
            rotation=rotation,
            scale=scale,
            start_key=start_key,
            viewport=viewport,
        )


        keyframe_dto.additional_properties = d
        return keyframe_dto

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
