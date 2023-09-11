from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.panel_request_source_file import PanelRequestSourceFile


T = TypeVar("T", bound="PanelRequest")


@_attrs_define
class PanelRequest:
    """
    Attributes:
        paths (List[str]): The file paths to upload
        source_file (Union[Unset, PanelRequestSourceFile]):
        start_index (Union[Unset, float]): the index at which to insert the created panels
    """

    paths: List[str]
    source_file: Union[Unset, "PanelRequestSourceFile"] = UNSET
    start_index: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        paths = self.paths

        source_file: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.source_file, Unset):
            source_file = self.source_file.to_dict()

        start_index = self.start_index

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paths": paths,
            }
        )
        if source_file is not UNSET:
            field_dict["sourceFile"] = source_file
        if start_index is not UNSET:
            field_dict["startIndex"] = start_index

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.panel_request_source_file import PanelRequestSourceFile

        d = src_dict.copy()
        paths = cast(List[str], d.pop("paths"))

        _source_file = d.pop("sourceFile", UNSET)
        source_file: Union[Unset, PanelRequestSourceFile]
        if isinstance(_source_file, Unset):
            source_file = UNSET
        else:
            source_file = PanelRequestSourceFile.from_dict(_source_file)

        start_index = d.pop("startIndex", UNSET)

        panel_request = cls(
            paths=paths,
            source_file=source_file,
            start_index=start_index,
        )

        panel_request.additional_properties = d
        return panel_request

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
