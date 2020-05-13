import os
import re
import sys
import tempfile
import time
from collections import OrderedDict
from typing import Dict, List, Tuple

from PySide2.QtCore import QCoreApplication, QRect, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                               QLineEdit, QMessageBox, QProgressDialog,
                               QPushButton, QStackedWidget, QVBoxLayout,
                               QWidget)

import flix as flix_api
import shotgun as shotgun_api


class main_dialogue(QDialog):

    def __init__(cls, parent=None):
        super(main_dialogue, cls).__init__(parent)
        cls.flix_api = flix_api.flix()
        cls.export_path = None
        cls.authenticated = False
        cls.setWindowTitle('Flix Production Handoff')

        h_main_box = QHBoxLayout()
        v_login_box = QVBoxLayout()
        v_sequence_box = QVBoxLayout()

        cls.hostname = QLineEdit('http://localhost:1234')
        cls.hostname.setMinimumWidth(200)
        hostname_label = QLabel('Flix Server')
        hostname_label.setBuddy(cls.hostname)
        cls.login = QLineEdit('admin')
        cls.login.setMinimumWidth(200)
        login_label = QLabel('Username')
        login_label.setBuddy(cls.login)
        cls.password = QLineEdit('admin')
        cls.password.setMinimumWidth(200)
        cls.password.setEchoMode(QLineEdit.Password)
        password_label = QLabel('Password')
        password_label.setBuddy(cls.password)
        cls.submit = QPushButton('Log In')
        cls.submit.clicked.connect(cls.authenticate)

        login_layout = QVBoxLayout()
        login_layout.addWidget(hostname_label)
        login_layout.addWidget(cls.hostname)
        login_layout.addWidget(login_label)
        login_layout.addWidget(cls.login)
        login_layout.addWidget(password_label)
        login_layout.addWidget(cls.password)
        login_layout.addWidget(cls.submit)
        login_widget = QWidget()
        login_widget.setLayout(login_layout)
        login_widget.setMaximumHeight(250)

        picture = QPixmap('./flix.png')
        picture = picture.scaledToHeight(120)

        label = QLabel()
        label.setPixmap(picture)

        v_login_box.addWidget(login_widget, alignment=Qt.AlignTop)
        v_login_box.addWidget(label, alignment=Qt.AlignCenter)

        cls.show_list = QComboBox()
        show_label = QLabel('Show')
        show_label.setMinimumWidth(400)
        show_label.setBuddy(cls.show_list)
        cls.show_list.currentTextChanged.connect(cls.on_show_changed)
        cls.episode_list = QComboBox()
        cls.episode_label = QLabel('Episode')
        cls.episode_label.setBuddy(cls.episode_list)
        cls.episode_list.currentTextChanged.connect(cls.on_episode_changed)
        cls.sequence_list = QComboBox()
        sequence_label = QLabel('Sequence')
        sequence_label.setBuddy(cls.sequence_list)
        cls.sequence_list.currentTextChanged.connect(cls.on_sequence_changed)

        cls.handoff_type_list = QComboBox()
        cls.handoff_type_list.addItems(['Local Export', 'Shotgun Export'])
        cls.handoff_type_label = QLabel('Handoff Type')
        cls.handoff_type_label.setBuddy(cls.handoff_type_list)
        cls.handoff_type_list.currentTextChanged.connect(
            cls.on_handoff_type_changed)

        cls.export_layout = QHBoxLayout()
        cls.export_path = QLineEdit()
        cls.export_path_label = QLabel('Export path')
        cls.export_path_label.setBuddy(cls.export_path)
        cls.export_path_button = QPushButton('Browse')
        cls.export_path_button.clicked.connect(cls.browse_export_path)
        cls.export_layout.addWidget(cls.export_path)
        cls.export_layout.addWidget(cls.export_path_button)

        cls.sg_hostname = QLineEdit('https://thomaslacroix.shotgunstudio.com')
        cls.sg_hostname.setMinimumWidth(350)
        cls.sg_hostname_label = QLabel('Shotgun URL')
        cls.sg_hostname_label.setBuddy(cls.sg_hostname)
        cls.sg_login = QLineEdit('thomas.lacroix@epitech.eu')
        cls.sg_login.setMinimumWidth(200)
        cls.sg_login_label = QLabel('Username')
        cls.sg_login_label.setBuddy(cls.sg_login)

        pull = QPushButton('Export Latest')
        pull.clicked.connect(cls.pull_latest)
        v_sequence_box.addWidget(show_label)
        v_sequence_box.addWidget(cls.show_list)
        v_sequence_box.addWidget(cls.episode_label)
        v_sequence_box.addWidget(cls.episode_list)
        v_sequence_box.addWidget(sequence_label)
        v_sequence_box.addWidget(cls.sequence_list)

        v_sequence_box.addWidget(cls.handoff_type_label)
        v_sequence_box.addWidget(cls.handoff_type_list)

        v_sequence_box.addWidget(cls.export_path_label)
        v_sequence_box.addLayout(cls.export_layout)
        v_sequence_box.addWidget(cls.sg_hostname_label)
        v_sequence_box.addWidget(cls.sg_hostname)
        v_sequence_box.addWidget(cls.sg_login_label)
        v_sequence_box.addWidget(cls.sg_login)

        v_sequence_box.addWidget(pull)
        cls.update_ui_handoff_type('Local Export')

        h_main_box.addLayout(v_login_box)
        h_main_box.addLayout(v_sequence_box)

        cls.setLayout(h_main_box)

    def authenticate(cls):
        """authenticate will authenticate a user and update the view
        """
        if cls.authenticated:
            cls.flix_api.reset()
            cls.authenticated = False
            cls.reset('Log In')
            return

        credentials = cls.flix_api.authenticate(cls.hostname.text(),
                                                cls.login.text(),
                                                cls.password.text())
        if credentials is None:
            cls.error('Could not authenticate user')
            cls.login.clear()
            cls.password.clear()
            return

        cls.init_shows()
        cls.authenticated = True
        cls.reset('Log Out')

    def error(cls, message: str):
        """error will show a error message with a given message

        Arguments:
            message {str} -- Message to show
        """
        err = QErrorMessage(cls.parent())
        err.setWindowTitle('Flix')
        err.showMessage(message)
        err.exec_()

    def info(cls, message: str):
        """info will show a message with a given message

        Arguments:
            message {str} -- Message to show
        """
        msgbox = QMessageBox(cls.parent())
        msgbox.setWindowTitle('Flix')
        msgbox.setText(message)
        msgbox.exec_()

    def reset(cls, action: str = 'Log Out'):
        """reset will reset the login form / shows info for login / logout

        Keyword Arguments:
            action {str} -- action to handle (default: {'Log Out'})
        """
        if action == 'Log Out':
            cls.hostname.setReadOnly(True)
            cls.login.setReadOnly(True)
            cls.password.setReadOnly(True)
            cls.submit.setText('Log Out')
            return
        cls.hostname.setReadOnly(False)
        cls.login.setReadOnly(False)
        cls.password.setReadOnly(False)
        cls.show_list.clear()
        cls.sequence_list.clear()
        cls.episode_list.clear()
        cls.submit.setText(action)

    def on_show_changed(cls, tracking_code: str):
        """on_show_changed triggered after a show is selected,
        will init the list of sequences from this show

        Arguments:
            tracking_code {str} -- show_tracking_code from the event
        """
        cls.selected_show_tracking_code = tracking_code
        show_id, episodic, _ = cls.get_selected_show()

        cls.sequence_list.clear()
        cls.episode_list.clear()
        if episodic is True:
            cls.episode_list.show()
            cls.episode_label.show()
            episodes = cls.flix_api.get_episodes(show_id)
            if episodes is None:
                cls.error('Could not retrieve episodes')
                return
            cls.episode_tracking_code = cls.get_episode_tracking_code(
                episodes)
            for e in cls.episode_tracking_code:
                cls.episode_list.addItem(e)
            cls.episode_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            return
        cls.episode_list.hide()
        cls.episode_label.hide()
        sequences = cls.flix_api.get_sequences(show_id)
        if sequences is None:
            cls.error('Could not retreive sequences')
            return
        cls.sequence_tracking_code = cls.get_sequence_tracking_code(
            sequences)
        for s in cls.sequence_tracking_code:
            cls.sequence_list.addItem(s)
        cls.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def on_episode_changed(cls, tracking_code: str):
        """on_episode_changed triggered after an episode is selected,
        will store the selected episode

        Arguments:
            tracking_code {str} -- episode_tracking_code from the event
        """
        if tracking_code == '':
            return
        cls.selected_episode_tracking_code = tracking_code
        show_id, _, _ = cls.get_selected_show()
        episode_id, _ = cls.get_selected_episode()
        sequences = cls.flix_api.get_sequences(show_id, episode_id)
        if sequences is None:
            cls.error('Could not retreive sequences')
            return
        cls.sequence_tracking_code = cls.get_sequence_tracking_code(
            sequences)
        cls.sequence_list.clear()
        for s in cls.sequence_tracking_code:
            cls.sequence_list.addItem(s)
        cls.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def on_sequence_changed(cls, tracking_code: str):
        """on_sequence_changed triggered after a sequence is selected,
        will store the selected sequence

        Arguments:
            tracking_code {str} -- sequence_tracking_code from the event
        """
        cls.selected_sequence_tracking_code = tracking_code

    def on_handoff_type_changed(cls, handoff_type: str):
        """on_handoff_type_changed triggered when the handoff type changed

        Arguments:
            handoff_type {str} -- Handoff type from the event
        """
        cls.update_ui_handoff_type(handoff_type)

    def browse_export_path(cls):
        """browse_export_path will create a dialog window to
        browse and set an export path
        """
        dialog = QFileDialog()
        export_p = None
        if cls.export_path.text() is not '':
            if os.path.exists(cls.export_path.text()):
                export_p = cls.export_path.text()
        export_p = dialog.getExistingDirectory(dir=export_p)
        if len(export_p) < 1:
            return
        cls.export_path.setText(export_p)

    def init_shows(cls):
        """init_shows will retrieve the list of show and update the UI
        """
        shows = cls.flix_api.get_shows()
        if shows is None:
            cls.error('Could not retreive shows')
            return
        cls.show_tracking_code = cls.get_show_tracking_code(shows)
        cls.show_list.clear()
        for s in cls.show_tracking_code:
            cls.show_list.addItem(s)
        cls.show_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def update_ui_handoff_type(cls, handoff_type: str):
        """update_ui_handoff_type will update the UI depending
        of the handoff type

        Arguments:
            handoff_type {str} -- Handoff type
        """
        if handoff_type == 'Local Export':
            cls.sg_hostname.hide()
            cls.sg_hostname_label.hide()
            cls.sg_login.hide()
            cls.sg_login_label.hide()
            cls.export_path_label.show()
            cls.export_path.show()
            cls.export_path_button.show()
        else:
            cls.sg_hostname.show()
            cls.sg_hostname_label.show()
            cls.sg_login.show()
            cls.sg_login_label.show()
            cls.export_path_label.hide()
            cls.export_path.hide()
            cls.export_path_button.hide()
        cls.selected_handoff_type = handoff_type

    def sort_alphanumeric(cls, d: Dict) -> Dict:
        """sort_alphanumeric will sort a dictionnary alphanumerically by keys

        Arguments:
            d {Dict} -- Dictionnary to sort

        Returns:
            Dict -- Sorted Dictionnary
        """
        def convert(text): return int(text) if text.isdigit() else text
        def alphanum_key(key): return [convert(c)
                                       for c in re.split('([0-9]+)', key)]
        keys = sorted(d.keys(), key=alphanum_key)
        return OrderedDict((k, d[k]) for k in keys)

    def get_show_tracking_code(cls, shows: List) -> Dict:
        """get_show_tracking_code will format the shows to have a mapping:
        tracking_code -> [show_id, episodic]

        Arguments:
            shows {List} -- List of shows

        Returns:
            Dict -- Shows by tracking code
        """
        show_tracking_codes = {}
        if shows is None:
            return show_tracking_codes
        for s in shows:
            if s.get('hidden', False) is False:
                show_tracking_codes[s.get('tracking_code')] = [
                    s.get('id'),
                    s.get('episodic')
                ]
        return cls.sort_alphanumeric(show_tracking_codes)

    def get_sequence_tracking_code(cls, sequences: List) -> Dict:
        """get_sequence_tracking_code will format the sequences to have
        a mapping: tracking_code -> [sequence_id, last_seq_rev_id]

        Arguments:
            sequences {List} -- List of sequences

        Returns:
            Dict -- sequence ID and last seq rev by tracking code
        """
        sequence_tracking_codes = {}
        if sequences is None:
            return sequence_tracking_codes
        for s in sequences:
            if s.get('revisions_count') > 0:
                sequence_tracking_codes[s.get('tracking_code')] = [
                    s.get('id'),
                    s.get('revisions_count')
                ]
        return cls.sort_alphanumeric(sequence_tracking_codes)

    def get_episode_tracking_code(cls, episodes: List) -> Dict:
        """get_episode_tracking_code will format the episodes to have a
        mapping: tracking_code -> episode_id

        Arguments:
            episodes {List} -- List of episodes

        Returns:
            Dict -- Episodes by tracking code
        """
        episode_tracking_codes = {}
        if episodes is None:
            return episode_tracking_codes
        for s in episodes:
            episode_tracking_codes[s.get('tracking_code')] = s.get('id')
        return cls.sort_alphanumeric(episode_tracking_codes)

    def get_selected_show(cls) -> Tuple(int, bool, str):
        """get_selected_show will return the selected show info

        Returns:
            Tuple(int, bool, str) -- Show ID, Episodic, Show tracking code
        """
        stc = cls.selected_show_tracking_code
        show_id = cls.show_tracking_code[stc][0]
        episodic = cls.show_tracking_code[stc][1]
        return show_id, episodic, stc

    def get_selected_episode(cls) -> Tuple(int, str):
        """get_selected_episode will return the selected episode info

        Returns:
            Tuple(int, str) -- Episode ID, Episode tracking code
        """
        etc = cls.selected_episode_tracking_code
        episode_id = cls.episode_tracking_code[etc]
        return episode_id, etc

    def get_selected_sequence(cls) -> Tuple(int, int, str):
        """get_selected_sequence will return the selected sequence info

        Returns:
            Tuple(int, int, str) -- Sequence ID, Seq rev ID, seq tracking code
        """
        stc = cls.selected_sequence_tracking_code
        seq_id = cls.sequence_tracking_code[stc][0]
        seq_rev = cls.sequence_tracking_code[stc][1]
        return seq_id, seq_rev, stc

    def format_panel_for_revision(cls, panel: object, pos: int) -> object:
        """format_panel_for_revision will format the panel as
        revisionned panel

        Arguments:
            panel {object} -- Panel from Flix
            pos {int} -- Position in the Flix timeline

        Returns:
            object -- Formatted panel
        """
        return {
            'dialogue': panel.get('dialogue'),
            'duration': panel.get('duration'),
            'id': panel.get('panel_id'),
            'revision_number': panel.get('revision_number'),
            'asset': panel.get('asset'),
            'pos': pos
        }

    def get_markers(cls, sequence_revision: object) -> Dict:
        """get_markers will format the sequence_revision to have a
        mapping of markers: start -> marker_name

        Arguments:
            sequence_revision {object} -- Sequence revision

        Returns:
            Dict -- Markers by start time
        """
        markers_mapping = {}
        markers = sequence_revision.get('meta_data', {}).get('markers', [])
        for m in markers:
            markers_mapping[m.get('start')] = m.get('name')
        return OrderedDict(sorted(markers_mapping.items()))

    def get_markers_per_panels(cls, markers: List, panels: List) -> Dict:
        """get_markers_per_panels will return a mapping of markers per panels

        Arguments:
            markers {List} -- List of markers
            panels {List} -- List of panels

        Returns:
            Dict -- Panels per markers
        """
        panels_per_markers = {}
        panel_in = 0
        markers_keys = list(markers.keys())
        marker_i = 0
        for i, p in enumerate(panels):
            if markers_keys[marker_i] == panel_in:
                panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(
                    cls.format_panel_for_revision(p, i))
                if len(markers_keys) > marker_i + 1:
                    marker_i = marker_i + 1
            elif markers_keys[marker_i] > panel_in:
                panels_per_markers[markers[markers_keys[marker_i - 1]]].append(
                    cls.format_panel_for_revision(p, i))
            elif len(markers_keys) - 1 == marker_i:
                if markers[markers_keys[marker_i]] not in panels_per_markers:
                    panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(
                    cls.format_panel_for_revision(p, i))
            panel_in = panel_in + p.get('duration')
        return panels_per_markers

    def mo_per_shots(cls,
                     panels_per_markers: Dict,
                     show_id: int,
                     seq_id: int,
                     seq_rev_number: int,
                     episode_id: int = None) -> Dict:
        """mo_per_shots will make a mapping of all media objects per shots

        Arguments:
            panels_per_markers {Dict} -- Panels per markers
            show_id {int} -- Show ID
            seq_id {int} -- Sequence ID
            seq_rev_number {int} -- Sequence Revision ID

        Keyword Arguments:
            episode_id {int} -- Episode ID (default: {None})

        Returns:
            Dict -- Media objects per shots
        """
        mo_per_shots = {}
        for shot_name in panels_per_markers:
            mo_per_shots[shot_name] = {'artwork': [], 'thumbnails': []}
            panels = panels_per_markers[shot_name]
            for p in panels:
                asset = cls.flix_api.get_asset(p.get('asset').get('asset_id'))
                if asset is None:
                    cls.error('Could not retrieve asset')
                    return None, False
                artwork = asset.get('media_objects', {}).get('artwork')[0]
                mo_per_shots[shot_name]['artwork'].append({
                    'name': artwork.get('name'),
                    'id': p.get('id'),
                    'revision_number': p.get('revision_number'),
                    'pos': p.get('pos'),
                    'mo': artwork.get('id')
                })
                mo_per_shots[shot_name]['thumbnails'].append(
                    {'name': asset.get('media_objects', {}).get('thumbnail')
                     [0].get('name'),
                     'id': p.get('id'),
                     'revision_number': p.get('revision_number'),
                     'pos': p.get('pos'),
                     'mo': asset.get('media_objects', {}).get('thumbnail')
                     [0].get('id')})
            if cls.update_progress(
                'Export quicktime from Flix for shot {0}'.format(shot_name),
                    True) is False:
                return None, False
            chain_id = cls.flix_api.start_quicktime_export(
                show_id, seq_id, seq_rev_number, panels, episode_id, False)
            while True:
                res = cls.flix_api.get_chain(chain_id)
                if res is None or res.get('status') == 'errored' or res.get(
                        'status') == 'timed out':
                    cls.error('Could not export quicktime')
                    return None, False
                if res.get('status') == 'in progress':
                    time.sleep(1)
                    continue
                if res.get('status') == 'completed':
                    asset = cls.flix_api.get_asset(
                        res.get('results', {}).get('assetID'))
                    if asset is None:
                        cls.error('Could not retrieve asset')
                        return None, False
                    mo_per_shots[shot_name]['mov'] = asset.get(
                        'media_objects', {}).get('artwork', [])[0].get('id')
                    break
        return mo_per_shots, True

    def create_folder(cls, path: str):
        """create_folder will create a folder if it does not exist

        Arguments:
            path {str} -- Path to create the folder
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def create_folders(cls, base: str) -> str:
        """create_folders will create the structure of folders from
        shows to sequence revision

        Arguments:
            base {str} -- base of the folder creation

        Returns:
            str -- Sequence revision path
        """
        _, episodic, show_tracking_code = cls.get_selected_show()
        _, seq_rev_number, seq_tracking_code = cls.get_selected_sequence()
        show_path = os.path.join(base, show_tracking_code)
        cls.create_folder(show_path)
        sequence_path = os.path.join(show_path, seq_tracking_code)
        if episodic:
            _, episode_tracking_code = cls.get_selected_episode()
            episode_path = os.path.join(show_path, episode_tracking_code)
            cls.create_folder(episode_path)
            sequence_path = os.path.join(episode_path, seq_tracking_code)
        cls.create_folder(sequence_path)
        sequence_revision_path = os.path.join(
            sequence_path, 'v{0}'.format(seq_rev_number))
        cls.create_folder(sequence_revision_path)
        return sequence_revision_path

    def get_default_image_name(
            cls,
            seq_rev_number: int,
            panel_pos: int,
            panel_id: int,
            panel_revision: int) -> str:
        """get_default_image_name will format the image name

        Arguments:
            seq_rev_number {int} -- Sequence revision number
            panel_pos {int} -- Panel position
            panel_id {int} -- Panel ID
            panel_revision {int} -- Panel revision

        Returns:
            str -- Formatted name
        """
        _, _, show_tracking_code = cls.get_selected_show()
        _, _, seq_tracking_code = cls.get_selected_sequence()
        return '{0}_{1}_v{2}_{3}_{4}_v{5}'.format(
            show_tracking_code,
            seq_tracking_code,
            seq_rev_number,
            panel_pos,
            panel_id,
            panel_revision)

    def download_files(cls, export_path: str, mo_per_shots: Dict) -> bool:
        """download_files will download all the media objects

        Arguments:
            export_path {str} -- Path to export files
            mo_per_shots {Dict} -- Media objects per shots

        Returns:
            bool -- State of the download file
        """
        _, seq_rev_number, seq_tracking_code = cls.get_selected_sequence()
        for _, shot in enumerate(mo_per_shots):
            shot_path = os.path.join(export_path, shot)
            cls.create_folder(shot_path)
            mov_name = '{0}_v{1}_{2}.mov'.format(
                seq_tracking_code, seq_rev_number, shot)
            mov_path = os.path.join(shot_path, mov_name)
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                mov_path = mov_path.replace('\\', '\\\\')
            cls.flix_api.download_media_object(
                mov_path, mo_per_shots[shot].get('mov'))
            artwork_folder_path = os.path.join(shot_path, 'artwork')
            cls.create_folder(artwork_folder_path)
            if cls.update_progress(
                'Download artworks for shot {0}'.format(shot),
                    True) is False:
                return
            for artwork in mo_per_shots[shot].get('artwork', []):
                ext = os.path.splitext(artwork.get('name'))
                art_name = cls.get_default_image_name(
                    seq_rev_number, artwork.get('pos'),
                    artwork.get('id'),
                    artwork.get('revision_number'))
                artwork_path = os.path.join(
                    artwork_folder_path, '{0}{1}'.format(art_name, ext[1]))
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    artwork_path = artwork_path.replace('\\', '\\\\')
                cls.flix_api.download_media_object(
                    artwork_path, artwork.get('mo'))
            thumb_folder_path = os.path.join(shot_path, 'thumbnail')
            cls.create_folder(thumb_folder_path)
            if cls.update_progress(
                'Download thumbnails for shot {0}'.format(shot),
                    True) is False:
                return
            for thumb in mo_per_shots[shot].get('thumbnails', []):
                ext = os.path.splitext(thumb.get('name'))
                art_name = cls.get_default_image_name(
                    seq_rev_number, thumb.get('pos'),
                    thumb.get('id'),
                    thumb.get('revision_number'))
                thumb_path = os.path.join(
                    thumb_folder_path, '{0}{1}'.format(art_name, ext[1]))
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    thumb_path = thumb_path.replace('\\', '\\\\')
                cls.flix_api.download_media_object(
                    thumb_path, thumb.get('mo'))
        return True

    def push_to_sg(cls, mo_per_shots: Dict, sg_password: str) -> bool:
        """push_to_sg will push a sequence revision to Shotgun
        Will return False if an error occurred or if the
        user stop from the progress

        Arguments:
            mo_per_shots {Dict} -- Media objects per shots
            sg_password {str} -- Shotgun password

        Returns:
            bool -- State of the push to shotgun
        """
        _, _, show_name = cls.get_selected_show()
        _, seq_rev_number, seq_name = cls.get_selected_sequence()
        sg_show = cls.shotgun.get_project(show_name)
        if sg_show is None:
            sg_show = cls.shotgun.create_project(show_name)
        sg_seq = cls.shotgun.get_sequence(sg_show, seq_name)
        if sg_seq is None:
            sg_seq = cls.shotgun.create_seq(sg_show, seq_name)
        temp_folder = tempfile.gettempdir()
        for shot_name in mo_per_shots:
            if cls.update_progress(
                'Push shot {0} to Shotgun'.format(shot_name),
                    True) is False:
                return False
            sg_shot = cls.shotgun.get_shot(sg_show, sg_seq, shot_name)
            if sg_shot is None:
                sg_shot = cls.shotgun.create_shot(sg_show, sg_seq, shot_name)
            version = cls.shotgun.get_version(sg_show, sg_shot)
            if version is None:
                new_version = 1
            else:
                ver = re.search('(.*)v([0-9]+)', version['code'])
                new_version = int(ver.group(2)) + 1
            version = cls.shotgun.create_version(
                sg_show, sg_shot, new_version)
            mov_name = '{0}_v{1}_{2}.mov'.format(
                seq_name, seq_rev_number, shot_name)
            temp_quicktime_path = os.path.join(temp_folder, mov_name)
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                temp_quicktime_path = temp_quicktime_path.replace('\\', '\\\\')
            if cls.flix_api.download_media_object(
                    temp_quicktime_path,
                    mo_per_shots[shot_name].get('mov')) is None:
                cls.error(
                    'could not download quicktime for shot {0}'.format(
                        shot_name))
                continue
            title_progress = 'Upload movie for shot {0} to Shotgun'.format(
                shot_name)
            if cls.update_progress(title_progress, True) is False:
                return False
            cls.shotgun.upload_movie(version, temp_quicktime_path)
        return True

    def update_progress(cls,
                        message: str,
                        keep_value: bool = False,
                        start: bool = False) -> bool:
        """update_progress will update the progress message
        and will return False if the progress is 'canceled' by the user

        Arguments:
            message {str} -- Message to show in the progress

        Keyword Arguments:
            keep_value {bool} -- Keep previous value (default: {False})
            start {bool} -- Fist start (default: {False})

        Returns:
            bool -- Progress not stopped
        """
        if start:
            cls.progress_start = 0
        next_value = cls.progress_start
        if keep_value is False:
            next_value = next_value + 1
        cls.progress_start = next_value
        cls.progress.setValue(next_value)
        cls.progress.setLabelText(message)
        cls.progress.repaint()
        QCoreApplication.processEvents()
        if cls.progress.wasCanceled():
            return False
        return True

    def init_local_export(cls) -> bool:
        """init_local_export will initialise the export

        Returns:
            bool -- If the export path is valid or not
        """
        if len(cls.export_path.text()) <= 0:
            cls.info('You need to select an export path')
            return False
        if os.path.exists(cls.export_path.text()) is False:
            cls.info('Invalid export path')
            return False
        return True

    def init_shotgun_export(cls) -> bool:
        """init_shotgun_export will init the shotgun export

        Returns:
            bool -- Can login to shotgun
        """
        if cls.sg_login.text() == '' or cls.sg_hostname.text() == '':
            cls.info('You need to enter your shotgun info')
            return '', False
        sg_password, ok = QInputDialog().getText(cls,
                                                 'Shotgun password',
                                                 'Shotgun password:',
                                                 QLineEdit.Password)
        if ok is False:
            return '', False
        cls.shotgun = shotgun_api.shotgun(cls.sg_hostname.text(),
                                          cls.sg_login.text(),
                                          sg_password)
        try:
            _, _, stc = cls.get_selected_show()
            cls.shotgun.get_project(stc)
        except BaseException:
            cls.progress.hide()
            cls.error('could not login to shotgun')
            return '', False
        return sg_password, True

    def pull_latest(cls):
        """pull_latest will export the latest sequence revision
        """
        if not cls.authenticated:
            cls.info('You should log in first')
            return
        cls.progress = QProgressDialog('Operation in progress.',
                                       'Stop',
                                       0,
                                       7)
        cls.progress.setMinimumWidth(400)
        cls.progress.setMinimumHeight(100)
        cls.progress.show()

        if cls.selected_handoff_type == 'Local Export':
            if cls.init_local_export() is False:
                cls.progress.hide()
                return
        else:
            sg_password, ok = cls.init_shotgun_export()
            if ok is False:
                cls.progress.hide()
                return

        show_id, episodic, _ = cls.get_selected_show()
        seq_id, seq_rev_number, _ = cls.get_selected_sequence()
        seq_rev = cls.flix_api.get_sequence_rev(show_id,
                                                seq_id,
                                                seq_rev_number)
        episode_id = None
        if episodic:
            episode_id, _ = cls.get_selected_episode()
        if seq_rev is None:
            cls.progress.hide()
            cls.error('Could not retrieve sequence revision')
            return
        if cls.update_progress('Get markers', False, True) is False:
            return
        markers = cls.get_markers(seq_rev)
        if len(markers) < 1:
            cls.progress.hide()
            cls.info('You need at least one shot')
            return
        if cls.update_progress('Get Panels') is False:
            return
        panels = cls.flix_api.get_panels(show_id, seq_id, seq_rev_number)
        if panels is None:
            cls.progress.hide()
            cls.error('Could not retrieve panels')
            return

        if cls.update_progress('Get Markers') is False:
            return
        panels_per_markers = cls.get_markers_per_panels(markers, panels)
        if cls.update_progress('Get Assets info') is False:
            return
        mo_per_shots, ok = cls.mo_per_shots(panels_per_markers,
                                            show_id,
                                            seq_id,
                                            seq_rev_number,
                                            episode_id)
        if mo_per_shots is None:
            cls.progress.hide()
            cls.error('Could not retrieve media objects per shots')
            return
        if ok is False:
            return

        if cls.selected_handoff_type == 'Local Export':
            if cls.update_progress('Create folders for export') is False:
                return
            seq_rev_path = cls.create_folders(cls.export_path.text())
            if cls.update_progress('Download files') is False:
                return
            if cls.download_files(seq_rev_path, mo_per_shots) is False:
                return
        else:
            if cls.update_progress('Push to Shotgun') is False:
                return
            cls.push_to_sg(mo_per_shots, sg_password)
            if cls.update_progress('Pushed to Shotgun') is False:
                return
        if cls.update_progress('Finished') is False:
            return
        cls.info('Sequence revision exported successfully')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
