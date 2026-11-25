from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.project_details_metadata_dto_episode import ProjectDetailsMetadataDtoEpisode
  from ..models.project_details_metadata_dto_sequence import ProjectDetailsMetadataDtoSequence
  from ..models.project_details_metadata_dto_sequence_revision import ProjectDetailsMetadataDtoSequenceRevision
  from ..models.project_details_metadata_dto_show import ProjectDetailsMetadataDtoShow





T = TypeVar("T", bound="ProjectDetailsMetadataDto")



@_attrs_define
class ProjectDetailsMetadataDto:
    """ 
        Attributes:
            show (ProjectDetailsMetadataDtoShow | Unset): Arbitrary key-value metadata to merge into the entity. Each value
                must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            episode (ProjectDetailsMetadataDtoEpisode | Unset): Arbitrary key-value metadata to merge into the entity. Each
                value must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            sequence (ProjectDetailsMetadataDtoSequence | Unset): Arbitrary key-value metadata to merge into the entity.
                Each value must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
            sequence_revision (ProjectDetailsMetadataDtoSequenceRevision | Unset): Arbitrary key-value metadata to merge
                into the entity. Each value must be a string, or `null` to delete that key.

                **Note:** Keys in this dictionary are **case-sensitive**.

                Best practice: Use namespaced keys to avoid conflicts with other extensions (e.g., `vendor.plugin:key`).
                Example: {'com.myextension:status': 'inprogress', 'com.myextension:tag': None}.
     """

    show: ProjectDetailsMetadataDtoShow | Unset = UNSET
    episode: ProjectDetailsMetadataDtoEpisode | Unset = UNSET
    sequence: ProjectDetailsMetadataDtoSequence | Unset = UNSET
    sequence_revision: ProjectDetailsMetadataDtoSequenceRevision | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.project_details_metadata_dto_episode import ProjectDetailsMetadataDtoEpisode # noqa: PLC0415
        from ..models.project_details_metadata_dto_sequence import ProjectDetailsMetadataDtoSequence # noqa: PLC0415
        from ..models.project_details_metadata_dto_sequence_revision import ProjectDetailsMetadataDtoSequenceRevision # noqa: PLC0415
        from ..models.project_details_metadata_dto_show import ProjectDetailsMetadataDtoShow # noqa: PLC0415
        show: dict[str, Any] | Unset = UNSET
        if not isinstance(self.show, Unset):
            show = self.show.to_dict()

        episode: dict[str, Any] | Unset = UNSET
        if not isinstance(self.episode, Unset):
            episode = self.episode.to_dict()

        sequence: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sequence, Unset):
            sequence = self.sequence.to_dict()

        sequence_revision: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sequence_revision, Unset):
            sequence_revision = self.sequence_revision.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if show is not UNSET:
            field_dict["show"] = show
        if episode is not UNSET:
            field_dict["episode"] = episode
        if sequence is not UNSET:
            field_dict["sequence"] = sequence
        if sequence_revision is not UNSET:
            field_dict["sequenceRevision"] = sequence_revision

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_details_metadata_dto_episode import ProjectDetailsMetadataDtoEpisode # noqa: PLC0415
        from ..models.project_details_metadata_dto_sequence import ProjectDetailsMetadataDtoSequence # noqa: PLC0415
        from ..models.project_details_metadata_dto_sequence_revision import ProjectDetailsMetadataDtoSequenceRevision # noqa: PLC0415
        from ..models.project_details_metadata_dto_show import ProjectDetailsMetadataDtoShow # noqa: PLC0415
        d = dict(src_dict)
        _show = d.pop("show", UNSET)
        show: ProjectDetailsMetadataDtoShow | Unset
        if isinstance(_show,  Unset) or _show is None:
            show = UNSET
        else:
            show = ProjectDetailsMetadataDtoShow.from_dict(_show)




        _episode = d.pop("episode", UNSET)
        episode: ProjectDetailsMetadataDtoEpisode | Unset
        if isinstance(_episode,  Unset) or _episode is None:
            episode = UNSET
        else:
            episode = ProjectDetailsMetadataDtoEpisode.from_dict(_episode)




        _sequence = d.pop("sequence", UNSET)
        sequence: ProjectDetailsMetadataDtoSequence | Unset
        if isinstance(_sequence,  Unset) or _sequence is None:
            sequence = UNSET
        else:
            sequence = ProjectDetailsMetadataDtoSequence.from_dict(_sequence)




        _sequence_revision = d.pop("sequenceRevision", UNSET)
        sequence_revision: ProjectDetailsMetadataDtoSequenceRevision | Unset
        if isinstance(_sequence_revision,  Unset) or _sequence_revision is None:
            sequence_revision = UNSET
        else:
            sequence_revision = ProjectDetailsMetadataDtoSequenceRevision.from_dict(_sequence_revision)




        project_details_metadata_dto = cls(
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )


        project_details_metadata_dto.additional_properties = d
        return project_details_metadata_dto

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
