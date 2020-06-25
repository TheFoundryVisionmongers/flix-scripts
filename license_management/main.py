#
# Copyright (C) Foundry 2020
#

import argparse
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
    required_action = required_group.add_mutually_exclusive_group(
        required=True)
    required_action.add_argument(
        '--info', action='store_true', help='Show seats and logged in users')
    required_action.add_argument(
        '--revoke',
        help='Revoke user from access key',
        nargs='*',
        default=[])
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

    if args.info:
        # Get Access keys:
        access_keys = flix_api.get_users()
        if access_keys is None:
            print('could not get access keys from Flix Server')
            sys.exit(1)

        # Get infos
        info = flix_api.get_info()
        if info is None:
            print('could not get infos from Flix Server')
            sys.exit(1)

        # Print seats infos
        print('Seats in use: {} / Maximum seats: {}'.format(
            info.get('current_seats'),
            info.get('max_seats')))

        # Print table of users
        dash = '-' * 100
        print(dash)
        print('{:<20s}|{:>6s}|{:>20s}|{:>30s}'.format(
            'access_key',
            'user id',
            'username', 'expiry_date'))
        print(dash)
        for ak in access_keys.get('access_keys', []):
            owner = ak.get('owner', {})
            print('{:<20s}|{:>7s}|{:>20s}|{:>30s}'.format(
                str(ak.get('id')),
                str(owner.get('id')),
                str(owner.get('username')),
                str(ak.get('expiry_date'))))

    elif args.revoke:
        # Revoke access keys
        for ak_id in args.revoke:
            if flix_api.revoke_access_key(ak_id) is False:
                print('could not revoke access key: {}'.format(ak_id))
