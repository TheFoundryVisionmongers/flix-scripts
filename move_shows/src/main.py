import click
import mysql.connector

from collections import namedtuple

from mysql.connector import errorcode
from mysql.connector.connection_cext import MySQLConnection
from mysql.connector.cursor_cext import MySQLCursor

from os import remove

from shutil import copyfile

from typing import List

MYSQL_QUERY_INSTALL_VERSION = "SELECT `value` FROM `settings` WHERE `key` = 'version'"
MYSQL_QUERY_SHOWS = "SELECT `show_id`, `title` FROM `shows`"
MYSQL_QUERY_SEQUENCES = (
    "SELECT `id`, `tracking_code` FROM `sequence` WHERE `show_id` = %s"
)
MYSQL_QUERY_MEDIA_OBJECTS = """SELECT
    CONCAT(`media_object`.`id`, '_', `media_object`.`filename`) AS 'FilePath'
FROM
    `media_object`
LEFT JOIN
        `asset` ON `asset`.`asset_id` = `media_object`.`asset_id`
LEFT JOIN
        `vPanel_asset_ref` ON `vPanel_asset_ref`.`asset_id` = `asset`.`asset_id`
WHERE
    `media_object`.`show_directory` = 1 AND
    `vPanel_asset_ref`.show_id = %s AND
    `vPanel_asset_ref`.`sequence_id`= %s
"""
MYSQL_UPDATE_SEQUENCE_DIALOGUE = "UPDATE `sequence_dialogue` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_VDIALOGUE = (
    "UPDATE `vDialogue` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
)
MYSQL_UPDATE_COMMENT_TO_PANEL = "UPDATE `comment_to_panel` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_SEQUENCE_PANEL = "UPDATE `sequence_panel` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_PANEL_KEY_FRAME = "UPDATE `panel_key_frame` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_RELATED_PANELS = "UPDATE `related_panels` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_PANEL_ORIGIN = (
    "UPDATE `panelOrigin` SET `show_id` = %s WHERE `show_id` = %s AND sequence_id = %s"
)
MYSQL_UPDATE_VPANEL_ASSET_REF = "UPDATE `vPanel_asset_ref` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_SEQUENCE_REVISION_ENTITY_TYPE = "UPDATE `sequence_revision_entity_type` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
MYSQL_UPDATE_PANEL = (
    "UPDATE `panel` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
)
MYSQL_UPDATE_VMASTER = (
    "UPDATE `vMaster` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
)
MYSQL_UPDATE_VPANEL = (
    "UPDATE `vPanel` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
)
MYSQL_UPDATE_VSEQUENCE = (
    "UPDATE `vSequence` SET `show_id` = %s WHERE `show_id` = %s AND `sequence_id` = %s"
)
MYSQL_UPDATE_ENTITY = """UPDATE
    `entity`
JOIN
    `sequence_revision_entity_type` ON `sequence_revision_entity_type`.`entity_id` = `entity`.`id`
SET
    `entity`.`show_id` = %s
WHERE
    `sequence_revision_entity_type`.`show_id` = %s AND
    `sequence_revision_entity_type`.`sequence_id` = %s
"""
MYSQL_UPDATE_ASSET = """UPDATE 
    `asset`
JOIN
    `vPanel_asset_ref` ON `vPanel_asset_ref`.`asset_id` = `asset`.`asset_id`
SET
    `asset`.`show_id` = %s
WHERE
    `vPanel_asset_ref`.`show_id` = %s AND
    `vPanel_asset_ref`.`sequence_id` = %s
    
"""
MYSQL_UPDATE_SEQUENCE = (
    "UPDATE `sequence` SET `show_id` = %s WHERE `show_id` = %s AND `id` = %s"
)

FLIX_DB_VERSIONS_TO_RELEASE = {
    "42": "6.4.1",
    "56": "6.5.0",
    "58": "6.6.0",
}

SequenceMap = namedtuple("SequenceMap", "sequence_id tracking_code")
ShowMap = namedtuple("ShowMap", "show_id title")


@click.command()
def main():
    click.echo(
        "Welcome to the Move Show script. This script will update the Flix database to move a sequence, and all connected entities to a different show"
    )
    click.echo(
        "To run this script will need database credentials with the same permissions as the database user the Flix Server uses"
    )
    click.echo(
        "Additionally, it will to be able to Read/Write/Delete from the Flix Server asset directory"
    )
    click.echo(
        "It is strongly recommended this script is only run when there are no Flix Client users active"
    )
    if not click.confirm(
        "Would you like to continue? (You will be asked to confirm again before changes are made permanent)"
    ):
        click.echo("User has exited early")
        return

    try:
        conn = connect_to_database()
        cur = conn.cursor()
        flix_version = get_flix_version(cur)
        shows = get_shows(cur)
        source_show = pick_show(
            shows, "Which show contains the sequence you want to move"
        )
        dest_show = pick_show(
            shows, "Which show would you like to move the sequence to"
        )
        if source_show.show_id == dest_show.show_id:
            raise Exception("Source and destination show cannot be the same")

        source_sequences = get_sequences(cur, source_show.show_id)
        source_sequence = pick_sequence(source_sequences)
        source_files = get_source_filenames(
            cur, source_show.show_id, source_sequence.sequence_id
        )

        asset_dir = get_asset_dir_path()
        copy_files(asset_dir, source_files, source_show, dest_show)

        update_tables(cur, flix_version, source_show, dest_show, source_sequence)

        if click.confirm(
            "All updates made, please confirm you would like to commit the changes"
        ):
            conn.commit()
            delete_files(asset_dir, source_files, source_show)
        else:
            delete_files(asset_dir, source_files, dest_show)

        cur.close()
        conn.close()
    except Exception as err:
        click.echo(f"An error occurred: {err}")


def connect_to_database() -> MySQLConnection:
    click.echo("Establishing connection to database. Please provide MyySQL connection details")
    user = click.prompt("Username", type=str, err=True, default="flix")
    password = click.prompt(
        "Password", type=str, hide_input=True, err=True, default="password"
    )
    host = click.prompt("Host address", type=str, err=True, default="127.0.0.1")
    database_name = click.prompt(
        "Database name", type=str, err=True, default="flix", show_default=True
    )
    enable_ssl = click.prompt(
        "Enable SSL", type=bool, err=True, default=False, show_default=True
    )

    try:
        return mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database_name,
            ssl_disabled=not enable_ssl,
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            click.echo("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            click.echo("Database does not exist")
        raise err


def copy_files(
    asset_dir: str, filenames: List[str], source_show: ShowMap, dest_show: ShowMap
) -> None:
    click.echo(f"Copying {len(filenames)} files")
    for fn in filenames:
        copyfile(
            f"{asset_dir}{source_show.show_id}/{fn}",
            f"{asset_dir}{dest_show.show_id}/{fn}",
        )


def delete_files(asset_dir: str, filenames: List[str], source_show: ShowMap) -> None:
    click.echo(f"Deleting {len(filenames)} files")
    for fn in filenames:
        remove(f"{asset_dir}{source_show.show_id}/{fn}")


def get_asset_dir_path() -> str:
    asset_dir_path = click.prompt(
        "Please enter the path to your asset directory",
        type=str,
        default="/path/to/assets",
    )
    if asset_dir_path[-1] != "/":
        asset_dir_path += "/"

    return asset_dir_path


def get_flix_version(cur: MySQLCursor) -> str:
    try:
        click.echo("Getting Flix install version from database")
        cur.execute(MYSQL_QUERY_INSTALL_VERSION)
        (db_version,) = next(cur)

        flix_version = FLIX_DB_VERSIONS_TO_RELEASE[f"{db_version}"]
        click.echo(f"Found Flix version: {flix_version}")
        return flix_version
    except KeyError:
        click.echo(f"Could not establish Flix version from db version: {db_version}")
        raise Exception("Unsupported Flix version")
    except Exception:
        raise Exception("Unsupported Flix version")


def get_source_filenames(
    cur: MySQLCursor, show_id: int, sequence_id: int
) -> List[str]:
    click.echo(f"Fetching media objects associated with sequence ID {sequence_id}")

    ret: List[str] = []
    cur.execute(
        MYSQL_QUERY_MEDIA_OBJECTS,
        (
            show_id,
            sequence_id,
        ),
    )
    for (path,) in cur:
        ret.append(path)
    click.echo(f"Found {len(ret)} files to move")
    return ret


def get_sequences(cur: MySQLCursor, show_id: int) -> List[SequenceMap]:
    click.echo(f"Fetching sequences from show ID {show_id}")
    ret: List[SequenceMap] = []
    cur.execute(MYSQL_QUERY_SEQUENCES, (show_id,))
    for seq_id, code in cur:
        ret.append(SequenceMap(seq_id, code))

    return ret


def get_shows(cur: MySQLCursor) -> List[ShowMap]:
    click.echo("Fetching shows from database")
    ret: List[ShowMap] = []
    cur.execute(MYSQL_QUERY_SHOWS)
    for show_id, title in cur:
        ret.append(ShowMap(show_id, title))

    click.echo(f"Found {len(ret)} shows")
    return ret


def get_update_queries(flix_version: str) -> List[str]:
    queries = [
        MYSQL_UPDATE_SEQUENCE_DIALOGUE,
        MYSQL_UPDATE_VDIALOGUE,
        MYSQL_UPDATE_COMMENT_TO_PANEL,
        MYSQL_UPDATE_SEQUENCE_PANEL,
        MYSQL_UPDATE_PANEL_KEY_FRAME,
        MYSQL_UPDATE_PANEL_ORIGIN,
        MYSQL_UPDATE_VPANEL_ASSET_REF,
        MYSQL_UPDATE_PANEL,
        MYSQL_UPDATE_VMASTER,
        MYSQL_UPDATE_VPANEL,
        MYSQL_UPDATE_VSEQUENCE,
        MYSQL_UPDATE_ASSET,
        MYSQL_UPDATE_SEQUENCE,
    ]

    if flix_version in (
        "6.5.0",
        "6.6.0",
    ):
        queries.append(MYSQL_UPDATE_RELATED_PANELS)
        queries.append(MYSQL_UPDATE_SEQUENCE_REVISION_ENTITY_TYPE)
        queries.append(MYSQL_UPDATE_ENTITY)

    return queries


def pick_sequence(sequences: List[SequenceMap]) -> SequenceMap:
    tracking_code_to_id = {s.tracking_code: s for s in sequences}
    sequence_code = click.prompt(
        "Which sequence would you like to transfer",
        type=click.Choice([v for v in tracking_code_to_id.keys()]),
    )
    return tracking_code_to_id[sequence_code]


def pick_show(shows: List[ShowMap], prompt: str) -> ShowMap:
    title_to_id = {s.title: s for s in shows}
    show_title = click.prompt(
        prompt,
        type=click.Choice([v for v in title_to_id.keys()]),
    )
    return title_to_id[show_title]


def update_tables(
    cur: MySQLCursor,
    flix_version: str,
    source_show: ShowMap,
    dest_show: ShowMap,
    seq: SequenceMap,
) -> None:
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for query in get_update_queries(flix_version):
        cur.execute(
            query,
            (
                dest_show.show_id,
                source_show.show_id,
                seq.sequence_id,
            ),
        )
    cur.execute("SET FOREIGN_KEY_CHECKS=1")


if __name__ == "__main__":
    main()
