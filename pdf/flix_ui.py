#
# Copyright (C) Foundry 2020
#

import os
import re
import sys
from collections import OrderedDict
from typing import Callable, Dict, List, Tuple

from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)

import flix as flix_api


class flix_ui(QWidget):
    """flix_ui is a widget that allow you to login / logout
    Select a show, episode and sequences
    There is some exported events:
    e_login: dict representing the credentials
    e_logout: event representing the logout
    e_show_changed: show ID, Tracking code, episodic
    e_episode_changed: episode ID, tracking code
    e_sequence_changed: sequence ID, sequence Revision number, tracking code
    """

    e_login = Signal(dict)
    e_logout = Signal()
    e_show_changed = Signal(int, str, bool)
    e_episode_changed = Signal(int, str)
    e_sequence_changed = Signal(int, int, str)
    e_sequence_rev_changed = Signal(dict)

    __selected_show_tracking_code = ''
    __selected_episode_tracking_code = ''
    __selected_sequence_tracking_code = ''

    __err_authenticate = 'You need to be authenticated'
    __err_show_not_found = 'Could not find show'
    __err_episode_not_found = 'Could not find episode'
    __err_sequence_not_found = 'Could not find sequence'
    __err_sequence_rev_not_found = 'Could not find sequence revision'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flix_api = flix_api.flix()
        self.authenticated = False
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        # Setup UI view
        v_main_box = QVBoxLayout()
        h_login_sequence = QHBoxLayout()
        v_login_layout = QVBoxLayout()
        v_sequence_box = QVBoxLayout()

        # Setup Flix Login view
        self.hostname, hostname_label = self.__create_line_label(
            'http://127.0.0.1:1234', 'Flix Server')
        self.login, login_label = self.__create_line_label('admin', 'Username')
        self.password, password_label = self.__create_line_label(
            'admin', 'Password', echo_mode=True)
        self.submit = QPushButton('Log In')
        self.submit.clicked.connect(self.__authenticate)

        # Add Login view to layout
        self.__add_widget_to_layout(v_login_layout,
                                    hostname_label,
                                    self.hostname,
                                    login_label,
                                    self.login,
                                    password_label,
                                    self.password,
                                    self.submit)

        # Setup lists for shows / episodes and sequences
        self.show_list, show_label = self.__create_combo_label(
            'Show', self.__on_show_changed)
        self.episode_list, self.episode_label = self.__create_combo_label(
            'Episode', self.__on_episode_changed)
        self.episode_list.hide()
        self.episode_label.hide()

        self.sequence_list, sequence_label = self.__create_combo_label(
            'Sequence', self.__on_sequence_changed)
        self.sequence_rev_list, sequence_rev_label = self.__create_combo_label(
            'Sequence Revision', self.__on_sequence_rev_changed)

        self.__add_widget_to_layout(v_sequence_box,
                                    show_label,
                                    self.show_list,
                                    self.episode_label,
                                    self.episode_list,
                                    sequence_label,
                                    self.sequence_list,
                                    sequence_rev_label,
                                    self.sequence_rev_list)

        h_login_sequence.addLayout(v_login_layout)
        h_login_sequence.addLayout(v_sequence_box)

        v_main_box.addLayout(h_login_sequence)

        # Add Flix logo
        picture = QPixmap('./flix.png')
        picture = picture.scaledToHeight(120)
        label = QLabel()
        label.setPixmap(picture)
        v_main_box.addWidget(label, alignment=Qt.AlignCenter)

        self.setLayout(v_main_box)

    def is_authenticated(self) -> bool:
        """is_authenticated will return the state of the authentication

        Returns:
            bool -- Authenticated or not
        """
        return self.authenticated

    def get_flix_api(self) -> flix_api.flix:
        """get_flix_api will return the flix_api

        Returns:
            flix_api.flix -- Flix api entity
        """
        return self.flix_api

    def get_selected_show(self) -> Tuple[int, bool, str]:
        """get_selected_show will return the selected show info

        Raises:
            RuntimeError: Show not found
            RuntimeError: Need authentication

        Returns:
            Tuple[int, bool, str] -- Show ID, Episodic, Show tracking code
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        stc = self.__selected_show_tracking_code
        if not (stc in self.show_tracking_code):
            raise RuntimeError(self.__err_show_not_found)
        show_id = self.show_tracking_code[stc][0]
        episodic = self.show_tracking_code[stc][1]
        return show_id, episodic, stc

    def get_selected_episode(self) -> Tuple[int, str]:
        """get_selected_episode will return the selected episode info

        Raises:
            RuntimeError: Episode not found
            RuntimeError: Need authentication

        Returns:
            Tuple[int, str] -- Episode ID, Episode tracking code
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        etc = self.__selected_episode_tracking_code
        if not (etc in self.episode_tracking_code):
            raise RuntimeError(self.__err_episode_not_found)
        episode_id = self.episode_tracking_code[etc]
        return episode_id, etc

    def get_default_image_name(
            self,
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
        _, _, show_tracking_code = self.get_selected_show()
        _, _, seq_tracking_code = self.get_selected_sequence()
        return '{0}_{1}_v{2}_{3}_{4}_v{5}'.format(
            show_tracking_code,
            seq_tracking_code,
            seq_rev_number,
            panel_pos,
            panel_id,
            panel_revision)

    def local_download(self, base_path: str, mo: dict, seq_rev_nbr: int):
        """local_download will download a media object locally

        Raises:
            RuntimeError: Need authentication

        Arguments:
            base_path {str} -- Path to download the file

            mo {Dict} -- Media object entity

            seq_rev_nbr {int} -- Sequence revision number
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        ext = os.path.splitext(mo.get('name'))
        filename = self.get_default_image_name(
            seq_rev_nbr, mo.get('pos'),
            mo.get('id'),
            mo.get('revision_number'))
        file_path = os.path.join(
            base_path, '{0}{1}'.format(filename, ext[1]))
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            file_path = file_path.replace('\\', '\\\\')
        self.get_flix_api().download_media_object(
            file_path, mo.get('mo'))
        return file_path

    def get_panels_with_thumbs(self, fn_progress: Callable[[str], None]):
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)
        show_id, episodic, _ = self.get_selected_show()
        seq_id, _, _ = self.get_selected_sequence()
        seq_rev = self.get_selected_sequence_rev()
        seq_rev_number = seq_rev.get('revision')
        fn_progress('get sequence revision')

        fn_progress('get panels')
        panels = self.get_flix_api().get_panels(
            show_id, seq_id, seq_rev_number)
        if panels is None:
            self.__error('Could not retrieve panels')
            return None
        dialogues = self.get_dialogues_by_panel_id()
        # Format panels
        formatted_panels = []
        pos = 1

        for p in panels:
            # Fetch the full asset from the ID.
            asset = self.get_flix_api().get_asset(p.get('asset', {}).get('asset_id', 0))

            mos = asset.get('media_objects', {})
            thumbs = mos.get('thumbnail', [])
            if len(thumbs) > 0:
                mo = thumbs[0]
                formatted_panels.append({
                    'mo': {
                        'name': mo.get('name'),
                        'id': p.get('panel_id'),
                        'revision_number': p.get('revision_number'),
                        'pos': pos,
                        'mo': mo.get('id')
                    },
                    'id': p.get('panel_id'),
                    'rev': p.get('revision_number'),
                    'published': p.get('published'),
                    'dialogue': dialogues.get(p.get('panel_id', 0), '')
                })
            pos += 1

        return formatted_panels

    def get_dialogues_by_panel_id(self):
        """get_dialogues_by_panel_id will get the dialogues to have
        a mapping panel_id -> dialogue

        Returns:
            Dict -- Mapping panel_id to dialogue
        """
        seq_id, seq_rev_number, _ = self.get_selected_sequence()
        show_id, _, _ = self.get_selected_show()
        dialogues = self.get_flix_api().get_dialogues(
            show_id, seq_id, seq_rev_number)

        mapped_dialogues = {}
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        for d in dialogues:
            t = d.get('text', '').replace('</p>', '\n')
            mapped_dialogues[d.get('panel_id')] = re.sub(cleanr, '', t)
        return mapped_dialogues

    def get_media_object_per_shots(self, fn_progress: Callable[[str], None]):
        """get_media_object_per_shots will get the media objects per shotss

        Raises:
            RuntimeError: Need authentication

        Arguments:
            Callable[[str], None] -- fn_progress is a progress function

        Returns:
            Dict -- Mapping of media objects per shots
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        show_id, episodic, _ = self.get_selected_show()
        seq_id, seq_rev_number, _ = self.get_selected_sequence()
        flix_api = self.get_flix_api()
        fn_progress('get sequence revision')
        seq_rev = flix_api.get_sequence_rev(show_id, seq_id, seq_rev_number)
        episode_id = None
        if episodic:
            episode_id, _ = self.get_selected_episode()
        if seq_rev is None:
            self.__error('Could not retrieve sequence revision')
            return None
        fn_progress('get markers')
        markers = self.get_flix_api().get_markers(seq_rev)
        if len(markers) < 1:
            self.__info('You need at least one shot')
            return None
        fn_progress('get panels')
        panels = self.get_flix_api().get_panels(
            show_id, seq_id, seq_rev_number)
        if panels is None:
            self.__error('Could not retrieve panels')
            return None
        fn_progress('get markers per panels')
        p_per_markers = self.get_flix_api().get_markers_per_panels(markers,
                                                                   panels)
        mo_per_shots, ok = self.get_flix_api().mo_per_shots(p_per_markers,
                                                            show_id,
                                                            seq_id,
                                                            seq_rev_number,
                                                            episode_id)

        # Split export quicktime
        for shot_name in mo_per_shots:
            def on_retry(r): return fn_progress(
                'export quicktime for shot {0}{1}'.format(
                    shot_name, '.' * (r % 4)))
            fn_progress('export quicktime for shot {0}'.format(shot_name))
            mo = self.get_flix_api().get_mo_quicktime_export(
                shot_name, p_per_markers[shot_name],
                show_id, seq_id, seq_rev_number, episode_id, on_retry)
            mo_per_shots[shot_name]['mov'] = mo

        if mo_per_shots is None:
            self.__error('Could not retrieve media objects per shots')
            return None
        if ok is False:
            return None
        return mo_per_shots

    def get_selected_sequence(self) -> Tuple[int, int, str]:
        """get_selected_sequence will return the selected sequence info

        Raises:
            RuntimeError: Sequence not found
            RuntimeError: Need authentication

        Returns:
            Tuple[int, int, str] -- Sequence ID, Seq rev ID, Seq tracking code
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        stc = self.__selected_sequence_tracking_code
        if not (stc in self.sequence_tracking_code):
            raise RuntimeError(self.__err_sequence_not_found)
        seq_id = self.sequence_tracking_code[stc][0]
        seq_rev = self.sequence_tracking_code[stc][1]
        return seq_id, seq_rev, stc

    def get_selected_sequence_rev(self) -> Dict:
        """get_selected_sequence_rev will return the selected
        sequence revision info

        Raises:
            RuntimeError: Sequence not found
            RuntimeError: Need authentication

        Returns:
            Tuple[int, int, str] -- Sequence ID, Seq rev ID, Seq tracking code
        """
        if not self.authenticated:
            raise RuntimeError(self.__err_authenticate)

        stc = self.__selected_sequence_rev_tracking_code
        if not (stc in self.seq_revisions_rev):
            raise RuntimeError(self.__err_sequence_rev_not_found)
        seq_rev = self.seq_revisions_rev[stc]
        return seq_rev

    def __create_line_label(self,
                            name: str,
                            label: str,
                            min_width: int = 200,
                            echo_mode: bool = False) -> Tuple[Dict,
                                                              Dict]:
        """__create_line_label will create a line edit button and his label

        Arguments:
            name {str} -- Default value

            label {str} -- Label name

            min_width {int} -- Minium width (default: {200})

            echo_mode {bool} -- Stars for password (default: {False})

        Returns:
            Tuple[Dict, Dict] -- Line Edit, Label
        """
        line_edit = QLineEdit(name)
        line_edit.setMinimumWidth(min_width)
        if echo_mode:
            line_edit.setEchoMode(QLineEdit.Password)
        label = QLabel(label)
        label.setBuddy(line_edit)
        return line_edit, label

    def __create_combo_label(
            self, label: str, fn_text_changed: object) -> Tuple[Dict, Dict]:
        """__create_combo_label will create a combo box and his label

        Arguments:
            label {str} -- Label name

            fn_text_changed {object} -- Callback function for text_changed

        Returns:
            Tuple[Dict, Dict] -- ComboBox, Label
        """
        combo = QComboBox()
        label = QLabel(label)
        label.setMinimumWidth(300)
        label.setBuddy(combo)
        combo.currentTextChanged.connect(fn_text_changed)
        return combo, label

    def __add_widget_to_layout(self, layout: Dict, *widgets: Dict):
        """__add_widget_to_layout will add all the widget to a layout
        __add_widget_to_layout(layout, widget1, widget2, widget3)

        Arguments:
            layout {Dict} -- Layout to add widget to

            widgets {*Dict} -- All the widgets to add
        """

        for w in widgets:
            layout.addWidget(w)

    def __authenticate(self):
        """__authenticate will authenticate a user and update the view
        """
        if self.authenticated:
            self.flix_api.reset()
            self.e_logout.emit()
            self.__reset('Log In')
            self.authenticated = False
            return

        credentials = self.flix_api.authenticate(self.hostname.text(),
                                                 self.login.text(),
                                                 self.password.text())
        if credentials is None:
            self.__error('Could not authenticate user')
            self.login.clear()
            self.password.clear()
            return
        self.e_login.emit(credentials)
        self.authenticated = True
        self.__init_shows()
        self.__reset('Log Out')

    def __reset(self, action: str = 'Log Out'):
        """__reset will reset the login form / shows info for login / logout

        Arguments:
            action {str} -- action to handle (default: {'Log Out'})
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
        self.sequence_rev_list.clear()
        self.episode_list.clear()
        self.submit.setText(action)

    def __on_show_changed(self, tracking_code: str):
        """__on_show_changed triggered after a show is selected,
        will init the list of sequences from this show

        Arguments:
            tracking_code {str} -- show_tracking_code from the event
        """
        if tracking_code == '':
            return
        self.__selected_show_tracking_code = tracking_code
        show_id, episodic, _ = self.get_selected_show()
        self.e_show_changed.emit(show_id, tracking_code, episodic)

        self.sequence_list.clear()
        self.sequence_rev_list.clear()
        self.episode_list.clear()
        # If the show is episodic we show the episode list and update his list
        if episodic is True:
            self.episode_list.show()
            self.episode_label.show()
            episodes = self.flix_api.get_episodes(show_id)
            if episodes is None:
                self.__error('Could not retrieve episodes')
                return
            self.episode_tracking_code = self.__get_episode_tracking_code(
                episodes)
            for e in self.episode_tracking_code:
                self.episode_list.addItem(e)
            self.episode_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            return
        # If not episodic we hide the episode list and update the sequence list
        self.episode_list.hide()
        self.episode_label.hide()
        sequences = self.flix_api.get_sequences(show_id)
        if sequences is None:
            self.__error('Could not retreive sequences')
            return
        self.sequence_tracking_code = self.__get_sequence_tracking_code(
            sequences)
        for s in self.sequence_tracking_code:
            self.sequence_list.addItem(s)
        self.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def __on_episode_changed(self, tracking_code: str):
        """__on_episode_changed triggered after an episode is selected,
        will store the selected episode

        Arguments:
            tracking_code {str} -- episode_tracking_code from the event
        """
        if tracking_code == '':
            return
        self.__selected_episode_tracking_code = tracking_code
        show_id, _, _ = self.get_selected_show()
        episode_id, _ = self.get_selected_episode()
        self.e_episode_changed.emit(episode_id, tracking_code)
        sequences = self.flix_api.get_sequences(show_id, episode_id)
        if sequences is None:
            self.__error('Could not retreive sequences')
            return
        self.sequence_tracking_code = self.__get_sequence_tracking_code(
            sequences)
        self.sequence_list.clear()
        for s in self.sequence_tracking_code:
            self.sequence_list.addItem(s)
        self.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def __on_sequence_changed(self, tracking_code: str):
        """__on_sequence_changed triggered after a sequence is selected,
        will store the selected sequence

        Arguments:
            tracking_code {str} -- sequence_tracking_code from the event
        """
        if tracking_code == '':
            return
        self.__selected_sequence_tracking_code = tracking_code
        episode_id = None
        show_id, episodic, _ = self.get_selected_show()
        if episodic:
            episode_id, _ = self.get_selected_episode()
        seq_id, seq_rev, _ = self.get_selected_sequence()
        self.e_sequence_changed.emit(seq_id, seq_rev, tracking_code)

        seq_revisions = self.flix_api.get_sequence_revisions(show_id, seq_id,
                                                             episode_id)
        if seq_revisions is None:
            self.__error('Could not retreive sequence revisions')
            return

        self.seq_revisions_rev = self.__get_sequence_rev_id(seq_revisions)
        self.sequence_rev_list.clear()
        for s in self.seq_revisions_rev:
            self.sequence_rev_list.addItem(s)
        self.sequence_rev_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def __on_sequence_rev_changed(self, tracking_code: str):
        """__on_sequence_rev_changed triggered after a sequence
        revision is selected, will store the selected sequence revision

        Arguments:
            tracking_code {str} -- sequence_rev_tracking_code from the event
        """
        if tracking_code == '':
            return
        self.__selected_sequence_rev_tracking_code = tracking_code
        seq_rev = self.get_selected_sequence_rev()
        self.e_sequence_rev_changed.emit(seq_rev)

    def __init_shows(self):
        """__init_shows will retrieve the list of show and update the UI
        """
        shows = self.flix_api.get_shows()
        if shows is None:
            self.__error('Could not retreive shows')
            return
        self.show_tracking_code = self.__get_show_tracking_code(shows)
        self.show_list.clear()
        for s in self.show_tracking_code:
            self.show_list.addItem(s)
        self.show_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def __sort_alphanumeric(self, d: Dict, reverse: bool = False) -> Dict:
        """__sort_alphanumeric will sort a dictionnary alphanumerically by keys

        Arguments:
            d {Dict} -- Dictionnary to sort

        Returns:
            Dict -- Sorted Dictionnary
        """
        def convert(text): return int(text) if text.isdigit() else text

        def alphanum_key(key): return [convert(c)
                                       for c in re.split('([0-9]+)', key)]
        keys = sorted(d.keys(), key=alphanum_key, reverse=reverse)
        return OrderedDict((k, d[k]) for k in keys)

    def __get_show_tracking_code(self, shows: List) -> Dict:
        """__get_show_tracking_code will format the shows to have a mapping:
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
        return self.__sort_alphanumeric(show_tracking_codes)

    def __get_sequence_tracking_code(self, sequences: List) -> Dict:
        """__get_sequence_tracking_code will format the sequences to have
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
        return self.__sort_alphanumeric(sequence_tracking_codes)

    def __get_sequence_rev_id(self, seq_revs: List) -> Dict:
        """__get_sequence_rev_id will format the sequences to have
        a mapping: id -> seq_rev

        Arguments:
            sequences {List} -- List of sequence revisions

        Returns:
            Dict -- sequence revisions
        """
        sequence_rev_ids = {}
        if seq_revs is None:
            return sequence_rev_ids
        for s in seq_revs:
            if not s.get('deleted', False):
                name = "{0} - {1}".format(s.get('revision'), s.get('comment'))
                sequence_rev_ids[name] = s
        return self.__sort_alphanumeric(sequence_rev_ids, True)

    def __get_episode_tracking_code(self, episodes: List) -> Dict:
        """__get_episode_tracking_code will format the episodes to have a
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
        return self.__sort_alphanumeric(episode_tracking_codes)

    def __error(self, message: str):
        """__error will show a error message with a given message

        Arguments:
            message {str} -- Message to show
        """
        err = QErrorMessage(self.parent())
        err.setWindowTitle('Flix')
        err.showMessage(message)
        err.exec_()


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.setWindowTitle('Flix Production Handoff')

        main_layout = QVBoxLayout()
        widget_flix_ui = flix_ui()
        # Bind event from flix
        widget_flix_ui.e_login.connect(self.on_login)
        widget_flix_ui.e_logout.connect(self.on_logout)
        widget_flix_ui.e_show_changed.connect(self.on_show_changed)
        widget_flix_ui.e_episode_changed.connect(self.on_episode_changed)
        widget_flix_ui.e_sequence_changed.connect(self.on_sequence_changed)
        widget_flix_ui.e_sequence_rev_changed.connect(self.on_seq_rev_changed)

        # Add flix Ui widget
        main_layout.addWidget(widget_flix_ui)
        self.setLayout(main_layout)

    def on_login(self, credentials):
        print('logged in', credentials)

    def on_logout(self):
        print('logged out')

    def on_show_changed(self, show_id, tracking_code, episodic):
        print('show selected', show_id, tracking_code, episodic)

    def on_episode_changed(self, episode_id, tracking_code):
        print('episode selected', episode_id, tracking_code)

    def on_sequence_changed(self, sequence_id, seq_rev, tracking_code):
        print('sequence selected', sequence_id, seq_rev, tracking_code)

    def on_seq_rev_changed(self, seq_rev):
        print('sequence revision selected', seq_rev)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
