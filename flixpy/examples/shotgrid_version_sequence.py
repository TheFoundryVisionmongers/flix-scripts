"""Demonstrates automatically creating a new ShotGrid version on a publish to editorial.

This example shows how to use webhooks to listen for publishes from Flix to editorial
and automatically create a new version in ShotGrid. The new version will be linked to a sequence
and have a QuickTime exported from the Flix sequence revision attached.

The code assumes that you have attached the IDs of your ShotGrid project and sequence
to the metadata of your Flix show and sequence respectively, in the form of a ``shotgrid_id`` field.
See ``shotgrid_create_show.py`` for an example on how to do that.

Additionally, you must have registered a webhook with the Flix Server, either using
the ``/webhook`` endpoint or the ``flix webhook`` command from the Flix SDK.
The example assumes that you have registered a TCP webhook with the URL
``http://<hostname>:8888/events/shotgrid`` with the ``Publish to editorial``
event enabled.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import tempfile
from typing import TYPE_CHECKING, Literal, TypedDict, cast

import flix
import shotgun_api3  # type: ignore[import-untyped]
from typing_extensions import NotRequired

if TYPE_CHECKING:
    import pathlib

logger = logging.getLogger(__name__)

# ShotGrid credentials to create the new version
SHOTGRID_BASE_URL = "https://yourstudio.shotgunstudio.com/"
SHOTGRID_USERNAME = "user.name@example.com"
SHOTGRID_PASSWORD = "hunter2"

# Flix server and credentials for exporting the QuickTime
FLIX_HOSTNAME = "localhost"
FLIX_PORT = 8080
FLIX_API_KEY = os.getenv("FLIX_API_KEY")
FLIX_API_SECRET = os.getenv("FLIX_API_SECRET")

# create long-lived ShotGrid client so we don't need
# to create a new one for each event
SG = shotgun_api3.Shotgun(SHOTGRID_BASE_URL, login=SHOTGRID_USERNAME, password=SHOTGRID_PASSWORD)


# optional: typed schemas for our ShotGrid entities for use with Mypy/Pyright
class BaseSchema(TypedDict):
    """Common base schema for entities with IDs."""

    id: int


class ShotgridProject(BaseSchema):
    """Typed schema for existing ShotGrid projects."""

    type: Literal["Project"]


class ShotgridSequence(BaseSchema):
    """Typed schema for existing ShotGrid sequences."""

    type: Literal["Sequence"]


class ShotgridVersion(TypedDict):
    """Typed schema for new ShotGrid versions."""

    project: ShotgridProject
    entity: NotRequired[ShotgridSequence]
    code: str
    description: NotRequired[str | None]


class ShotgridVersionWithID(BaseSchema, ShotgridVersion):
    """Typed schema for existing ShotGrid versions."""

    type: Literal["Project"]


# specify the HTTP endpoint for your webhook, as well as
# the secret you got when registering the webhook with the server
@flix.webhook(path="/events/shotgrid", secret="3a990b93-d661-4540-80ce-f4a421c528df")
async def on_event(event: flix.WebhookEvent) -> None:
    """Handle all events enabled for this webhook."""
    logger.info("Got event: %s", event)


@on_event.handle(flix.PublishEditorialEvent)
async def on_publish(event: flix.PublishEditorialEvent) -> None:
    """Handle editorial publish events."""
    logger.info(
        "Got publish event for show %s, sequence %s, revision %s",
        event.show.tracking_code,
        event.sequence.tracking_code,
        event.sequence_revision.revision_number,
    )

    # export QuickTime - requires that we have passed client_options
    # to flix.run_webhook_server to ensure that we have an authenticated client
    logger.info("Exporting QuickTime...")
    quicktime_mo = await event.sequence_revision.export_quicktime()

    # create a temporary directory for downloading the QuickTime
    with tempfile.TemporaryDirectory() as dir_path:
        logger.info("Downloading QuickTime...")
        quicktime_path = await quicktime_mo.download_to(dir_path)

        # create the new ShotGrid version and upload the QuickTime
        # optional: run on a different thread to prevent the synchronous
        # ShotGrid calls from blocking processing of other events
        await asyncio.get_running_loop().run_in_executor(
            None, _upload_to_shotgrid, event, quicktime_path
        )


def _upload_to_shotgrid(event: flix.PublishEditorialEvent, quicktime_path: pathlib.Path) -> None:
    """Create a new ShotGrid version from a Flix sequence revision and attach a QuickTime."""
    logger.info("Creating new ShotGrid version...")
    version = cast(ShotgridVersionWithID, SG.create("Version", _version_from_publish(event)))

    logger.info("Uploading QuickTime to ShotGrid...")
    SG.upload(
        entity_type=version["type"],
        entity_id=version["id"],
        path=str(quicktime_path),
        field_name="sg_uploaded_movie",
        # display_name="Some display name",
    )


def _version_from_publish(event: flix.PublishEditorialEvent) -> ShotgridVersion:
    """Construct a ShotGrid version entity from a publish event."""
    project_id = event.show.metadata.get_int("shotgrid_id")
    sequence_id = event.sequence.metadata.get_int("shotgrid_id")
    if project_id is None or sequence_id is None:
        raise ValueError("The ShotGrid ID must be set on the Flix show and sequence")

    code = "{show_tracking_code}_{sequence_tracking_code}_v{revision_number:03}".format(
        show_tracking_code=event.show.tracking_code,
        sequence_tracking_code=event.sequence.tracking_code,
        revision_number=event.sequence_revision.revision_number or 0,
    )
    return ShotgridVersion(
        code=code,
        description=event.sequence_revision.comment or None,
        project=ShotgridProject(
            id=project_id,
            type="Project",
        ),
        entity=ShotgridSequence(
            id=sequence_id,
            type="Sequence",
        ),
    )


async def run_publish_webhook() -> None:
    """Run the webhook server until interrupted."""
    # ensure we close the ShotGrid client when exiting
    with contextlib.closing(SG):
        await flix.run_webhook_server(
            on_event,
            port=8888,
            # pass client options to the webhook runner
            # so we can run methods that communicate with
            # the Flix Server
            client_options={
                "hostname": FLIX_HOSTNAME,
                "port": FLIX_PORT,
                "api_key": FLIX_API_KEY,
                "api_secret": FLIX_API_SECRET,
            },
        )


if __name__ == "__main__":
    # enable logging
    logging.basicConfig(level=logging.INFO)
    # start the server
    asyncio.run(run_publish_webhook())
