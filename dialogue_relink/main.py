#
# Copyright (C) Foundry 2021
#

import argparse
import datetime
import os
import signal
import sys

import flix as flix_api


def fetch_sequence_revision_by_id(show_id, seq_id, episode_id, revision_id):
    seq_revision = flix_api.get_sequence_revision_by_id(
        show_id, seq_id, episode_id, revision_id)

    return seq_revision


def fetch_sequence_revision_panels(show_id, seq_id, episode_id, revision_id):
    panels = flix_api.get_sequence_revision_panels(
        show_id, seq_id,  episode_id, revision_id)

    return panels


def fetch_panel_dialogues(show_id, seq_id, episode_id, panel_id):
    dialogues = flix_api.get_panel_dialogues(
        show_id, seq_id, episode_id, panel_id)

    return dialogues


def loop_panels(panels, show_id, seq_id, episode_id, revision_id):
    rev = fetch_sequence_revision_by_id(
        show_id, seq_id, episode_id, revision_id)
    
    revisioned_panels = []

    for p in panels:
        latest_dialogue = fetch_panel_dialogues(show_id, seq_id, episode_id, p.get("panel_id"))
        
        dialogue = None
        if len(latest_dialogue):
            dialogue = { 'id': latest_dialogue[0].get('dialogue_id'), 'text': "" }

        formatted_panel = flix_api.format_panel_for_revision(p, dialogue)
        revisioned_panels.append(formatted_panel)
        
        
    flix_api.create_new_sequence_revision(
            show_id, seq_id, revisioned_panels, rev)


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
        '--showid', required=True, help='show ID')
    required_group.add_argument(
        '--sequenceid', required=True, help='show ID')
    required_group.add_argument(
        '--episodeid', required=True, help='Episode ID')
    required_group.add_argument(
        '--revisionid', required=True, help='Revision ID')

    return parser.parse_args()


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
        foo = fetch_sequence_revision_panels(
            args.showid, args.sequenceid, args.episodeid, args.revisionid)

        loop_panels(foo, args.showid, args.sequenceid,
                    args.episodeid, args.revisionid)
