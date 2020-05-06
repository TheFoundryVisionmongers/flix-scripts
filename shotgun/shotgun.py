import base64
import binascii
import functools
import hashlib
import hmac
import json
import os
import re
import sys
import tempfile
import time
import threading
import requests
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta

import shotgun_api3
from PySide2.QtGui import (QPixmap)
from PySide2.QtCore import (Qt, QCoreApplication, QRect)
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                               QLineEdit, QMessageBox, QProgressDialog,
                               QPushButton, QStackedWidget, QVBoxLayout,
                               QWidget)


class flix:

    def __init__(self):
        self.reset()

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
            r = requests.post(hostname + '/authenticate', headers=header, verify=False)
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
        self.expiry = datetime.strptime(response['expiry_date'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return response

    def get_shows(self):
        """get_shows retrieve the list of shows"""
        headers = self.__get_headers(None, '/shows', 'GET')
        response = None
        try:
            r = requests.get(self.hostname + '/shows', headers=headers, verify=False)
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

    def get_asset(self, asset_id):
        """get_asset retrieve an asset"""
        url = '/asset/{0}'.format(asset_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None

        try:
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve asset', err)
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
            r = requests.get(self.hostname + url, headers=headers, verify=False)
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
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            response = json.loads(r.content)
            response = response.get('sequences')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequences', err)
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
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            response = json.loads(r.content)
            response = response.get('panels')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve panels', err)
            return None
        return response

    def get_dialogues(self, show_id, sequence_id, revision_number):
        """get_dialogues retrieve the list of dialogues from a sequence revision
        show_id: show ID
        sequence_id: sequence ID
        revision_number: sequence revision number
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/dialogues'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            response = json.loads(r.content)
            response = response.get('dialogues')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve dialogues', err)
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
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequence revision', err)
            return None
        return response

    def download_media_object(self, temp_filepath, media_object_id):
        """download_media_object download a media object
        temp_filepath: filepath to store the downloaded image
        media_object_id: media object id
        """
        url = '/file/{0}/data'.format(media_object_id)
        headers = self.__get_headers(None, url, 'GET')
        try:
            r = requests.get(self.hostname + url, headers=headers, verify=False)
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

    def start_quicktime_export(self, show_id, sequence_id, seq_rev_number, panel_revisions, episode_id=None, include_dialogue=False):
        """start_quicktime_export will create a quicktime export
        show_id: show ID
        sequence_id: sequence ID
        seq_rev_number: sequence revision ID
        panel_revisions: revisioned panels to export
        include_dialogue: include dialogue or not
        """

        url = '/show/{0}/sequence/{1}/revision/{2}/export/quicktime'.format(show_id, sequence_id, seq_rev_number)
        if episode_id is not None:
            url = '/show/{0}/episode/{1}/sequence/{2}/revision/{3}/export/quicktime'.format(show_id, episode_id, sequence_id, seq_rev_number)
        content = {
            'include_dialogue': include_dialogue,
            'panel_revisions': panel_revisions
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers, data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not export quicktime', err)
            return None
        return response

    def get_chain(self, chain_id):
        """get_sequence_rev retrieve a chain
        chain_id: chain ID
        """
        url = '/chain/{0}'.format(chain_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers, verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve chain', err)
            return None
        return response

    def new_sequence_revision(self, show_id, sequence_id, revisioned_panels, markers, comment='From Hiero'):
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
            'meta_data': {'annotations': [], 'audio_timings': [], 'highlights': [], 'markers': markers},
            'revisioned_panels': revisioned_panels
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers, data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create sequence revision', err)
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
            r = requests.post(self.hostname + url, headers=headers, data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create blank panel', err)
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
        """__get_token will request a token and reset it if it is too close to expiry"""
        if self.key is None or self.secret is None or self.expiry is None or datetime.now() + timedelta(hours=2) > self.expiry:
            authentificationToken = self.authenticate(
                self.hostname, self.login, self.password)
            self.key = authentificationToken['id']
            self.secret = authentificationToken['secret_access_key']
            self.expiry = datetime.strptime(authentificationToken['expiry_date'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return self.key, self.secret

    def __fn_sign(self, access_key_id, secret_access_key, url, content, http_method, content_type, dt):
        """After being logged in, you will have a token. This token will be use to sign your requests.
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
                content_md5 = hashlib.md5(binascii.hexlify(content)).hexdigest()
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
            hmac.new(secret_access_key.encode('utf-8'), raw_string.encode('utf-8'), digestmod=hashlib.sha256).digest()
        )
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


class shotgun:
    def __init__(self, hostname, login, password):
        self.hostname = hostname
        self.login = login
        self.password = password
        self.sg = shotgun_api3.Shotgun(self.hostname, login=self.login, password=self.password)

    def get_project(self, project_name):
        project = self.sg.find_one('Project',  [['name', 'is', project_name]], ['id', 'name'])
        if project:
            return project
        else:
            print('Could not find {0} Project in SG'.format(project_name))
            return None

    def create_project(self, project_name):
        data = {
            'name': project_name,
        }
        return self.sg.create('Project', data)

    def get_sequence(self, project, seq_name):
        sFilters = [['project', 'is', project], ['code', 'is', seq_name]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Sequence', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Sequence in SG'.format(seq_name))
        return None

    def create_seq(self, project, seq_name):
        data = {
            'project': {"type": "Project", "id": project['id']},
            'code': seq_name,
            'sg_status_list': "ip"
        }
        return self.sg.create('Sequence', data)

    def get_shot(self, project, seq, shot_name):
        sFilters = [['project', 'is', project], ['sg_sequence', 'is', seq], ['code', 'is', shot_name]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Shot', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Shot in SG'.format(shot_name))
        return None

    def create_shot(self, project, seq, shot_name):
        data = {
            "project": {"type": "Project", "id": project['id']},
            'code': shot_name,
            'sg_sequence': {'type': 'Sequence', 'id': seq['id']},
            'sg_status_list': 'ip'
        }
        return self.sg.create('Shot', data)

    def get_version(self, project, shot):
        sFilters = [['project', 'is', project], ['entity', 'is', {'type': 'Shot', 'id': shot['id']}]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Version', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Version in SG'.format(shot['code']))
        return None

    def create_version(self, show, shot, version_number):
        data = {'project': {'type': 'Project', 'id': show['id']},
                'code': shot['code'] + "_v%03d" % version_number,
                'sg_status_list': 'rev',
                'entity': {'type': 'Shot', 'id': shot['id']}
                }
        return self.sg.create('Version', data)

    def upload_movie(self, version, movie_path):
        return self.sg.upload('Version', version['id'], movie_path, field_name='sg_uploaded_movie')


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.flix_api = flix()
        self.export_path = None
        self.authenticated = False
        self.setWindowTitle('Flix Production Handoff')

        h_main_box = QHBoxLayout()
        v_login_box = QVBoxLayout()
        v_sequence_box = QVBoxLayout()

        self.hostname = QLineEdit('http://localhost:1234')
        self.hostname.setMinimumWidth(200)
        hostname_label = QLabel('Flix Server')
        hostname_label.setBuddy(self.hostname)
        self.login = QLineEdit('admin')
        self.login.setMinimumWidth(200)
        login_label = QLabel('Username')
        login_label.setBuddy(self.login)
        self.password = QLineEdit('admin')
        self.password.setMinimumWidth(200)
        self.password.setEchoMode(QLineEdit.Password)
        password_label = QLabel('Password')
        password_label.setBuddy(self.password)
        self.submit = QPushButton('Log In')
        self.submit.clicked.connect(self.authenticate)

        login_layout = QVBoxLayout()
        login_layout.addWidget(hostname_label)
        login_layout.addWidget(self.hostname)
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password)
        login_layout.addWidget(self.submit)
        login_widget = QWidget()
        login_widget.setLayout(login_layout)
        login_widget.setMaximumHeight(250)

        picture = QPixmap('./flix.png')
        picture = picture.scaledToHeight(120)

        label = QLabel()
        label.setPixmap(picture)

        v_login_box.addWidget(login_widget, alignment=Qt.AlignTop)
        v_login_box.addWidget(label, alignment=Qt.AlignCenter)

        self.show_list = QComboBox()
        show_label = QLabel('Show')
        show_label.setMinimumWidth(400)
        show_label.setBuddy(self.show_list)
        self.show_list.currentTextChanged.connect(self.on_show_changed)
        self.episode_list = QComboBox()
        self.episode_label = QLabel('Episode')
        self.episode_label.setBuddy(self.episode_list)
        self.episode_list.currentTextChanged.connect(self.on_episode_changed)
        self.sequence_list = QComboBox()
        sequence_label = QLabel('Sequence')
        sequence_label.setBuddy(self.sequence_list)
        self.sequence_list.currentTextChanged.connect(self.on_sequence_changed)

        self.handoff_type_list = QComboBox()
        self.handoff_type_list.addItems(['Local Export', 'Shotgun Export'])
        self.handoff_type_label = QLabel('Handoff Type')
        self.handoff_type_label.setBuddy(self.handoff_type_list)
        self.handoff_type_list.currentTextChanged.connect(self.on_handoff_type_changed)

        self.export_layout = QHBoxLayout()
        self.export_path = QLineEdit()
        self.export_path_label = QLabel('Export path')
        self.export_path_label.setBuddy(self.export_path)
        self.export_path_button = QPushButton('Browse')
        self.export_path_button.clicked.connect(self.browse_export_path)
        self.export_layout.addWidget(self.export_path)
        self.export_layout.addWidget(self.export_path_button)

        self.sg_hostname = QLineEdit('https://thomaslacroix.shotgunstudio.com')
        self.sg_hostname.setMinimumWidth(350)
        self.sg_hostname_label = QLabel('Shotgun URL')
        self.sg_hostname_label.setBuddy(self.sg_hostname)
        self.sg_login = QLineEdit('thomas.lacroix@epitech.eu')
        self.sg_login.setMinimumWidth(200)
        self.sg_login_label = QLabel('Username')
        self.sg_login_label.setBuddy(self.sg_login)

        pull = QPushButton('Export Latest')
        pull.clicked.connect(self.pull_latest)
        v_sequence_box.addWidget(show_label)
        v_sequence_box.addWidget(self.show_list)
        v_sequence_box.addWidget(self.episode_label)
        v_sequence_box.addWidget(self.episode_list)
        v_sequence_box.addWidget(sequence_label)
        v_sequence_box.addWidget(self.sequence_list)

        v_sequence_box.addWidget(self.handoff_type_label)
        v_sequence_box.addWidget(self.handoff_type_list)

        v_sequence_box.addWidget(self.export_path_label)
        v_sequence_box.addLayout(self.export_layout)
        v_sequence_box.addWidget(self.sg_hostname_label)
        v_sequence_box.addWidget(self.sg_hostname)
        v_sequence_box.addWidget(self.sg_login_label)
        v_sequence_box.addWidget(self.sg_login)

        v_sequence_box.addWidget(pull)
        self.update_ui_handoff_type('Local Export')

        h_main_box.addLayout(v_login_box)
        h_main_box.addLayout(v_sequence_box)

        self.setLayout(h_main_box)

    def authenticate(self):
        """authenticate will authenticate a user and update the view"""
        if self.authenticated:
            self.flix_api.reset()
            self.authenticated = False
            self.reset('Log In')
            return

        credentials = self.flix_api.authenticate(self.hostname.text(), self.login.text(), self.password.text())
        if credentials is None:
            self.error('Could not authenticate user')
            self.login.clear()
            self.password.clear()
            return

        self.init_shows()
        self.authenticated = True
        self.reset('Log Out')

    def browse_export_path(self):
        dialog = QFileDialog()
        export_p = None
        if self.export_path.text() is not '':
            if os.path.exists(self.export_path.text()):
                export_p = self.export_path.text()
        export_p = dialog.getExistingDirectory(dir=export_p)
        if len(export_p) < 1:
            return
        self.export_path.setText(export_p)

    def init_shows(self):
        """init_shows will retrieve the list of show and update the UI"""
        shows = self.flix_api.get_shows()
        if shows is None:
            self.error('Could not retreive shows')
            return
        self.show_tracking_code = self.get_show_tracking_code(shows)
        self.show_list.clear()
        for s in self.show_tracking_code:
            self.show_list.addItem(s)
        self.show_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def reset(self, action='Log Out'):
        """reset will reset the login form / shows info for login / logout
        logout: action to handle, 'Log In' and 'Log Out'
        """
        if action == 'Log Out':
            self.hostname.setReadOnly(True)
            self.login.setReadOnly(True)
            self.password.setReadOnly(True)
            self.submit.setText('Log Out')
            return
        self.hostname.setReadOnly(False)
        self.login.setReadOnly(False)
        self.password.setReadOnly(False)
        self.show_list.clear()
        self.sequence_list.clear()
        self.episode_list.clear()
        self.submit.setText(action)

    def update_ui_handoff_type(self, handoff_type):
        if handoff_type == 'Local Export':
            self.sg_hostname.hide()
            self.sg_hostname_label.hide()
            self.sg_login.hide()
            self.sg_login_label.hide()
            self.export_path_label.show()
            self.export_path.show()
            self.export_path_button.show()
        else:
            self.sg_hostname.show()
            self.sg_hostname_label.show()
            self.sg_login.show()
            self.sg_login_label.show()
            self.export_path_label.hide()
            self.export_path.hide()
            self.export_path_button.hide()
        self.selected_handoff_type = handoff_type

    def sort_alphanumeric(self, d):
        """sort_alphanumeric will sort a dictionnary alphanumerically by his keys
        d: dictionnary to sort
        """
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        keys = sorted(d.keys(), key=alphanum_key)
        return OrderedDict((k, d[k]) for k in keys)

    def get_show_tracking_code(self, shows):
        """get_show_tracking_code will format the shows to have a mapping: tracking_code -> [show_id, episodic]
        shows: list of show
        """
        show_tracking_codes = {}
        if shows is None:
            return show_tracking_codes
        for s in shows:
            if s.get('hidden', False) is False:
                show_tracking_codes[s.get('tracking_code')] = [s.get('id'), s.get('episodic')]
        return self.sort_alphanumeric(show_tracking_codes)

    def get_sequence_tracking_code(self, sequences):
        """get_sequence_tracking_code will format the sequences to have a mapping: tracking_code -> [sequence_id, last_seq_rev_id]
        sequences: list of sequence
        """
        sequence_tracking_codes = {}
        if sequences is None:
            return sequence_tracking_codes
        for s in sequences:
            if s.get('revisions_count') > 0:
                sequence_tracking_codes[s.get('tracking_code')] = [s.get('id'), s.get('revisions_count')]
        return self.sort_alphanumeric(sequence_tracking_codes)

    def get_episode_tracking_code(self, episodes):
        """get_episode_tracking_code will format the episodes to have a mapping: tracking_code -> episode_id
        episodes: list of episodes
        """
        episode_tracking_codes = {}
        if episodes is None:
            return episode_tracking_codes
        for s in episodes:
            episode_tracking_codes[s.get('tracking_code')] = s.get('id')
        return self.sort_alphanumeric(episode_tracking_codes)

    def on_handoff_type_changed(self, handoff_type):
        self.update_ui_handoff_type(handoff_type)

    def get_selected_show(self):
        stc = self.selected_show_tracking_code
        show_id = self.show_tracking_code[stc][0]
        episodic = self.show_tracking_code[stc][1]
        return show_id, episodic, stc

    def get_selected_episode(self):
        etc = self.selected_episode_tracking_code
        episode_id = self.episode_tracking_code[etc]
        return episode_id, etc

    def get_selected_sequence(self):
        stc = self.selected_sequence_tracking_code
        seq_id = self.sequence_tracking_code[stc][0]
        seq_rev = self.sequence_tracking_code[stc][1]
        return seq_id, seq_rev, stc

    def on_show_changed(self, tracking_code):
        """on_show_changed triggered after a show is selected, will init the list of sequences from this show
        tracking_code: show_tracking_code from the event
        """
        self.selected_show_tracking_code = tracking_code
        show_id, episodic, _ = self.get_selected_show()

        self.sequence_list.clear()
        self.episode_list.clear()
        if episodic is True:
            self.episode_list.show()
            self.episode_label.show()
            episodes = self.flix_api.get_episodes(show_id)
            if episodes is None:
                self.error('Could not retrieve episodes')
            self.episode_tracking_code = self.get_episode_tracking_code(episodes)
            for e in self.episode_tracking_code:
                self.episode_list.addItem(e)
            self.episode_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        else:
            self.episode_list.hide()
            self.episode_label.hide()
            sequences = self.flix_api.get_sequences(show_id)
            if sequences is None:
                self.error('Could not retreive sequences')
                return
            self.sequence_tracking_code = self.get_sequence_tracking_code(sequences)
            for s in self.sequence_tracking_code:
                self.sequence_list.addItem(s)
            self.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def on_episode_changed(self, tracking_code):
        """on_episode_changed triggered after an episode is selected, will store the selected episode
        tracking_code: episode_tracking_code from the event
        """
        if tracking_code == '':
            return
        self.selected_episode_tracking_code = tracking_code
        show_id, _, _ = self.get_selected_show()
        episode_id, _ = self.get_selected_episode()
        sequences = self.flix_api.get_sequences(show_id, episode_id)
        if sequences is None:
            self.error('Could not retreive sequences')
            return
        self.sequence_tracking_code = self.get_sequence_tracking_code(sequences)
        self.sequence_list.clear()
        for s in self.sequence_tracking_code:
            self.sequence_list.addItem(s)
        self.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def on_sequence_changed(self, tracking_code):
        """on_sequence_changed triggered after a sequence is selected, will store the selected sequence
        tracking_code: sequence_tracking_code from the event
        """
        self.selected_sequence_tracking_code = tracking_code

    def error(self, message):
        """error will show a error message with a given message
        message: message to show
        """
        err = QErrorMessage(self.parent())
        err.setWindowTitle('Flix')
        err.showMessage(message)
        err.exec_()

    def info(self, message):
        """info will show a message with a given message
        message: message to show"""
        msgbox = QMessageBox(self.parent())
        msgbox.setWindowTitle('Flix')
        msgbox.setText(message)
        msgbox.exec_()

    def format_panel_for_revision(self, panel, pos):
        """format_panel_for_revision will format the panel as revisioned panel
        panel: panel to format
        """
        return {
            'dialogue': panel.get('dialogue'),
            'duration': panel.get('duration'),
            'id': panel.get('panel_id'),
            'revision_number': panel.get('revision_number'),
            'asset': panel.get('asset'),
            'pos': pos
        }

    def get_markers(self, sequence_revision):
        """get_markers will format the sequence_revision to have a mapping of markers: start -> marker_name
        sequences_revision: sequence revision entity
        """
        markers_mapping = {}
        markers = sequence_revision.get('meta_data', {}).get('markers', [])
        for m in markers:
            markers_mapping[m.get('start')] = m.get('name')
        return OrderedDict(sorted(markers_mapping.items()))

    def get_markers_per_panels(self, markers, panels):
        """get_markers_per_panels will return a mapping of markers per panels
        markers: list of markers
        panels: list of panels
        """
        panels_per_markers = {}
        panel_in = 0
        markers_keys = list(markers.keys())
        marker_i = 0
        for i, p in enumerate(panels):
            if markers_keys[marker_i] == panel_in:
                panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(self.format_panel_for_revision(p, i))
                if len(markers_keys) > marker_i+1:
                    marker_i = marker_i+1
            elif markers_keys[marker_i] > panel_in:
                panels_per_markers[markers[markers_keys[marker_i-1]]].append(self.format_panel_for_revision(p, i))
            elif len(markers_keys)-1 == marker_i:
                if markers[markers_keys[marker_i]] not in panels_per_markers:
                    panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(self.format_panel_for_revision(p, i))
            panel_in = panel_in + p.get('duration')
        return panels_per_markers

    def mo_per_shots(self, panels_per_markers, show_id, seq_id, seq_rev_number, episode_id=None):
        """mo_per_shots will make a mapping of all media objects per shots
        panels_per_markers: panels per markers
        show_id: show ID
        seq_id: sequence ID
        seq_rev_number: sequence revision number
        episode_id: episode ID (optional)
        """
        mo_per_shots = {}
        for shot_name in panels_per_markers:
            mo_per_shots[shot_name] = {'artwork': [], 'thumbnails': []}
            panels = panels_per_markers[shot_name]
            for p in panels:
                asset = self.flix_api.get_asset(p.get('asset').get('asset_id'))
                if asset is None:
                    self.error('Could not retrieve asset')
                    return None, False
                mo_per_shots[shot_name]['artwork'].append({
                    'name': asset.get('media_objects', {}).get('artwork')[0].get('name'),
                    'id': p.get('id'),
                    'revision_number': p.get('revision_number'),
                    'pos': p.get('pos'),
                    'mo': asset.get('media_objects', {}).get('artwork')[0].get('id')
                })
                mo_per_shots[shot_name]['thumbnails'].append({
                    'name': asset.get('media_objects', {}).get('thumbnail')[0].get('name'),
                    'id': p.get('id'),
                    'revision_number': p.get('revision_number'),
                    'pos': p.get('pos'),
                    'mo': asset.get('media_objects', {}).get('thumbnail')[0].get('id')
                })
            if self.update_progress('Export quicktime from Flix for shot {0}'.format(shot_name), True) is False:
                return None, False
            chain_id = self.flix_api.start_quicktime_export(show_id, seq_id, seq_rev_number, panels, episode_id, False)
            while True:
                res = self.flix_api.get_chain(chain_id)
                if res is None or res.get('status') == 'errored' or res.get('status') == 'timed out':
                    self.error('Could not export quicktime')
                    return None, False
                if res.get('status') == 'in progress':
                    time.sleep(1)
                    continue
                if res.get('status') == 'completed':
                    asset = self.flix_api.get_asset(res.get('results', {}).get('assetID'))
                    if asset is None:
                        self.error('Could not retrieve asset')
                        return None, False
                    mo_per_shots[shot_name]['mov'] = asset.get('media_objects', {}).get('artwork', [])[0].get('id')
                    break
        return mo_per_shots, True

    def create_folder(self, path):
        """create_folder will create a folder if it does not exist
        path: path of the folder
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def create_folders(self, base):
        """create_folders will create the structure of folders from shows to sequence revision
        base: base of the folder creation
        """
        _, episodic, show_tracking_code = self.get_selected_show()
        _, seq_rev_number, seq_tracking_code = self.get_selected_sequence()
        show_path = os.path.join(base, show_tracking_code)
        self.create_folder(show_path)
        sequence_path = os.path.join(show_path, seq_tracking_code)
        if episodic:
            _, episode_tracking_code = self.get_selected_episode()
            episode_path = os.path.join(show_path, episode_tracking_code)
            self.create_folder(episode_path)
            sequence_path = os.path.join(episode_path, seq_tracking_code)
        self.create_folder(sequence_path)
        sequence_revision_path = os.path.join(sequence_path, 'v{0}'.format(seq_rev_number))
        self.create_folder(sequence_revision_path)
        return sequence_revision_path

    def get_default_image_name(self, seq_rev_number, panel_pos, panel_id, panel_revision):
        """get_default_image_name will format the image name
        seq_rev_number: sequence revision number
        panel_pos: position of the panel in the sequence
        panel_id: panel ID
        panel_revision: panel revision
        """
        _, _, show_tracking_code = self.get_selected_show()
        _, _, seq_tracking_code = self.get_selected_sequence()
        return '{0}_{1}_v{2}_{3}_{4}_v{5}'.format(show_tracking_code,
                                                  seq_tracking_code, seq_rev_number,
                                                  panel_pos, panel_id, panel_revision)

    def download_files(self, export_path, mo_per_shots):
        """download_files will download all the media objects and put them in the correct directory
        export_path: path to export files
        mo_per_shots: media objects per shots
        """
        _, seq_rev_number, seq_tracking_code = self.get_selected_sequence()
        for _, shot in enumerate(mo_per_shots):
            shot_path = os.path.join(export_path, shot)
            self.create_folder(shot_path)
            mov_name = '{0}_v{1}_{2}.mov'.format(seq_tracking_code, seq_rev_number, shot)
            mov_path = os.path.join(shot_path, mov_name)
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                mov_path = mov_path.replace('\\', '\\\\')
            self.flix_api.download_media_object(mov_path, mo_per_shots[shot].get('mov'))
            artwork_folder_path = os.path.join(shot_path, 'artwork')
            self.create_folder(artwork_folder_path)
            if self.update_progress('Download artworks for shot {0}'.format(shot), True) is False:
                return
            for artwork in mo_per_shots[shot].get('artwork', []):
                ext = os.path.splitext(artwork.get('name'))
                art_name = self.get_default_image_name(seq_rev_number, artwork.get('pos'), artwork.get('id'), artwork.get('revision_number'))
                artwork_path = os.path.join(artwork_folder_path, '{0}{1}'.format(art_name, ext[1]))
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    artwork_path = artwork_path.replace('\\', '\\\\')
                self.flix_api.download_media_object(artwork_path, artwork.get('mo'))
            thumb_folder_path = os.path.join(shot_path, 'thumbnail')
            self.create_folder(thumb_folder_path)
            if self.update_progress('Download thumbnails for shot {0}'.format(shot), True) is False:
                return
            for thumb in mo_per_shots[shot].get('thumbnails', []):
                ext = os.path.splitext(thumb.get('name'))
                art_name = self.get_default_image_name(seq_rev_number, thumb.get('pos'), thumb.get('id'), thumb.get('revision_number'))
                thumb_path = os.path.join(thumb_folder_path, '{0}{1}'.format(art_name, ext[1]))
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    thumb_path = thumb_path.replace('\\', '\\\\')
                self.flix_api.download_media_object(thumb_path, thumb.get('mo'))
        return True

    def push_to_sg(self, mo_per_shots, sg_password):
        _, _, show_name = self.get_selected_show()
        _, seq_rev_number, seq_name = self.get_selected_sequence()
        sg_show = self.shotgun.get_project(show_name)
        if sg_show is None:
            sg_show = self.shotgun.create_project(show_name)
        sg_seq = self.shotgun.get_sequence(sg_show, seq_name)
        if sg_seq is None:
            sg_seq = self.shotgun.create_seq(sg_show, seq_name)
        temp_folder = tempfile.gettempdir()
        for shot_name in mo_per_shots:
            if self.update_progress('Push shot {0} to Shotgun'.format(shot_name), True) is False:
                return False
            sg_shot = self.shotgun.get_shot(sg_show, sg_seq, shot_name)
            if sg_shot is None:
                sg_shot = self.shotgun.create_shot(sg_show, sg_seq, shot_name)
            version = self.shotgun.get_version(sg_show, sg_shot)
            if version is None:
                new_version = 1
            else:
                ver = re.search('(.*)v([0-9]+)', version['code'])
                new_version = int(ver.group(2)) + 1
            version = self.shotgun.create_version(sg_show, sg_shot, new_version)
            mov_name = '{0}_v{1}_{2}.mov'.format(seq_name, seq_rev_number, shot_name)
            temp_quicktime_path = os.path.join(temp_folder, mov_name)
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                temp_quicktime_path = temp_quicktime_path.replace('\\', '\\\\')            
            if self.flix_api.download_media_object(temp_quicktime_path, mo_per_shots[shot_name].get('mov')) is None:
                self.error('could not download quicktime for shot {0}'.format(shot_name))
                continue
            if self.update_progress('Upload movie for shot {0} to Shotgun'.format(shot_name), True) is False:
                return False
            self.shotgun.upload_movie(version, temp_quicktime_path)
        return True

    def update_progress(self, message, keep_value=False, start=False):
        if start:
            self.progress_start = 0
        next_value = self.progress_start
        if keep_value is False:
            next_value = next_value + 1
        self.progress_start = next_value
        self.progress.setValue(next_value)
        self.progress.setLabelText(message)
        self.progress.repaint()
        QCoreApplication.processEvents()
        if self.progress.wasCanceled():
            return False
        return True

    def init_local_export(self):
        if len(self.export_path.text()) <= 0:
            self.info('You need to select an export path')
            return False
        if os.path.exists(self.export_path.text()) is False:
            self.info('Invalid export path')
            return False
        return True

    def init_shotgun_export(self):
        if self.sg_login.text() == '' or self.sg_hostname.text() == '':
            self.info('You need to enter your shotgun info')
            return '', False
        sg_password, ok = QInputDialog().getText(self, 'Shotgun password', 'Shotgun password:', QLineEdit.Password)
        if ok is False:
            return '', False
        self.shotgun = shotgun(self.sg_hostname.text(), self.sg_login.text(), sg_password)
        try:
            _, _, stc = self.get_selected_show()
            self.shotgun.get_project(stc)
        except:
            self.progress.hide()
            self.error('could not login to shotgun')
            return '', False
        return sg_password, True

    def pull_latest(self):
        """pull_latest will export the latest sequence revision"""
        if not self.authenticated:
            self.info('You should log in first')
            return

        self.progress = QProgressDialog("Operation in progress.", 'Stop', 0, 7)
        self.progress.setMinimumWidth(400)
        self.progress.setMinimumHeight(100)
        self.progress.show()
        if self.selected_handoff_type == 'Local Export':
            if self.init_local_export() is False:
                self.progress.hide()
                return
        else:
            sg_password, ok = self.init_shotgun_export()
            if ok is False:
                self.progress.hide()
                return

        show_id, episodic, _ = self.get_selected_show()
        seq_id, seq_rev_number, _ = self.get_selected_sequence()
        seq_rev = self.flix_api.get_sequence_rev(show_id, seq_id, seq_rev_number)
        episode_id = None
        if episodic:
            episode_id, _ = self.get_selected_episode()
        if seq_rev is None:
            self.progress.hide()
            self.error('Could not retrieve sequence revision')
            return
        if self.update_progress('Get markers', False, True) is False:
            return
        markers = self.get_markers(seq_rev)
        if len(markers) < 1:
            self.progress.hide()
            self.info('You need at least one shot')
            return
        if self.update_progress('Get Panels') is False:
            return
        panels = self.flix_api.get_panels(show_id, seq_id, seq_rev_number)
        if panels is None:
            self.progress.hide()
            self.error('Could not retrieve panels')
            return

        if self.update_progress('Get Markers') is False:
            return
        panels_per_markers = self.get_markers_per_panels(markers, panels)
        if self.update_progress('Get Assets info') is False:
            return
        mo_per_shots, ok = self.mo_per_shots(panels_per_markers, show_id, seq_id, seq_rev_number, episode_id)
        if mo_per_shots is None:
            self.progress.hide()
            self.error('Could not retrieve media objects per shots')
            return
        if ok is False:
            return

        if self.selected_handoff_type == 'Local Export':
            if self.update_progress('Create folders for export') is False:
                return
            seq_rev_path = self.create_folders(self.export_path.text())
            if self.update_progress('Download files') is False:
                return
            if self.download_files(seq_rev_path, mo_per_shots) is False:
                return
        else:
            if self.update_progress('Push to Shotgun') is False:
                return
            self.push_to_sg(mo_per_shots, sg_password)
            if self.update_progress('Pushed to Shotgun') is False:
                return
        if self.update_progress('Finished') is False:
            return
        self.info('Sequence revision exported successfully')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
