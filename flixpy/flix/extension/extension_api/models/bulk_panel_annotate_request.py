from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BulkPanelAnnotateRequest")


@_attrs_define
class BulkPanelAnnotateRequest:
    """
    Attributes:
        start_index (int): (Optional) The index from which to annotate panels. Defaults to currently selected panel.
            Example: 3.
        paths (List[str]): The file paths to be uploaded as panel annotations. Example:
            ['/path/to/file/1.psd','/path/to/file/2.psd'].
        origin (str): The origin of the incoming annotation. Example: Photoshop.
    """

    start_index: int
    paths: List[str]
    origin: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start_index = self.start_index
        paths = self.paths

        origin = self.origin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startIndex": start_index,
                "paths": paths,
                "origin": origin,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start_index = d.pop("startIndex")

        paths = cast(List[str], d.pop("paths"))

        origin = d.pop("origin")

        bulk_panel_annotate_request = cls(
            start_index=start_index,
            paths=paths,
            origin=origin,
        )

        bulk_panel_annotate_request.additional_properties = d
        return bulk_panel_annotate_request

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
