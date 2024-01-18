"""Demonstrates creating a show in Flix from an existing ShotGrid project.

This example fetches project and sequence data from ShotGrid
and creates a Flix show containing sequences with matching descriptions.
It provides examples of how you might generate tracking codes
based on what fields are available for your project and sequence entities.

Additionally, the code provides examples of more advanced, optional features,
such as type hinting and streaming uploads to Flix.

Note that this example does not take shots into account.
"""

import asyncio
import logging
import os
import re
from typing import TypedDict, cast

import aiohttp
import flix
import shotgun_api3  # type: ignore[import-untyped]

# ShotGrid credentials and project ID to fetch the project data from
SHOTGRID_BASE_URL = "https://yourstudio.shotgunstudio.com/"
SHOTGRID_USERNAME = "user.name@example.com"
SHOTGRID_PASSWORD = "hunter2"
SHOTGRID_PROJECT = 421

# Flix server and credentials for creating the new show
FLIX_HOSTNAME = "localhost"
FLIX_PORT = 8080
FLIX_USERNAME = "admin"
FLIX_PASSWORD = "admin"


# optional statically typed schemas for our ShotGrid data,
# useful when using a static type checker such as Mypy or Pyright
class ShotgridProject(TypedDict):
    """Typed schema for ShotGrid projects."""

    type: str
    id: int
    name: str | None
    sg_description: str | None
    image: str | None
    code: str | None


class ShotgridSequence(TypedDict):
    """Typed schema for ShotGrid sequences."""

    type: str
    id: int
    code: str | None
    description: str | None


async def import_sg_show() -> None:
    """Create a Flix show from an existing ShotGrid project."""
    sg = shotgun_api3.Shotgun(
        SHOTGRID_BASE_URL, login=SHOTGRID_USERNAME, password=SHOTGRID_PASSWORD
    )
    try:
        # fetch the existing ShotGrid project and sequence data
        sg_project = cast(
            ShotgridProject,
            sg.find_one(
                "Project",
                [["id", "is", SHOTGRID_PROJECT]],
                ["id", "name", "sg_description", "image", "code"],
            ),
        )
        sg_sequences = cast(
            list[ShotgridSequence],
            sg.find(
                "Sequence",
                [["project.Project.id", "is", SHOTGRID_PROJECT]],
                ["id", "code", "description"],
            ),
        )
    finally:
        sg.close()

    async with flix.Client(FLIX_HOSTNAME, FLIX_PORT) as client:
        await client.authenticate(FLIX_USERNAME, FLIX_PASSWORD)

        # create a new show with the appropriate tracking code,
        # title and description; default values will be used for
        # the frame rate (24 fps) and aspect ratio (1.77)
        fallback_tracking_code = "SGSHOW"
        show = client.new_show(
            tracking_code=get_show_tracking_code(sg_project) or fallback_tracking_code,
            title=sg_project["name"] or "",
            description=sg_project["sg_description"] or "",
        )
        # attach the ShotGrid ID to the show for future reference
        show.metadata["shotgrid_id"] = sg_project["id"]
        # persist the new show to the Flix database
        # this will also save the metadata
        await show.save()

        # if we have a thumbnail image, upload it to Flix
        # and attach it to the show
        if image := sg_project["image"]:
            thumbnail_asset = await upload_thumbnail(show, image)
            await show.metadata.set_and_save("thumbnail_asset_id", thumbnail_asset.asset_id)

        # create the sequences
        for i, sg_sequence in enumerate(sg_sequences):
            fallback_tracking_code = f"SG{i:04}"
            sequence = show.new_sequence(
                tracking_code=sanitize_tracking_code(sg_sequence["code"]) or fallback_tracking_code,
                description=sg_sequence["description"] or "",
            )
            # attach sequence ID to Flix sequence
            sequence.metadata["shotgrid_id"] = sg_sequence["id"]
            await sequence.save()


def get_show_tracking_code(sg_project: ShotgridProject) -> str:
    """Try to generate an appropriate Flix tracking code from a ShotGrid project.

    Returns:
        A tracking code for the show, or an empty string if none could be generated.
    """
    # if we have an explicit tracking code set, just use that
    if sanitized_code := sanitize_tracking_code(sg_project["code"]):
        return sanitized_code

    name = sg_project["name"]
    if name is None:
        # can't guess a tracking code if we have no name
        return ""

    # try to use
    initials = "".join(word[0] for word in name.split() if len(word) > 0 and word[0].isupper())
    if len(sanitized_initials := sanitize_tracking_code(initials)) >= 3:
        return sanitized_initials

    # just use the first 10 valid characters of the project name as a last resort
    return sanitize_tracking_code(name.upper())


TRACKING_CODE_ILLEGAL_CHARACTERS = re.compile(r"[^a-zA-Z0-9_-]")


def sanitize_tracking_code(tracking_code: str | None) -> str:
    """Convert a string to a valid Flix tracking code.

    Replaces spaces with underscores, removes illegal characters,
    and ensures that the result is no more than 10 characters long.

    Args:
        tracking_code: The tracking code to sanitise.

    Returns:
        The sanitised tracking code, or an empty string if it contained no legal characters.
    """
    if tracking_code is None:
        return ""

    return TRACKING_CODE_ILLEGAL_CHARACTERS.sub(
        "",
        tracking_code.replace(" ", "_"),
    )[:10]


async def upload_thumbnail(show: flix.Show, image_url: str) -> flix.Asset:
    """Stream a show thumbnail image from ShotGrid to Flix.

    This function uploads the file without saving the file to disk,
    passing the data directly to Flix as it's downloaded.

    Demonstrates how you can build more complex data flows
    with asynchronous functions without using threads.

    Args:
        show: The show to upload the thumbnail to.
        image_url: The URL to download the thumbnail from.

    Returns:
        The newly created asset for the show thumbnail.
    """
    async with aiohttp.ClientSession() as session, session.get(image_url) as resp:
        # create a file pipe to connect the downloader to the uploader
        r, w = os.pipe()
        # run download and upload in parallel
        # so the downloader can feed the data to the uploader
        downloader = asyncio.create_task(_download_file(resp, w))
        uploader = asyncio.create_task(_upload_file(show, resp, r))

        try:
            # wait for download and upload to complete
            _, pending = await asyncio.wait(
                [downloader, uploader], return_when=asyncio.FIRST_EXCEPTION
            )
        finally:
            # if either task failed, make sure we cancel the other
            for task in pending:
                task.cancel()

        # get the asset returned by upload_file()
        return uploader.result()


async def _upload_file(show: flix.Show, response: aiohttp.ClientResponse, r: int) -> flix.Asset:
    """Read data from a pipe and upload to Flix as a show thumbnail."""
    # pass the read end of the pipe to upload_file()
    # to upload the data written by the downloader
    with os.fdopen(r, "rb") as reader:
        return await show.upload_file(
            reader,
            flix.AssetType.SHOW_THUMBNAIL,
            name=response.url.name,
            size=response.content_length,
        )


async def _download_file(response: aiohttp.ClientResponse, w: int) -> None:
    """Download data from ShotGrid and write to a pipe."""
    # read the response from ShotGrid and pass the data to the uploader using the pipe
    # note: important to close the writer to signal the end of the file
    # (this is automatically handled by the 'with' statement)
    with os.fdopen(w, "wb") as writer:
        async for chunk in response.content.iter_chunked(1024 * 1024 * 10):
            writer.write(chunk)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(import_sg_show())
