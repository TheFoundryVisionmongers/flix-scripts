from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ViewportRequest")


@_attrs_define
class ViewportRequest:
    """
    Attributes:
        width (float): Width is the width of the media in pixels, dictating the scale of horizontal camera movements.
        height (float): Height is the height of the media in pixels, dictating the scale of vertical camera movements.
        scale (float): Stretch (Scale in API) specifies how much the source artwork has been stretched within this
            media.
            More specifically, it is the inverse stretch, such that if the source artwork has a width of 1000
            while the bounding box of the same artwork within this media has a width of 2000, the stretch will be
            1000 / 2000 = 0.5.
        offset_x (float): OffsetX is the horizontal offset of the source artwork within this media, if this media has
            been padded.
            In particular, it is the horizontal distance from the centre of this media to the centre of the source artwork.
            Specified in terms of the pixel space of the source artwork; calculate OffsetX / Stretch to get
            the offset in pixels within this me.
        offset_y (float): OffsetY is the vertical offset of the source artwork within this media, if this media has been
            padded.
            In particular, it is the vertical distance from the centre of this media to the centre of the source artwork.
            Specified in terms of the pixel space of the source artwork; calculate OffsetY / Stretch to get
            the offset in pixels within this media.
    """

    width: float
    height: float
    scale: float
    offset_x: float
    offset_y: float
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        width = self.width
        height = self.height
        scale = self.scale
        offset_x = self.offset_x
        offset_y = self.offset_y

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "width": width,
                "height": height,
                "scale": scale,
                "offsetX": offset_x,
                "offsetY": offset_y,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        width = d.pop("width")

        height = d.pop("height")

        scale = d.pop("scale")

        offset_x = d.pop("offsetX")

        offset_y = d.pop("offsetY")

        viewport_request = cls(
            width=width,
            height=height,
            scale=scale,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        viewport_request.additional_properties = d
        return viewport_request

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
