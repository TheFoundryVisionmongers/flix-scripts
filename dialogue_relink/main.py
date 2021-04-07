#
# Copyright (C) Foundry 2021
#

import argparse
import datetime
import os
import signal
import sys

import flix as flix_api


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
        '--revisionid', required=True, help='show ID')

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
        print('YAY')
