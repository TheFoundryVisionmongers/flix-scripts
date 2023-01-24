import asyncio

import flix

# Authentication data
HOSTNAME = "localhost"
PORT = 8080
USERNAME = "admin"
PASSWORD = "admin"

# Flix IDs
SHOW_ID = 1
SEQUENCE_ID = 1
SEQUENCE_REVISION = 1
PANEL_ID = 1
PANEL_REVISION = 1

# New file to be used to create the new panel revision
FILEPATH = "./new_file.psd"


async def main() -> None:
    async with flix.Client(HOSTNAME, PORT) as client:
        # Log into the Flix server
        await client.authenticate(USERNAME, PASSWORD)
        # Get the show from the server
        show = await client.get_show(SHOW_ID)
        # Create an 'artwork' media object with the file and transcode it to create a thumbnail
        with open(FILEPATH, 'rb') as f:
            asset = await show.upload_file(f, "artwork")
        job_ids = await show.transcode_assets([asset])

        # The transcodes do not need to complete before creating the panel revision
        print(f"Thumbnail transcoding occurring in jobs: {job_ids}")

        # Get the panel revision we want to update
        sequence = await show.get_sequence(SEQUENCE_ID)
        panel_revision = await sequence.get_panel_revision(PANEL_ID, PANEL_REVISION)
        # Set the asset to be the one we've just created with the new file
        panel_revision.asset = asset
        # Create a new revision of the panel
        await panel_revision.save()


if __name__ == "__main__":
    """
    This example shows how to create a new revision of a panel, using a new file for the new panel revision.
    
    The new panel revision will then be available within Flix. We are not creating a new sequence revision with this
    example.
    """

    asyncio.run(main())
