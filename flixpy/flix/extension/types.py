import dataclasses

from .extension_api import models

from ..lib import types as flix_types


__all__ = [
    "SourceFile",
    "ProjectDetails",
]


@dataclasses.dataclass
class SourceFile:
    id: str
    path: str


@dataclasses.dataclass
class ProjectDetails:
    show: flix_types.Show | None
    episode: flix_types.Episode | None
    sequence: flix_types.Sequence | None
    sequence_revision: flix_types.SequenceRevision | None

    @classmethod
    def from_model(cls, data: models.ProjectDetailsDto) -> "ProjectDetails":
        show: flix_types.Show | None = None
        episode: flix_types.Episode | None = None
        sequence: flix_types.Sequence | None = None
        sequence_revision: flix_types.SequenceRevision | None = None

        if data.show is not None:
            show = flix_types.Show(
                show_id=int(data.show.id),
                tracking_code=data.show.tracking_code,
                aspect_ratio=data.show.aspect_ratio,
                title=data.show.title or "",
                _client=None,
            )

            if data.episode is not None:
                episode = flix_types.Episode(
                    episode_id=int(data.episode.id),
                    tracking_code=data.episode.tracking_code,
                    created_date=data.episode.created_date,
                    title=data.episode.title or "",
                    owner=flix_types.User(data.episode.owner, _client=None),
                    _show=show,
                    _client=None,
                )

            if data.sequence is not None:
                sequence = flix_types.Sequence(
                    sequence_id=int(data.sequence.id),
                    tracking_code=data.sequence.tracking_code,
                    created_date=data.sequence.created_date,
                    description=data.sequence.title or "",
                    owner=flix_types.User(data.sequence.owner, _client=None),
                    _show=show,
                    _episode=episode,
                    _client=None,
                )

                if data.sequence_revision is not None:
                    sequence_revision = flix_types.SequenceRevision(
                        revision_number=int(data.sequence_revision.id),
                        published=data.sequence_revision.published,
                        comment=data.sequence_revision.comment or "",
                        created_date=data.sequence_revision.created_date,
                        owner=flix_types.User(data.sequence_revision.owner or "", _client=None),
                        _sequence=sequence,
                        _client=None,
                    )

        return cls(
            show=show,
            episode=episode,
            sequence=sequence,
            sequence_revision=sequence_revision,
        )
