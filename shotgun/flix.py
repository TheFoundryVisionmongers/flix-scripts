import base64
import binascii
import hashlib
import hmac
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


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

    def get_shows(self) -> Dict:
        """get_shows retrieve the list of shows

        Returns:
            Dict -- Shows
        """
        headers = self.__get_headers(None, '/shows', 'GET')
        response = None
        try:
            r = requests.get(self.hostname + '/shows', headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            response = response.get('shows')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve shows', err)
            return None
        return response

    def get_asset(self, asset_id: int) -> Dict:
        """get_asset retrieve an asset

        Arguments:
            asset_id {int} -- Asset ID

        Returns:
            Dict -- Asset
        """
        url = '/asset/{0}'.format(asset_id)
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
                print('Could not retrieve asset', err)
            return None
        return response

    def get_episodes(self, show_id: int) -> Dict:
        """get_episodes retrieve the list of episodes from a show

        Arguments:
            show_id {int} -- Show ID

        Returns:
            Dict -- Episodes
        """
        url = '/show/{0}/episodes'.format(show_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            response = response.get('episodes')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve episodes', err)
            return None
        return response

    def get_sequences(self, show_id: int, episode_id: int = None) -> Dict:
        """get_sequences retrieve the list of sequence from a show

        Arguments:
            show_id {int} -- Show ID

        Keyword Arguments:
            episode_id {int} -- Episode ID (default: {None})

        Returns:
            Dict -- Sequences
        """
        url = '/show/{0}/sequences'.format(show_id)
        if episode_id is not None:
            url = '/show/{0}/episode/{1}/sequences'.format(
                show_id, episode_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('sequences')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequences', err)
            return None
        return response

    def get_panels(
            self, show_id: int, sequence_id: int, rev_number: int) -> Dict:
        """get_panels retrieve the list of panels from a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            rev_number {int} -- Sequence revision number

        Returns:
            Dict -- Panels
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/panels'.format(
            show_id, sequence_id, rev_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('panels')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve panels', err)
            return None
        return response

    def get_dialogues(
            self, show_id: int, sequence_id: int, rev_number: int) -> Dict:
        """get_dialogues get the list of dialogues from a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            rev_number {int} -- Sequence revision number

        Returns:
            Dict -- Dialogues
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/dialogues'.format(
            show_id, sequence_id, rev_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('dialogues')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve dialogues', err)
            return None
        return response

    def get_sequence_rev(self, show_id: int, sequence_id: int,
                         revision_number: int) -> Dict:
        """get_sequence_rev retrieve a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            revision_number {int} -- Sequence Revision Number

        Returns:
            Dict -- Sequence Revision
        """
        url = '/show/{0}/sequence/{1}/revision/{2}'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequence revision', err)
            return None
        return response

    def download_media_object(
            self, temp_filepath: str, media_object_id: int) -> str:
        """download_media_object download a media object

        Arguments:
            temp_filepath {str} -- Temp filepath to store the downloaded file

            media_object_id {int} -- Media Object ID

        Returns:
            str -- Temp filepath of the downloaded file
        """
        url = '/file/{0}/data'.format(media_object_id)
        headers = self.__get_headers(None, url, 'GET')
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            file = open(temp_filepath, 'wb')
            file.write(r.content)
            file.close()
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve media object', err)
            return None
        return temp_filepath

    def start_quicktime_export(self,
                               show_id: int,
                               sequence_id: int,
                               seq_rev_number: int,
                               panel_revisions: List,
                               episode_id: int = None,
                               include_dialogue: bool = False) -> Dict:
        """start_quicktime_export will create a quicktime export

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            seq_rev_number {int} -- Sequence Revision Number

            panel_revisions {List} -- List of panel revisions

        Keyword Arguments:
            episode_id {int} -- Episode ID (default: {None})
            include_dialogue {bool} -- Include Dialogue (default: {False})

        Returns:
            Dict -- Export response
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/export/quicktime'.format(
            show_id, sequence_id, seq_rev_number)
        if episode_id is not None:
            url = ('/show/{0}/episode/{1}/sequence/{2}/revision/{3}/' +
                   'export/quicktime').format(
                       show_id, episode_id, sequence_id, seq_rev_number)
        content = {
            'include_dialogue': include_dialogue,
            'panel_revisions': panel_revisions
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not export quicktime', err)
            return None
        return response

    def get_chain(self, chain_id: int) -> Dict:
        """get_sequence_rev retrieve a chain

        Arguments:
            chain_id {int} -- Chain ID

        Returns:
            Dict -- Chain
        """
        url = '/chain/{0}'.format(chain_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve chain', err)
            return None
        return response

    def new_sequence_revision(self,
                              show_id: int,
                              sequence_id: int,
                              revisioned_panels: List,
                              markers: List,
                              comment: str = 'From Hiero') -> Dict:
        """new_sequence_revision will create a new sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            revisioned_panels {List} -- List of revisionned panels

            markers {List} -- List of Markers

        Keyword Arguments:
            comment {str} -- Comment (default: {'From Hiero'})

        Returns:
            Dict -- Sequence Revision
        """
        url = '/show/{0}/sequence/{1}/revision'.format(show_id, sequence_id)
        content = {
            'comment': comment,
            'imported': False,
            'meta_data': {
                'annotations': [],
                'audio_timings': [],
                'highlights': [],
                'markers': markers
            },
            'revisioned_panels': revisioned_panels
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create sequence revision', err)
            return None
        return response

    def new_panel(
            self, show_id: int, sequence_id: int, asset_id: int = None,
            duration: int = 12) -> Dict:
        """new_panel will create a blank panel

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

        Keyword Arguments:
            asset_id {int} -- Asset ID (default: {None})

            duration {int} -- Duration (default: {12})

        Returns:
            Dict -- Panel
        """
        url = '/show/{0}/sequence/{1}/panel'.format(show_id, sequence_id)
        content = {
            'duration': duration,
        }
        if asset_id is not None:
            content['asset'] = {'asset_id': asset_id}
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create blank panel', err)
            return None
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

        Keyword Arguments:
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
