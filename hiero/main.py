import os
import re
import sys
from collections import OrderedDict

from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QStackedWidget,
                               QVBoxLayout)

import flix_ui as flix_widget
import hiero_c as hiero_api
import hiero_ui as hiero_widget


class main_dialogue(QDialog):

    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.setWindowTitle('Flix')
        self.wg_flix_ui = flix_widget.flix_ui()
        self.wg_hiero_ui = hiero_widget.hiero_ui()

        self.wg_hiero_ui.e_update_in_flix.connect(self.on_update_in_flix)
        self.wg_hiero_ui.e_pull_latest.connect(self.on_pull_latest)

        # Setup UI view
        v_main_box = QVBoxLayout()
        v_main_box.addWidget(self.wg_flix_ui)
        v_main_box.addWidget(self.wg_hiero_ui)
        self.setLayout(v_main_box)

    def error(self, message):
        """error will show a error message with a given message

        Arguments:
            message {str} -- Message to show
        """
        err = QErrorMessage(self.parent())
        err.setWindowTitle('Flix')
        err.showMessage(message)
        err.exec_()

    def info(self, message):
        """info will show a message with a given message

        Arguments:
            message {str} -- Message to show
        """
        msgbox = QMessageBox(self.parent())
        msgbox.setWindowTitle('Flix')
        msgbox.setText(message)
        msgbox.exec_()

    def create_clip(self, seq_rev, p, clip_name, clips):
        """create_clip will create a clip or reuse one and download image

        Arguments:
            seq_rev {Dict} -- Sequence bin

            p {Dict} -- Panel entity

            clip_name {st} -- Name of the clip

            clips {List} -- List of all clips

        Returns:
            Dict -- Clip created / reused
        """
        if clip_name not in clips:
            temp_filepath = self.wg_flix_ui.download_first_thumb(p)
            if temp_filepath is None:
                return
            return seq_rev.createClip(temp_filepath)
        return clips[clip_name]

    def create_video_track(
            self,
            sequence,
            seq_bin,
            seq_rev_bin,
            seq_id,
            seq_rev_number):
        """create_video_track will create 2 videos tracks, one for the
        sequence and one for shots

        Arguments:
            sequence {Dict} -- Hiero Sequence

            seq_bin {Dict} -- Sequence Bin

            seq_rev_bin {Dict} -- Sequence revision Bin

            seq_id {int} -- Sequence ID

            seq_rev_number {int} -- Sequence revision number

        Returns:
            Tuple[Dict, Dict] -- VideoTrack, ShotTrack
        """
        _, seq_rev_nbr, seq_tc = self.wg_flix_ui.get_selected_sequence()
        mapped_dialogue = self.wg_flix_ui.get_dialogues_by_panel_id()
        markers_mapping = self.wg_flix_ui.get_markers_by_name()
        panels = self.wg_flix_ui.get_panels()
        if panels is None:
            self.error('Could not retreive panels')
            return

        vt_track_name = 'Flix_{0}_v{1}'.format(
            seq_tc, seq_rev_nbr)
        vt_shot_name = 'Shots' if len(markers_mapping) > 0 else None
        track, shots = self.wg_hiero_ui.create_video_tracks(vt_track_name,
                                                            vt_shot_name)
        clips = self.wg_hiero_ui.hiero_api.get_clips(seq_bin)

        prev = None
        panel_in = 0
        marker_in = None
        prev_marker_name = None
        for i, p in enumerate(panels):
            tags = []
            panel_id = p.get('panel_id')
            clip_name = '{0}_{1}_{2}_'.format(
                seq_tc, panel_id, p.get(
                    'revision_counter'))
            clip = self.create_clip(seq_rev_bin, p, clip_name, clips)
            if clip is None:
                self.error('could not create clip: {0}'.format(clip_name))
                return track, shots

            # Add comment
            tags = self.wg_hiero_ui.add_comment(p, tags)
            # Add panel info
            tags = self.wg_hiero_ui.add_panel_info_tag(p, tags)
            # Add marker
            self.wg_hiero_ui.add_marker(markers_mapping, panel_in, sequence)
            # Add track item
            prev = self.wg_hiero_ui.hiero_api.add_track_item(
                track, clip_name, clip, p.get('duration'), tags, prev)
            # Add dialogue
            self.wg_hiero_ui.add_dialogue(mapped_dialogue, panel_id, track, prev)
            # Add burnin
            marker_in = self.wg_hiero_ui.add_burnin(
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
        """pull_taltest_seq_rev will pull one latest sequence revision and send
        it to hiero
        """
        _, _, show_tc = self.wg_flix_ui.get_selected_show()
        seq_id, seq_rev_tc, seq_tc = self.wg_flix_ui.get_selected_sequence()
        sequence, seq, seq_rev_bin = self.wg_hiero_ui.pull_to_sequence(show_tc,
                                                                       seq_rev_tc,
                                                                       seq_tc)
        track, shots = self.create_video_track(
            sequence, seq, seq_rev_bin, seq_id, seq_rev_tc)
        if track is None:
            return
        sequence.addTrack(track)
        if shots is not None:
            sequence.addTrack(shots)

    def on_pull_latest(self):
        """on_pull_latest will retrieve the last sequence revision from Flix and
        will create / reuse bins, sequences, clips
        Depending on the selection it will pull only one or all of them
        """
        _, _, selected_seq_tc = self.wg_flix_ui.get_selected_sequence()
        if selected_seq_tc == 'All Sequences':
            for count in range(self.wg_flix_ui.sequence_list.count()):
                if self.wg_flix_ui.sequence_list.itemText(count) == 'All Sequences':
                    continue
                select_seq_tracking_code = self.wg_flix_ui.sequence_list.itemText(
                    count)
                self.wg_flix_ui.on_sequence_changed(select_seq_tracking_code)
                self.pull_latest_seq_rev()
            self.wg_flix_ui.on_sequence_changed('All Sequences')
        else:
            self.pull_latest_seq_rev()

        self.info('Sequence revision imported successfully')

    def on_update_in_flix(self):
        """on_update_in_flix will send a sequence to Flix
        """
        show_id, _, _ = self.wg_flix_ui.get_selected_show()
        seq_id, _, _ = self.wg_flix_ui.get_selected_sequence()
        revisioned_panels = []
        markers = []

        sequence = self.wg_hiero_ui.hiero_api.get_active_sequence()
        if sequence is None:
            self.error('could not find any sequence selected')
            return
        for tr in sequence.items():
            if tr.name() == 'Shots':
                markers = self.wg_hiero_ui.get_markers_from_sequence(tr)
            else:
                panels = self.wg_hiero_ui.get_panels_from_sequence(tr,
                                                       show_id,
                                                       seq_id,
                                                       self.wg_flix_ui.create_blank_panel)
                panels = self.wg_hiero_ui.update_panel_from_sequence(tr, panels)
                panels = self.wg_flix_ui.handle_duplicate_panels(panels)
                if len(panels) > 0 and len(revisioned_panels) < 1:
                    revisioned_panels = self.wg_flix_ui.get_flix_api().format_panel_for_revision(panels)

        if len(revisioned_panels) < 1:
            self.error(
                'could not create a sequence revision, need at least one clip')
            return

        comment, ok = QInputDialog.getText(
            self, 'Update to Flix', 'Sequence revision comment:')
        if ok is False:
            return

        new_seq_rev = self.wg_flix_ui.get_flix_api().new_sequence_revision(
            show_id, seq_id, revisioned_panels, markers, comment)
        if new_seq_rev is None:
            self.error('Could not save sequence revision')
        else:
            self.info('Sequence revision successfully created')


main_view = main_dialogue()
wm = hiero_api.hiero_c()
wm = wm.get_window_manager()
wm.addWindow(main_view)
