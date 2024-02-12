from __future__ import annotations

import asyncio
import datetime

import flix

HOSTNAME = "localhost"
PORT = 8080
USERNAME = "admin"
PASSWORD = "admin"

SHOW_ID = 478
SEQUENCE_ID = 415


async def main() -> None:
    async with flix.Client(HOSTNAME, PORT) as client:
        # authenticate with the Flix server
        await client.authenticate(USERNAME, PASSWORD)

        # fetch show and sequence
        show = await client.get_show(SHOW_ID)
        sequence = await show.get_sequence(SEQUENCE_ID)

        # print sequence metadata
        print("Current metadata:", sequence.metadata)

        # set a single metadata field without persisting to the database
        sequence.metadata["processed_time"] = datetime.datetime.utcnow()

        # set multiple metadata fields
        sequence.metadata.update(
            my_integer=10,
            my_float=3.14,
            my_bool=True,
            my_string="1234",
            my_array=["one", "two", "three"],
            my_object={"key": "value"},
        )

        # read a metadata field value
        print("Float value:", sequence.metadata["my_float"])

        # attempt to read a metadata field as an int
        try:
            int_value = sequence.metadata.get_int("my_string")
            print("String value as int:", int_value, type(int_value))
        except ValueError as e:
            print("Error: Could not read my_string as int:", e)

        # access more information about a metadata field
        object_field = sequence.metadata.get_field("my_object")
        print("my_object was modified at:", object_field.modified_date)

        # persist metadata to database
        await sequence.metadata.save()

        # set and persist a single metadata field
        await sequence.metadata.set_and_save("shotgrid_sequence_id", 23)

        # remove a single field from the database
        await sequence.metadata.delete_field("my_array")

        # clear local metadata
        sequence.metadata.clear()
        print("Empty metadata:", sequence.metadata)

        # re-fetch metadata from database
        await sequence.metadata.fetch_metadata()
        print("Updated metadata:", sequence.metadata)

        # fetch a single field from the database
        id_field = await sequence.metadata.fetch_field("shotgrid_sequence_id")
        print("Shotgrid sequence ID:", id_field.value)


if __name__ == "__main__":
    asyncio.run(main())
