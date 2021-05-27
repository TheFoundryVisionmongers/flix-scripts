#
# Copyright (C) Foundry 2021
#

import argparse
import sys
import flix as flix_api


def get_panels_with_media_objects(show_id: int, episode_id: int, sequence_id: int, revision_id: int):

    # Get selected revision
    revision = flix_api.get_sequence_revision_by_id(
        show_id, episode_id, sequence_id, revision_id)

    if revision is None:
        print('Revision not found.')
        sys.exit(1)

    # Get all panels in the sequence revision
    panels = flix_api.get_sequence_revision_panels(
        show_id, episode_id, sequence_id, revision_id)

    if panels is None:
        print('Panels not found.')
        sys.exit(1)

    panels_with_media_object = []

    # Loop through panels and get media objects for each
    for p in panels:
        assets = flix_api.get_asset(p.get("asset").get('asset_id'))

        updated_panel = flix_api.format_panel_with_media_objects(
            p, assets.get('media_objects'))
        panels_with_media_object.append(updated_panel)

    return panels_with_media_object


# Initialise cli params
def parse_cli():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS)

    # Required args
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument(
        '--server', required=True, help='Flix 6 server url')
    required_group.add_argument(
        '--user', required=True, help='Flix 6 client username')
    required_group.add_argument(
        '--password', required=True, help='Flix 6 client password')
    required_group.add_argument(
        '--showid', required=True, help='Show ID')
    required_group.add_argument(
        '--episodeid', required=False, help='Episode ID')
    required_group.add_argument(
        '--sequenceid', required=True, help='Sequence ID')
    required_group.add_argument(
        '--revisionid', required=True, help='Revision ID')

    return parser.parse_args()


# App starts here
if __name__ == '__main__':
    args = parse_cli()

    # Init flix api
    flix_api = flix_api.flix()

    # Retrieve authentification token
    hostname = args.server
    login = args.user
    password = args.password

    # Authenticate to Flix server
    credentials = flix_api.authenticate(hostname,
                                        login,
                                        password)
    if credentials is None:
        print('could not authenticate to Flix Server')
        sys.exit(1)
    else:
        panels = get_panels_with_media_objects(args.showid, args.episodeid, args.sequenceid,
                                               args.revisionid)

        print(panels)
