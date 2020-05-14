import base64
import binascii
import hashlib
import hmac
import json
import urllib2
from datetime import datetime, timedelta


class flix:

    def __init__(self):
        self.reset()

    def get_shows(self):
        """get_shows retrieve the list of shows"""
        headers = self.__get_headers(None, '/shows', 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + '/shows', headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('shows')
        except BaseException:
            print('Could not retrieve shows')
            return None
        return response

    def authenticate(self, hostname, login, password):
        """authenticate will authenticate a user
        hostname: hostname of the server (ex: http://localhost:1234)
        login: login of the user
        password: password of the user
        """
        authdata = base64.b64encode((login + ':' + password).encode('UTF-8'))
        response = None
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + authdata.decode('UTF-8'),
        }
        try:
            req = urllib2.Request(hostname + '/authenticate',
                                  headers=header, data='')
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            self.hostname = hostname
            self.login = login
            self.password = password
        except BaseException:
            print('Authentification failed')
            return None
        return response

    def get_episodes(self, show_id):
        """get_episodes retrieve the list of episodes from a show
        show_id: show ID
        """
        url = '/show/{0}/episodes'.format(show_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('episodes')
        except BaseException:
            print('Could not retrieve episodes')
            return None
        return response

    def get_sequences(self, show_id, episode_id=None):
        """get_sequences retrieve the list of sequence from a show
        show_id: show ID
        episode_id: optional is the episode ID
        """
        url = '/show/{0}/sequences'.format(show_id)
        if episode_id is not None:
            url = '/show/{0}/episode/{1}/sequences'.format(show_id, episode_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('sequences')
        except BaseException:
            print('Could not retrieve sequences')
            return None
        return response

    def get_panels(self, show_id, sequence_id, revision_number):
        """get_panels retrieve the list of panels from a sequence revision
        show_id: show ID
        sequence_id: sequence ID
        revision_number: sequence revision number
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/panels'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('panels')
        except BaseException:
            print('Could not retrieve panels')
            return None
        return response

    def get_dialogues(self, show_id, sequence_id, revision_number):
        """get_dialogues retrieve the list of dialogues from
        a sequence revision
        show_id: show ID
        sequence_id: sequence ID
        revision_number: sequence revision number
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/dialogues'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('dialogues')
        except BaseException:
            print('Could not retrieve dialogues')
            return None
        return response

    def get_sequence_rev(self, show_id, sequence_id, revision_number):
        """get_sequence_rev retrieve a sequence revision
        show_id: show ID
        sequence_id: sequence ID
        revision_number: sequence revision number
        """
        url = '/show/{0}/sequence/{1}/revision/{2}'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except BaseException:
            print('Could not retrieve sequence revision')
            return None
        return response

    def download_media_object(self, temp_filepath, media_object_id):
        """download_media_object download a media object
        temp_filepath: filepath to store the downloaded image
        media_object_id: media object id
        """
        url = '/file/{0}/data'.format(media_object_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            file = open(temp_filepath, 'wb')
            file.write(response)
            file.close()
        except BaseException:
            print('Could not retrieve thumbnail')
            return None
        return temp_filepath

    def new_sequence_revision(
            self, show_id, sequence_id, revisioned_panels, markers,
            comment='From Hiero'):
        """new_sequence_revision will create a new sequence revision
        show_id: show ID
        sequence_id: sequence ID
        revisioned_panels: list of revisoned panels for the sequence revision
        markers: list of markers
        comment: comment of the sequence revision
        """

        url = '/show/{0}/sequence/{1}/revision'.format(show_id, sequence_id)
        content = {
            'comment': comment,
            'imported': False,
            'meta_data': {
                'annotations': [],
                'audio_timings': [],
                'highlights': [],
                'markers': markers},
            'revisioned_panels': revisioned_panels}
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            req = urllib2.Request(self.hostname + url,
                                  headers=headers, data=json.dumps(content))
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except BaseException:
            print('Could not create sequence revision')
            return None
        return response

    def new_panel(self, show_id, sequence_id, asset_id=None, duration=12):
        """new_panel will create a blank panel
        show_id: show ID
        sequence_id: sequence ID
        asset_id: asset ID
        duration: duration
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
            req = urllib2.Request(self.hostname + url,
                                  headers=headers, data=json.dumps(content))
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except BaseException:
            print('Could not create blank panel')
            return None
        return response

    def reset(self):
        """reset will reset the user info"""
        self.hostname = None
        self.secret = None
        self.expiry = None
        self.login = None
        self.password = None
        self.key = None

    def __get_token(self):
        """__get_token will request a token and reset it if it is too
        close to expiry
        """
        if (self.key is None or self.secret is None or self.expiry is None or
                datetime.now() + timedelta(hours=2) > self.expiry):
            authentificationToken = self.authenticate(
                self.hostname, self.login, self.password)
            self.key = authentificationToken['id']
            self.secret = authentificationToken['secret_access_key']
            self.expiry = datetime.strptime(
                authentificationToken
                ['expiry_date'].split('.')[0],
                '%Y-%m-%dT%H:%M:%S')
        return self.key, self.secret

    def __fn_sign(
            self, access_key_id, secret_access_key, url, content, http_method,
            content_type, dt):
        """After being logged in, you will have a token. This token will be
        use to sign your requests.
        accessKeyId: Access key ID from your token
        secretAccessKey: Secret access key from your token
        url: Url of the request
        content: Content of your request
        httpMethod: Http Method of your request
        contentType: Content Type of your request
        """
        raw_string = http_method.upper() + '\n'
        content_md5 = ''
        if content:
            if isinstance(content, str):
                content_md5 = hashlib.md5(content).hexdigest()
            elif isinstance(content, bytes):
                content_md5 = hashlib.md5(
                    binascii.hexlify(content)).hexdigest()
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
            raise ValueError('FnSigner: You must specify a secret_access_key')
        digest_created = base64.b64encode(
            hmac.new(
                secret_access_key.encode('utf-8'),
                raw_string.encode('utf-8'),
                digestmod=hashlib.sha256).digest())
        return 'FNAUTH ' + access_key_id + ':' + digest_created.decode('utf-8')

    def __get_headers(self, content, url, method='POST'):
        """__get_headers will generate the header to make any request
        containing the authorization with signature
        content: content of the request
        url: url to make request
        method: request method
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
