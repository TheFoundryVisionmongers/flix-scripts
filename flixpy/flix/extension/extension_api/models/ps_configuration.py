from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PsConfiguration")


@_attrs_define
class PsConfiguration:
    """
    Attributes:
        always_open_source_file (bool):
        open_behaviour (str):
        send_annotation_as_layer (bool):
    """

    always_open_source_file: bool
    open_behaviour: str
    send_annotation_as_layer: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        always_open_source_file = self.always_open_source_file
        open_behaviour = self.open_behaviour
        send_annotation_as_layer = self.send_annotation_as_layer

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alwaysOpenSourceFile": always_open_source_file,
                "openBehaviour": open_behaviour,
                "sendAnnotationAsLayer": send_annotation_as_layer,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        always_open_source_file = d.pop("alwaysOpenSourceFile")

        open_behaviour = d.pop("openBehaviour")

        send_annotation_as_layer = d.pop("sendAnnotationAsLayer")

        ps_configuration = cls(
            always_open_source_file=always_open_source_file,
            open_behaviour=open_behaviour,
            send_annotation_as_layer=send_annotation_as_layer,
        )

        ps_configuration.additional_properties = d
        return ps_configuration

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
