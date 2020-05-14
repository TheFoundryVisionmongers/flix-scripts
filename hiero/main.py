import json
import os
import re
import sys
import tempfile
import uuid
from collections import OrderedDict

from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QStackedWidget,
                               QVBoxLayout)

import flix as flix_api
import hiero_c as hiero_api


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.flix_api = flix_api.flix()
        self.hiero_api = hiero_api.hiero_c()
        self.authenticated = False
        self.setWindowTitle("Flix")

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
        h_action = QHBoxLayout()
        pull = QPushButton("Pull Latest")
        pull.clicked.connect(self.pull_latest)
        update = QPushButton("Update in Flix")
        update.clicked.connect(self.update_in_flix)
        h_action.addWidget(pull)
        h_action.addWidget(update)
        v_sequence_box.addWidget(show_label)
        v_sequence_box.addWidget(self.show_list)
        v_sequence_box.addWidget(self.episode_label)
        v_sequence_box.addWidget(self.episode_list)
        v_sequence_box.addWidget(sequence_label)
        v_sequence_box.addWidget(self.sequence_list)
        v_sequence_box.addLayout(h_action)

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

        credentials = self.flix_api.authenticate(
            self.hostname.text(),
            self.login.text(),
            self.password.text())
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
        def convert(text): return int(text) if text.isdigit() else text
        def alphanum_key(key): return [convert(c)
                                       for c in re.split('([0-9]+)', key)]
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
                show_tracking_codes[s.get('tracking_code')] = [
                    s.get('id'), s.get('episodic')]
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
                sequence_tracking_codes[s.get('tracking_code')] = [
                    s.get('id'), s.get('revisions_count')]
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
            self.episode_tracking_code = self.get_episode_tracking_code(
                episodes)
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
            self.sequence_tracking_code = self.get_sequence_tracking_code(
                sequences)
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
        self.sequence_tracking_code = self.get_sequence_tracking_code(
            sequences)
        self.sequence_list.clear()
        for s in self.sequence_tracking_code:
            self.sequence_list.addItem(s)
        self.sequence_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def on_sequence_changed(self, tracking_code):
        """on_sequence_changed triggered after a sequence is selected, will store the selected sequence
        tracking_code: sequence_tracking_code from the event
        """
        self.selected_sequence_tracking_code = tracking_code

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
        self.sequence_tracking_code = self.get_sequence_tracking_code(
            sequences)

    def create_clip(self, seq_rev, p, clip_name, clips):
        """create_clip will create a clip and download image or reuse one
        seq_rev: sequence bin
        p: panel entity
        clip_name: name of the clip
        clips: list of all clips
        """
        if clip_name not in clips:
            temp_path = tempfile.mkdtemp()
            thumb_mo = p.get(
                'asset', {}).get(
                'media_objects', {}).get(
                'thumbnail', [])
            thumb_mo_id = None if len(thumb_mo) < 1 else thumb_mo[0].get('id')
            if thumb_mo_id is None:
                self.error('Could not retrieve thumbnail ID')
                return None
            temp_filepath = os.path.join(
                temp_path,
                '{0}_{1}_{2}_.png'.format(
                    self.selected_sequence_tracking_code,
                    p.get('panel_id'),
                    p.get('revision_counter')))
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                temp_filepath = temp_filepath.replace('\\', '\\\\')
            if self.flix_api.download_media_object(
                    temp_filepath, thumb_mo_id) is None:
                self.error('Could not download thumbnail')
                return None
            return seq_rev.createClip(temp_filepath)
        return clips[clip_name]

    def get_comment_tag(self, p):
        """get_comment_tag will make a copy of a comment tag and set his comment as a note
        p: panel entity
        """
        comment = p.get('latest_open_note', {}).get('body', None)
        t = None
        if comment is not None:
            t = self.hiero_api.create_comment_tag(comment)
        return t

    def add_dialogue(self, mapped_dialogue, panel_id, track, prev):
        """add_dialogue will create a dialogue and add it to the track
        mapped_dialogue: mapping of dialogue to ensure there is a dialogue for the panel
        panel_id: panel ID
        track: track to add the dialogue
        prev: previous trackitem
        """
        if panel_id in mapped_dialogue:
            settings = {
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
            self.hiero_api.add_dialogue_track_effect(track, prev, settings)

    def create_burnin(self, track, fr, to, burnin_name):
        """create_burnin will create a burnin and add it to the track
        track: track to add the burnin
        fr: from where to start the burnin (frame)
        to: from where to end the burnin (frame)
        burnin_name: name of the burnin
        """
        settings = {
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
        self.hiero_api.add_burnin_track_effect(track, fr, to, settings)

    def get_markers(self, sequence_revision):
        """get_markers will format the sequence_revision to have a mapping of markers: start -> marker_name
        sequences_revision: sequence revision entity
        """
        markers_mapping = {}
        markers = sequence_revision.get('meta_data', {}).get('markers', [])
        for m in markers:
            markers_mapping[m.get('start')] = m.get('name')
        return OrderedDict(sorted(markers_mapping.items()))

    def add_burnin(
            self,
            panels,
            panel_in,
            markers_mapping,
            marker_tmp,
            marker_in,
            shots,
            p,
            i):
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
                self.create_burnin(
                    shots,
                    marker_in,
                    panel_in - 1,
                    markers_mapping[panel_in])
            marker_in = panel_in
        if len(panels) - 1 == i and marker_in is not None:
            self.create_burnin(
                shots,
                marker_in,
                panel_in +
                p.get('duration') -
                1,
                marker_tmp)
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
        t = self.hiero_api.create_info_tag(json.dumps(p))
        tags.append(t)
        return tags

    def add_marker(self, markers_mapping, panel_in, sequence):
        """add_marker will add a marker in the sequence
        markers_mapping: mapping of markers
        panel_in: first frame of the panel(from the whole sequence)
        sequence: sequence to add to
        """
        if panel_in in markers_mapping:
            tag = self.hiero_api.create_marker_tag(
                    panel_in,
                    markers_mapping[panel_in])
            sequence.addTagToRange(tag, panel_in, panel_in + 1)

    def create_video_track(
            self,
            sequence,
            seq_bin,
            seq_rev_bin,
            seq_id,
            seq_rev_number):
        """create_video_track will create 2 videos tracks, one for the sequence and one for shots
        sequence: sequence
        seq_bin: sequence bin
        seq_rev: sequence revision bin
        seq_id: sequence ID
        seq_rev_number: sequence revision count
        """
        track = self.hiero_api.create_video_track(
            'Flix_{0}_v{1}'.format(
                self.selected_sequence_tracking_code,
                seq_rev_number))
        show_id = self.show_tracking_code[self.selected_show_tracking_code][0]
        dialogues = self.flix_api.get_dialogues(
            show_id, seq_id, seq_rev_number)
        mapped_dialogue = self.get_dialogues_by_panel_id(dialogues)
        sequence_revision = self.flix_api.get_sequence_rev(
            show_id, seq_id, seq_rev_number)
        if sequence_revision is None:
            self.error('Could not retreive sequence revision')
            return
        markers_mapping = self.get_markers(sequence_revision)
        shots = self.hiero_api.create_video_track('Shots') if len(markers_mapping) > 0 else None
        clips = self.hiero_api.get_clips(seq_bin)
        panels = self.flix_api.get_panels(show_id, seq_id, seq_rev_number)
        if panels is None:
            self.error('Could not retreive panels')
            return
        prev = None
        panel_in = 0
        marker_in = None
        prev_marker_name = None

        for i, p in enumerate(panels):
            tags = []
            panel_id = p.get('panel_id')
            clip_name = '{0}_{1}_{2}_'.format(
                self.selected_sequence_tracking_code, panel_id, p.get(
                    'revision_counter'))
            clip = self.create_clip(seq_rev_bin, p, clip_name, clips)
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
            prev = self.hiero_api.add_track_item(
                track, clip_name, clip, p.get('duration'), tags, prev)
            # Add dialogue
            self.add_dialogue(mapped_dialogue, panel_id, track, prev)
            # Add burnin
            marker_in = self.add_burnin(
                panels,
                panel_in,
                markers_mapping,
                prev_marker_name,
                marker_in,
                shots,
                p,
                i)

            if panel_in in markers_mapping:
                prev_marker_name = markers_mapping[panel_in]
            panel_in = panel_in + p.get('duration')
        return track, shots

    def pull_latest_seq_rev(self):
        # Update sequence mapping to have the last seq rev info
        self.update_sequence_items()

        seq_id = self.sequence_tracking_code[self.selected_sequence_tracking_code][0]
        seq_rev_number = self.sequence_tracking_code[self.selected_sequence_tracking_code][1]

        my_project = self.hiero_api.get_project(
            'Flix_{0}'.format(
                self.selected_show_tracking_code))
        seq, seq_bin_reused = self.hiero_api.get_project_bin(
            my_project, 'Flix_{0}'.format(
                self.selected_sequence_tracking_code))
        if seq_bin_reused is False:
            clipsBin = my_project.clipsBin()
            clipsBin.addItem(seq)

        seq_rev_bin, seq_rev_bin_reused = self.hiero_api.get_seq_bin(
            seq, 'v{0}'.format(seq_rev_number))
        if seq_rev_bin_reused is False:
            seq.addItem(seq_rev_bin)

        sequence = self.hiero_api.create_sequence(
            'Flix_{0}_v{1}'.format(
                self.selected_sequence_tracking_code,
                seq_rev_number))
        seq_item = self.hiero_api.sequence_to_bin_item(sequence)
        seq_rev_bin.addItem(seq_item)
        track, shots = self.create_video_track(
            sequence, seq, seq_rev_bin, seq_id, seq_rev_number)
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
                self.selected_sequence_tracking_code = self.sequence_list.itemText(
                    count)
                self.pull_latest_seq_rev()
            self.selected_sequence_tracking_code = 'All Sequences'
        else:
            self.pull_latest_seq_rev()

        self.info('Sequence revision imported successfully')

    def get_panels_from_sequence(self, sequence, show_id, sequence_id):
        """get_panels_from_sequence will retrieve all the clips and format them as panels from a hiero sequence
        sequence: Video track sequence
        show_id: show ID
        sequence_id: sequence ID
        """
        panels = []
        for track_item in sequence.items():
            panel_info = None
            tags_note = self.hiero_api.get_item_tags_note(track_item, 'France')
            if len(tags_note) > 0:
                panel_info = tags_note[0]
            if panel_info is None:
                blank_panel = self.flix_api.new_panel(show_id, sequence_id)
                blank_panel['panel_id'] = blank_panel.get('id')
                blank_panel['revision_number'] = 1
                panels.append(json.dumps(blank_panel))
            else:
                panels.append(panel_info)
        return panels

    def update_panel_from_sequence(self, sequence, panels):
        """update_panel_from_sequence will update panels depending on hiero sequence
        sequence: Video track sequence
        """
        for i, track_item in enumerate(sequence.items()):
            panel = json.loads(panels[i])
            panel['duration'] = int(track_item.duration())
            panels[i] = panel
        return panels

    def format_panel_for_revision(self, panels):
        """format_panel_for_revision will format the panels as revisioned panels
        panels: list of panels
        """
        revisioned_panels = []
        for p in panels:
            revisioned_panels.append({
                'dialogue': p.get('dialogue'),
                'duration': p.get('duration'),
                'id': p.get('panel_id'),
                'revision_number': p.get('revision_number')
            })
        return revisioned_panels

    def get_markers_from_sequence(self, sequence):
        """get_markers_from_sequence will retrieve all the markers from a sequence
        sequence: Video track shots
        """
        markers = []
        for mrks in sequence.subTrackItems():
            for marker in mrks:
                name = marker.name()
                if len(name) > 36:
                    name = name[:-39]
                markers.append({
                    'name': name,
                    'start': marker.timelineIn()
                })
        return markers

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

    def duplicate_panel(self, show_id, sequence_id, p):
        """duplicate_panel wil duplicate a panel and reuse his asset
        p: panel to duplicate
        """
        new_panel = self.flix_api.new_panel(
            show_id, sequence_id, p['asset']['asset_id'], p['duration'])
        new_panel['panel_id'] = new_panel.get('id')
        new_panel['revision_number'] = 1
        new_panel['duration'] = p['duration']
        return new_panel

    def handle_duplicate_panels(self, panels, show_id, seq_id):
        """handle_duplicate_panels will handle duplicate panels and create new ones
        panels: list of panels to update
        show_id: show ID
        seq_id: sequence ID
        """
        uniq_p = {}
        for i, p in enumerate(panels):
            uid = '{0}-{1}'.format(p.get('panel_id'), p.get('revision_number'))
            if uid in uniq_p:
                panels[i] = self.duplicate_panel(show_id, seq_id, p)
                continue
            uniq_p[uid] = True
        return panels

    def update_in_flix(self):
        """update_in_flix will send a sequence to Flix"""
        show_id = self.show_tracking_code[self.selected_show_tracking_code][0]
        seq_id = self.sequence_tracking_code[self.selected_sequence_tracking_code][0]
        revisioned_panels = []
        markers = []

        sequence = self.hiero_api.get_active_sequence()
        if sequence is None:
            self.error('could not find any sequence selected')
            return
        for tr in sequence.items():
            if tr.name() == 'Shots':
                markers = self.get_markers_from_sequence(tr)
            else:
                panels = self.get_panels_from_sequence(tr, show_id, seq_id)
                panels = self.update_panel_from_sequence(tr, panels)
                panels = self.handle_duplicate_panels(panels, show_id, seq_id)
                if len(panels) > 0 and len(revisioned_panels) < 1:
                    revisioned_panels = self.format_panel_for_revision(panels)

        if len(revisioned_panels) < 1:
            self.error(
                'could not create a sequence revision, need at least one clip')
            return

        comment, ok = QInputDialog.getText(
            self, 'Update to Flix', 'Sequence revision comment:')
        if ok is False:
            return

        new_seq_rev = self.flix_api.new_sequence_revision(
            show_id, seq_id, revisioned_panels, markers, comment)
        if new_seq_rev is None:
            self.error('Could not save sequence revision')
        else:
            self.info('Sequence revision successfully created')


main_view = main_dialogue()
wm = hiero_api.hiero_c()
wm = wm.new_window_manager()
wm.addWindow(main_view)
