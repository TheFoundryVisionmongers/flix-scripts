#
# Copyright (C) Foundry 2021
#

import argparse
import datetime
import os
import signal
import sys
import flix as flix_api


def start_relink(show_id, episode_id, sequence_id, revision_id, comment):

    # Get selected revision
    revision = flix_api.get_sequence_revision_by_id(
        show_id, episode_id, sequence_id, revision_id)

    if revision == None:
        sys.exit(1)

    # Get all panels in the sequence revision
    panels = flix_api.get_sequence_revision_panels(
        show_id, episode_id, sequence_id, revision_id)

    if panels == None:
        sys.exit(1)

    revisioned_panels = []

    # Loop through panels and get dialogues for each
    # Select the latest dialogue
    for p in panels:
        dialogues = flix_api.get_panel_dialogues(
            show_id, episode_id, sequence_id, p.get("panel_id"))

        dialogue = None
        if len(dialogues):
            dialogue = {'id': dialogues[0].get(
                'dialogue_id'), 'text': ""}

        # Creates json object for each panel to POST
        formatted_panel = flix_api.format_panel_for_revision(p, dialogue)
        revisioned_panels.append(formatted_panel)

    # Sends POST request to create a new sequence revision with correct panels and dialogues
    flix_api.create_new_sequence_revision(
        show_id, episode_id, sequence_id, revisioned_panels, revision, comment)


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
        '--sequenceid', required=True, help='Sequence ID')
    required_group.add_argument(
        '--episodeid', required=False, help='Episode ID')
    required_group.add_argument(
        '--revisionid', required=True, help='Revision ID')
    required_group.add_argument(
        '--comment', required=False, help='New Sequence Revision Comment')

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
        start_relink(args.showid, args.episodeid, args.sequenceid,
                     args.revisionid, args.comment)
