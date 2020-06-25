#
# Copyright (C) Foundry 2020
#

import base64
import binascii
import hashlib
import hmac
import json
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Tuple

import requests


class flix:
    """Flix will handle the login and expose functions to get,
    create shows etc.
    """

    def __init__(self):
        self.reset()

    def authenticate(self, hostname: str, login: str, password: str) -> Dict:
        """authenticate will authenticate a user

        Arguments:
            hostname {str} -- Hostname of the server

            login {str} -- Login of the user

            password {str} -- Password of the user

        Returns:
            Dict -- Authenticate
        """
        authdata = base64.b64encode((login + ':' + password).encode('UTF-8'))
        response = None
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + authdata.decode('UTF-8'),
        }
        try:
            r = requests.post(hostname + '/authenticate', headers=header,
                              verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            self.hostname = hostname
            self.login = login
            self.password = password
        except requests.exceptions.RequestException as err:
            print('Authentification failed', err)
            return None

        self.key = response['id']
        self.secret = response['secret_access_key']
        self.expiry = datetime.strptime(
            response['expiry_date'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return response

    def reset(self):
        """reset will reset the user info
        """
        self.hostname = None
        self.secret = None
        self.expiry = None
        self.login = None
        self.password = None
        self.key = None

    def revoke_access_key(self, access_key) -> bool:
        url = '/authenticate/key/{}'.format(access_key)
        headers = self.__get_headers(None, url, 'DELETE')

        try:
            r = requests.delete(self.hostname + url, headers=headers,
                                verify=False)
            r.raise_for_status()
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            elif r is not None and r.status_code == 403:
                print('could not revoke access key (need to be admin user)')
                return None
            else:
                print('Could not revoke access key', err)
            return False
        return True

    def get_info(self) -> Dict:
        url = '/info'
        headers = self.__get_headers(None, url, 'GET')
        response = None

        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve info', err)
            return None
        return response

    def get_users(self) -> Dict:
        url = '/users/current'
        headers = self.__get_headers(None, url, 'GET')
        response = None

        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            elif r is not None and r.status_code == 403:
                print('could not get infos (need to be admin user)')
                return None
            else:
                print('Could not retrieve users', err)
            return None
        return response

    def __get_token(self) -> Tuple[str, str]:
        """__get_token will request a token and will reset it
        if it is too close to the expiry date

        Returns:
            Tuple[str, str] -- Key and Secret
        """
        if (self.key is None or self.secret is None or self.expiry is None or
                datetime.now() + timedelta(hours=2) > self.expiry):
            authentificationToken = self.authenticate(
                self.hostname, self.login, self.password)
            auth_id = authentificationToken['id']
            auth_secret_token = authentificationToken['secret_access_key']
            auth_expiry_date = authentificationToken['expiry_date']
            auth_expiry_date = auth_expiry_date.split('.')[0]
            self.key = auth_id
            self.secret = auth_secret_token
            self.expiry = datetime.strptime(auth_expiry_date,
                                            '%Y-%m-%dT%H:%M:%S')
        return self.key, self.secret

    def __fn_sign(self,
                  access_key_id: str,
                  secret_access_key: str,
                  url: str,
                  content: object,
                  http_method: str,
                  content_type: str,
                  dt: str) -> str:
        """After being logged in, you will have a token.

        Arguments:
            access_key_id {str} -- Access key ID from your token

            secret_access_key {str} -- Secret access key from your token

            url {str} -- Url of the request

            content {object} -- Content of your request

            http_method {str} -- Http Method of your request

            content_type {str} -- Content Type of your request

            dt {str} -- Datetime

        Raises:
            ValueError: 'You must specify a secret_access_key'

        Returns:
            str -- Signed header
        """
        raw_string = http_method.upper() + '\n'
        content_md5 = ''
        if content:
            if isinstance(content, str):
                content_md5 = hashlib.md5(content).hexdigest()
            elif isinstance(content, bytes):
                hx = binascii.hexlify(content)
                content_md5 = hashlib.md5(hx).hexdigest()
            elif isinstance(content, dict):
                jsoned = json.dumps(content)
                content_md5 = hashlib.md5(jsoned.encode('utf-8')).hexdigest()
        if content_md5 != '':
            raw_string += content_md5 + '\n'
            raw_string += content_type + '\n'
        else:
            raw_string += '\n\n'
        raw_string += dt.isoformat().split('.')[0] + 'Z' + '\n'
        url_bits = url.split('?')
        url_without_query_params = url_bits[0]
        raw_string += url_without_query_params
        if len(secret_access_key) == 0:
            raise ValueError('You must specify a secret_access_key')
        digest_created = base64.b64encode(
            hmac.new(secret_access_key.encode('utf-8'),
                     raw_string.encode('utf-8'),
                     digestmod=hashlib.sha256).digest()
        )
        return 'FNAUTH ' + access_key_id + ':' + digest_created.decode('utf-8')

    def __get_headers(
            self, content: object, url: str, method: str = 'POST') -> object:
        """__get_headers will generate the header to make any request
        containing the authorization with signature

        Arguments:
            content {object} -- Content of the request

            url {str} -- Url to make the request

            method {str} -- Request method (default: {'POST'})

        Returns:
            object -- Headers
        """
        dt = datetime.utcnow()
        key, secret = self.__get_token()
        return {
            'Authorization': self.__fn_sign(
                key,
                secret,
                url,
                content,
                method,
                'application/json',
                dt),
            'Content-Type': 'application/json',
            'Date': dt.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        }
