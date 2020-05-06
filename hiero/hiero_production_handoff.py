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
import urllib2
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta

from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QStackedWidget,
                               QVBoxLayout)

from hiero.core import (Bin, BinItem, Format, Sequence, Tag, VideoTrack,
                        newProject)
from hiero.ui import addMenuAction, createMenuAction


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
        except:
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
        except:
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
        except:
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
        except:
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
        except:
            print('Could not retrieve panels')
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
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
            response = response.get('dialogues')
        except:
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
        except:
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
            file = open(temp_filepath, "w")
            file.write(response)
            file.close()
        except:
            print('Could not retrieve thumbnail')
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
            req = urllib2.Request(self.hostname + url, headers=headers, data=json.dumps(content))
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except:
            print('Could not export quicktime')
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
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except:
            print('Could not retrieve chain')
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
            req = urllib2.Request(self.hostname + url, headers=headers, data=json.dumps(content))
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except:
            print('Could not create sequence revision')
            return None
        return response
    
    def get_asset(self, asset_id):
        """get_asset retrieve an asset"""
        url = '/asset/{0}'.format(asset_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None

        try:
            req = urllib2.Request(self.hostname + url, headers=headers)
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except:
            print('Could not retrieve asset')
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
            req = urllib2.Request(self.hostname + url, headers=headers, data=json.dumps(content))
            response = urllib2.urlopen(req).read()
            response = json.loads(response)
        except:
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


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.flix_api = flix()
        self.authenticated = False
        self.setWindowTitle("Flix Production Handoff")
        self.preset_comment_tag = hiero.core.findProjectTags(hiero.core.project('Tag Presets'), 'Comment')[0]
        self.preset_fr_tag_tag = hiero.core.findProjectTags(hiero.core.project('Tag Presets'), 'France')[0]
        self.preset_ready_to_start_tag = hiero.core.findProjectTags(hiero.core.project('Tag Presets'), 'Ready To Start')[0]
        self.preset_ref_tag = hiero.core.findProjectTags(hiero.core.project('Tag Presets'), 'Reference')[0]

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

        v_login_box.addWidget(hostname_label)
        v_login_box.addWidget(self.hostname)
        v_login_box.addWidget(login_label)
        v_login_box.addWidget(self.login)
        v_login_box.addWidget(password_label)
        v_login_box.addWidget(self.password)
        v_login_box.addWidget(self.submit)
        self.submit.clicked.connect(self.authenticate)

        self.show_list = QComboBox()
        show_label = QLabel('Show')
        show_label.setMinimumWidth(200)
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
        self.handoff_type_list.addItems(['Panels', 'Shots'])
        handoff_type_label = QLabel('Handoff Type')
        handoff_type_label.setBuddy(self.handoff_type_list)
        self.handoff_type_list.currentTextChanged.connect(self.on_handoff_type_changed)
        self.selected_handoff_type = 'Panels'

        pull = QPushButton("Pull Latest")
        pull.clicked.connect(self.pull_latest)
        v_sequence_box.addWidget(show_label)
        v_sequence_box.addWidget(self.show_list)
        v_sequence_box.addWidget(self.episode_label)
        v_sequence_box.addWidget(self.episode_list)
        v_sequence_box.addWidget(sequence_label)
        v_sequence_box.addWidget(self.sequence_list)
        v_sequence_box.addWidget(handoff_type_label)
        v_sequence_box.addWidget(self.handoff_type_list)
        v_sequence_box.addWidget(pull)

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

    def get_dialogues_by_panel_id(self, dialogues):
        """get_dialogues_by_panel_id will format the dialogues to have a mapping panel_id -> dialogue
        dialogues: list of dialogue
        """
        mapped_dialogues = {}
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        for d in dialogues:
            t = d.get('text', '').replace('</p>', '\n')
            mapped_dialogues[d.get('panel_id')] = re.sub(cleanr, '', t)
        return mapped_dialogues

    def on_show_changed(self, tracking_code):
        """on_show_changed triggered after a show is selected, will init the list of sequences from this show
        tracking_code: show_tracking_code from the event
        """
        self.selected_show_tracking_code = tracking_code
        show_id = self.show_tracking_code[tracking_code][0]
        episodic = self.show_tracking_code[tracking_code][1]

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
            self.sequence_list.addItem('All Sequences')
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
        show_id = self.show_tracking_code[self.selected_show_tracking_code][0]
        episode_id = self.episode_tracking_code[tracking_code]
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

    def on_handoff_type_changed(self, handoff_type):
        self.selected_handoff_type = handoff_type

    def update_sequence_items(self):
        """update_sequence_items will refresh the list of sequence from the selected show"""
        show_id = self.show_tracking_code[self.selected_show_tracking_code][0]
        episodic = self.show_tracking_code[self.selected_show_tracking_code][1]
        episode_id = None
        if episodic:
            episode_id = self.episode_tracking_code[self.selected_episode_tracking_code]
        sequences = self.flix_api.get_sequences(show_id, episode_id)
        if sequences is None:
            self.error('Could not retreive sequences')
            return
        self.sequence_tracking_code = self.get_sequence_tracking_code(sequences)

    def add_track_item(self, track, track_item_name, source_clip, duration=12, tags=[], last_track_item=None):
        """add_track_item will add a trackitem to a track, it will add a source and tags
        track: track to add the new track item
        track_item_name: name of the new track item
        source_clip: clip to link to the track item
        duration: duration of the clip
        tags: list of tags to add to the new track_item
        last_track_item: previous track item to link them all
        """
        track_item = track.createTrackItem(track_item_name)
        track_item.setSource(source_clip)
        for t in tags:
            track_item.addTag(t)
        if last_track_item:
            track_item.setTimelineIn(last_track_item.timelineOut() + 1)
            track_item.setTimelineOut(last_track_item.timelineOut() + duration)
        else:
            track_item.setTimelineIn(0)
            track_item.setTimelineOut(duration - 1)

        track.addTrackItem(track_item)
        return track_item

    def get_project(self, project_name):
        """get_project will reuse existing project depending of the project name or will create it
        project_name: project to find
        """
        my_project = hiero.core.project(project_name)
        if my_project is None:
            my_project = newProject(project_name)
        f = Format(1000, 562, 1, 'flix')
        my_project.setOutputFormat(f)
        return my_project

    def get_project_bin(self, project_bin, bin_name):
        """get_project_bin will try to reuse a bin from a project depending on the bin_name or will create it
        project_bin: is the project bin
        bin_name: bin's name to search
        """
        b = project_bin.bins(bin_name)
        if len(b) > 0:
            b = b[0]
            return b, True
        return Bin(bin_name), False

    def get_seq_bin(self, host_b, bin_name):
        """get_seq_bin will try to reuse a bin from a project depending on the bin_name or will create it
            host_b: is the host bin
            bin_name: bin's name to search
        """
        b = host_b.bins()
        for seq_bin in b:
            if seq_bin.name() == bin_name:
                return seq_bin, True
        return Bin(bin_name), False

    def get_clips(self, seq_bin):
        """get_clips will retrieve all the clips from the bin
        seq_bin: bin of the sequence
        """
        clips = {}
        for b in seq_bin.bins():
            for c in b.clips():
                clips[c.name()] = c.activeItem()
        return clips

    def create_clip(self, seq_rev_bin, media_object, clip_name, clips):
        """create_clip will create a clip and download image or reuse one
        seq_rev_bin: sequence bin
        p: panel entity
        clip_name: name of the clip
        clips: list of all clips
        """
        if clip_name not in clips:
            temp_path = tempfile.mkdtemp()
            thumb_mo_id = media_object.get('id')
            if thumb_mo_id is None:
                self.error('Could not retrieve thumbnail ID')
                return None
            ext = os.path.splitext(media_object.get('name'))
            temp_filepath = os.path.join(temp_path, '{0}{1}'.format(clip_name, ext[1]))
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                temp_filepath = temp_filepath.replace('\\', '\\\\')
            if self.flix_api.download_media_object(temp_filepath, thumb_mo_id) is None:
                self.error('Could not download thumbnail')
                return None
            return seq_rev_bin.createClip(temp_filepath)
        return clips[clip_name]

    def get_comment_tag(self, p):
        """get_comment_tag will make a copy of a comment tag and set his comment as a note
        p: panel entity
        """
        comment = p.get('latest_open_note', {}).get('body', None)
        t = None
        if comment is not None:
            t = self.preset_comment_tag.copy()
            cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            comment = re.sub(cleanr, '', comment)
            t.setNote(comment)
        return t

    def add_dialogue(self, mapped_dialogue, panel_id, track, prev):
        """add_dialogue will create a dialogue and add it to the track
        mapped_dialogue: mapping of dialogue to ensure there is a dialogue for the panel
        panel_id: panel ID
        track: track to add the dialogue
        prev: previous trackitem
        """
        if panel_id in mapped_dialogue:
            node = track.createEffect(effectType='Text2', trackItem=prev, subTrackIndex=0).node()
            dialogue_settings = {
                'name': 'dialogue-[{0}]'.format(uuid.uuid4()),
                'message': mapped_dialogue[panel_id],
                'opacity': .6,
                'global_font_scale': .3,
                'enable_background': True,
                'background_opacity': .6,
                'box': (0, 0, 1000, 562),
                'xjustify': 1,
                'yjustify': 2
            }
            for name, value in dialogue_settings.iteritems():
                node[name].setValue(value)

    def create_burnin(self, track, fr, to, burnin_name):
        """create_burnin will create a burnin and add it to the track
        track: track to add the burnin
        fr: from where to start the burnin (frame)
        to: from where to end the burnin (frame)
        burnin_name: name of the burnin
        """
        node = track.createEffect(effectType='BurnIn', subTrackIndex=0, timelineIn=fr, timelineOut=to).node()
        burnin_settings = {
            'name': '{0}-[{1}]'.format(burnin_name, uuid.uuid4()),
            'burnIn_textScale': .25,
            'burnIn_topLeft': 'hiero/clip',
            'burnIn_topMiddle': 'none',
            'burnIn_topRight': 'hiero/sequence/timecode',
            'burnIn_bottomLeft': 'none',
            'burnIn_bottomMiddle': 'none',
            'burnIn_bottomRight': 'none',
            'burnIn_backgroundEnable': 'true',
            'burnIn_backgroundXBorder': 10,
            'burnIn_backgroundYBorder': 10,
            'burnIn_backgroundOpacity': .6,
        }

        for name, value in burnin_settings.iteritems():
            node[name].setValue(value)

    def get_markers(self, sequence_revision):
        """get_markers will format the sequence_revision to have a mapping of markers: start -> marker_name
        sequences_revision: sequence revision entity
        """
        markers_mapping = {}
        markers = sequence_revision.get('meta_data', {}).get('markers', [])
        for m in markers:
            markers_mapping[m.get('start')] = m.get('name')
        return OrderedDict(sorted(markers_mapping.items()))

    def create_marker(self, in_time, marker_name):
        """create_marker will create a marker
        in_time: start of the marker
        marker_name: name of the marker
        """
        t = self.preset_ready_to_start_tag.copy()
        t.setNote(marker_name)
        t.metadata().setValue('tag.start', '{0}'.format(in_time))
        t.metadata().setValue('tag.length', '{0}'.format(1))
        t.setInTime(in_time)
        t.setOutTime(in_time + 1)
        return t

    def add_burnin(self, panels, panel_in, markers_mapping, marker_tmp, marker_in, shots, p, i):
        """add_burnin will add a burnin in a VideoTrack
        panels: list of panels
        panel_in: first frame of the panel (from the whole timeline)
        markers_mapping: mapping of markers
        marker_in: first frame of the marker to add as burnin
        shots: video track to add the burnin
        p: actual panel
        i: position of the panel
        """
        if panel_in in markers_mapping and markers_mapping[panel_in] != marker_tmp:
            if marker_in is not None:
                self.create_burnin(shots, marker_in, panel_in - 1, markers_mapping[panel_in])
            marker_in = panel_in
        if len(panels) - 1 == i and marker_in is not None:
            self.create_burnin(shots, marker_in, panel_in + p.get('duration') - 1, marker_tmp)
        return marker_in

    def add_comment(self, p, tags):
        """add_comment will add a tag comment to the list
        p: actual panel
        tags: list of tags
        """
        comment_tag = self.get_comment_tag(p)
        if comment_tag is not None:
            tags.append(comment_tag)
        return tags

    def add_panel_info_tag(self, p, tags):
        """add_panel_info_tag will add a tag of the panel info
        p: actual panel
        tags: list of tags
        """
        t = self.preset_fr_tag_tag.copy()
        t.setNote(json.dumps(p))
        t.setVisible(False)
        tags.append(t)
        return tags

    def add_marker(self, markers_mapping, panel_in, sequence):
        """add_marker will add a marker in the sequence
        markers_mapping: mapping of markers
        panel_in: first frame of the panel(from the whole sequence)
        sequence: sequence to add to
        """
        if panel_in in markers_mapping:
            sequence.addTagToRange(self.create_marker(panel_in, markers_mapping[panel_in]), panel_in, panel_in + 1)

    def create_video_track(self, sequence, seq_bin, seq_rev_bin, seq_id, seq_rev_number):
        """create_video_track will create 2 videos tracks, one for the sequence and one for shots
        sequence: sequence
        seq_bin: sequence bin
        seq_rev: sequence revision bin
        seq_id: sequence ID
        seq_rev_number: sequence revision count
        """
        track = VideoTrack('Flix_{0}_v{1}'.format(self.selected_sequence_tracking_code, seq_rev_number))
        show_id = self.show_tracking_code[self.selected_show_tracking_code][0]
        sequence_revision = self.flix_api.get_sequence_rev(show_id, seq_id, seq_rev_number)
        if sequence_revision is None:
            self.error('Could not retreive sequence revision')
            return
        panels = self.flix_api.get_panels(show_id, seq_id, seq_rev_number)
        if panels is None:
            self.error('Could not retreive panels')
            return

        if self.selected_handoff_type == 'Panels':
            return self.create_panels_video_track(track, sequence, show_id, seq_id, seq_rev_number,
                                                  panels, sequence_revision, seq_bin, seq_rev_bin)
        return self.create_shots_video_track(track, sequence, show_id, seq_id, seq_rev_number,
                                                panels, sequence_revision, seq_bin, seq_rev_bin)

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

    def mo_per_shots(self, panels_per_markers, show_id, seq_id, seq_rev_number):
        """mo_per_shots will make a mapping of all media objects per shots
        panels_per_markers: panels per markers
        show_id: show ID
        seq_id: sequence ID
        seq_rev_number: sequence revision number
        episode_id: episode ID (optional)
        """
        mo_per_shots = {}
        for shot_name in panels_per_markers:
            mo_per_shots[shot_name] = {}
            panels = panels_per_markers[shot_name]
            shot_duration = 0
            for p in panels:
                shot_duration = shot_duration + p.get('duration')
            mo_per_shots[shot_name]['duration'] = shot_duration
            chain_id = self.flix_api.start_quicktime_export(show_id, seq_id, seq_rev_number, panels)
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
                    mo_per_shots[shot_name]['mov'] = asset.get('media_objects', {}).get('artwork', [])[0]
                    break
        return mo_per_shots, True

    def create_panels_video_track(self, track, sequence, show_id, seq_id, seq_rev_number, panels, sequence_revision, seq_bin, seq_rev_bin):
        dialogues = self.flix_api.get_dialogues(show_id, seq_id, seq_rev_number)
        mapped_dialogue = self.get_dialogues_by_panel_id(dialogues)
        markers_mapping = self.get_markers(sequence_revision)
        shots = VideoTrack('Shots') if len(markers_mapping) > 0 else None
        clips = self.get_clips(seq_bin)

        prev = None
        panel_in = 0
        marker_in = None
        prev_marker_name = None

        for i, p in enumerate(panels):
            tags = []
            panel_id = p.get('panel_id')
            clip_name = '{0}_{1}_{2}_'.format(self.selected_sequence_tracking_code, panel_id, p.get('revision_counter'))
            media_objects = p.get('asset', {}).get('media_objects', {}).get('thumbnail', [])
            if len(media_objects) < 1:
                self.error('could not get media object')
                return track, shots
            clip = self.create_clip(seq_rev_bin, media_objects[0], clip_name, clips)
            if clip is None:
                self.error('could not create clip: {0}'.format(clip_name))
                return track, shots

            # Add comment
            tags = self.add_comment(p, tags)
            # Add panel info
            tags = self.add_panel_info_tag(p, tags)
            # Add marker
            self.add_marker(markers_mapping, panel_in, sequence)
            # Add track item
            prev = self.add_track_item(track, clip_name, clip, p.get('duration'), tags, prev)
            # Add dialogue
            self.add_dialogue(mapped_dialogue, panel_id, track, prev)
            # Add burnin
            marker_in = self.add_burnin(panels, panel_in, markers_mapping, prev_marker_name, marker_in, shots, p, i)

            if panel_in in markers_mapping:
                prev_marker_name = markers_mapping[panel_in]
            panel_in = panel_in + p.get('duration')    
    
        return track, shots

    def create_shots_video_track(self, track, sequence, show_id, seq_id, seq_rev_number, panels, sequence_revision, seq_bin, seq_rev_bin):
        clips = self.get_clips(seq_bin)
        markers = self.get_markers(sequence_revision)
        if len(markers) < 1:
            self.info('You need at least one shot')
            return track, None
        panels_per_markers = self.get_markers_per_panels(markers, panels)
        mo_per_shots, ok = self.mo_per_shots(panels_per_markers, show_id, seq_id, seq_rev_number)
        if mo_per_shots is None:
            self.error('Could not retrieve media objects per shots')
            return track, None
        if ok is False:
            return track, None

        prev = None
        print(markers)
        print(mo_per_shots)
        for _, shot_name in enumerate(markers.values()):
            clip_name = '{0}_{1}'.format(self.selected_sequence_tracking_code, shot_name)

            media_object = mo_per_shots[shot_name]['mov']
            clip = self.create_clip(seq_rev_bin, media_object, clip_name, clips)
            if clip is None:
                self.error('could not create clip: {0}'.format(clip_name))
                return track, None
            prev = self.add_track_item(track, clip_name, clip, mo_per_shots[shot_name]['duration'], [], prev)
    
        return track, None

    def pull_latest_seq_rev(self):
        # Update sequence mapping to have the last seq rev info
        self.update_sequence_items()

        seq_id = self.sequence_tracking_code[self.selected_sequence_tracking_code][0]
        seq_rev_number = self.sequence_tracking_code[self.selected_sequence_tracking_code][1]

        my_project = self.get_project('Flix_{0}'.format(self.selected_show_tracking_code))
        seq, seq_bin_reused = self.get_project_bin(my_project, 'Flix_{0}'.format(self.selected_sequence_tracking_code))
        if seq_bin_reused is False:
            clipsBin = my_project.clipsBin()
            clipsBin.addItem(seq)

        seq_rev_bin, seq_rev_bin_reused = self.get_seq_bin(seq, 'v{0}'.format(seq_rev_number))
        if seq_rev_bin_reused is False:
            seq.addItem(seq_rev_bin)

        sequence = Sequence('Flix_{0}_v{1}'.format(self.selected_sequence_tracking_code, seq_rev_number))
        seq_rev_bin.addItem(BinItem(sequence))
        track, shots = self.create_video_track(sequence, seq, seq_rev_bin, seq_id, seq_rev_number)
        if track is None:
            return
        sequence.addTrack(track)
        if shots is not None:
            sequence.addTrack(shots)

    def pull_latest(self):
        """pull_latest will retrieve the last sequence revision from Flix and will create / reuse bins, sequences, clips"""

        if self.selected_sequence_tracking_code == 'All Sequences':
            for count in range(self.sequence_list.count()):
                if self.sequence_list.itemText(count) == 'All Sequences':
                    continue
                self.selected_sequence_tracking_code = self.sequence_list.itemText(count)
                self.pull_latest_seq_rev()
        else:
            self.pull_latest_seq_rev()

        self.selected_sequence_tracking_code = 'All Sequences'
        self.info('Sequence revision imported successfully')

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

main_view = main_dialogue()
wm = hiero.ui.windowManager()
wm.addWindow(main_view)
