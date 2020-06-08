#
# Copyright (C) Foundry 2020
#

import json
import sys
import uuid

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (QApplication, QHBoxLayout, QPushButton,
                               QSizePolicy, QWidget)

import hiero_c as hiero_api


class hiero_ui(QWidget):

    e_pull_latest = Signal()
    e_update_in_flix = Signal()

    def __init__(self, *args, **kwargs):
        super(hiero_ui, self).__init__(*args, **kwargs)
        self.hiero_api = hiero_api.hiero_c()
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        h_action = QHBoxLayout()
        pull = QPushButton("Pull Latest")
        pull.clicked.connect(self.on_pull_latest)
        update = QPushButton("Update in Flix")
        update.clicked.connect(self.on_update_in_flix)
        h_action.addWidget(pull)
        h_action.addWidget(update)
        self.setLayout(h_action)

    def on_pull_latest(self):
        """on_pull_latest callback of the pull latest event
        """
        self.e_pull_latest.emit()

    def on_update_in_flix(self):
        """on_update_in_flix callback of the update in flix event
        """
        self.e_update_in_flix.emit()

    def create_video_tracks(self, video_name, shot_name=None):
        """create_video_tracks

        Arguments:
            video_name {str} -- Video track name for the sequence

            shot_name {str} -- Video track for the shots (default: {None})

        Returns:
            Tuple[Dict, Dict] -- Seq video track, Shot video track
        """
        track = self.hiero_api.create_video_track(video_name)
        if shot_name is None:
            shot = None
        else:
            shot = self.hiero_api.create_video_track('Shots')
        return track, shot

    def add_dialogue(self, mapped_dialogue, panel_id, track, prev):
        """add_dialogue will create a dialogue and add it to the track

        Arguments:
            mapped_dialogue {Dict} -- mapping of dialogue to ensure there is a
            dialogue for the panel

            panel_id {int} -- Panel ID

            track {dict} -- Track to add the dialogue

            prev {Dict} -- Previous trackitem
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

    def add_burnin(
            self,
            panels,
            panel_in,
            markers_map,
            current_marker,
            marker_in,
            shots,
            p,
            i):
        """add_burnin will add a burnin in a VideoTrack

        Arguments:
            panels {List} -- List of Panels

            panel_in {int} -- First frame of the panel (from whole timeline)

            markers_map {Dict} -- Mapping of markers

            current_marker {str} -- Current Marker

            marker_in {int} -- First frame of the marker to add as burnin

            shots {Dict} -- Video track to add the burnin

            p {Dict} -- Panel

            i {int} -- Posiion of the panel

        Returns:
            int -- Value of the panel marker in
        """
        if panel_in in markers_map and markers_map[panel_in] != current_marker:
            if marker_in is not None:
                self.create_burnin(
                    shots,
                    marker_in,
                    panel_in - 1,
                    markers_map[panel_in])
            marker_in = panel_in
        if len(panels) - 1 == i and marker_in is not None:
            self.create_burnin(
                shots,
                marker_in,
                panel_in +
                p.get('duration') -
                1,
                current_marker)
        return marker_in

    def get_panels_from_sequence(
            self,
            sequence,
            show_id,
            sequence_id,
            blank_panel):
        """get_panels_from_sequence will retrieve all the clips and format
        them as panels from a hiero sequence

        Arguments:
            sequence {Dict} -- Video Track Sequence

            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            blank_panel {Callable[[], None]} -- Callback to create blank panel

        Returns:
            List -- List of panels
        """
        panels = []
        for track_item in sequence.items():
            panel_info = None
            tags_note = self.hiero_api.get_item_tags_note(track_item, 'France')
            if len(tags_note) > 0:
                panel_info = tags_note[0]
            if panel_info is None:
                panels.append(json.dumps(blank_panel()))
            else:
                panels.append(panel_info)
        return panels

    def update_panel_from_sequence(self, sequence, panels):
        """update_panel_from_sequence will update panels depending
        on hiero sequence

        Arguments:
            sequence {Dict} -- Video Track Sequence

            panels {List} -- List of Panels

        Returns:
            List -- List of Panels
        """
        for i, track_item in enumerate(sequence.items()):
            panel = json.loads(panels[i])
            panel['duration'] = int(track_item.duration())
            panels[i] = panel
        return panels

    def get_markers_from_sequence(self, sequence):
        """get_markers_from_sequence will retrieve all the
        markers from a sequence

        Arguments:
            sequence {Dict} -- Video Track Shots

        Returns:
            List -- List of markers
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

    def get_comment_tag(self, p):
        """get_comment_tag will make a copy of a comment tag and set
        his comment as a note

        Arguments:
            p {Dict} -- Panel

        Returns:
            Dict -- Hiero Tag
        """
        comment = p.get('latest_open_note', {}).get('body', None)
        t = None
        if comment is not None:
            t = self.hiero_api.create_comment_tag(comment)
        return t

    def add_panel_info_tag(self, p, tags):
        """add_panel_info_tag will add a tag of the panel info

        Arguments:
            p {Dict} -- Panel

            tags {List} -- List of all tags

        Returns:
            List -- List of all tags
        """
        t = self.hiero_api.create_info_tag(json.dumps(p))
        tags.append(t)
        return tags

    def add_marker(self, markers_mapping, panel_in, sequence):
        """add_marker will add a marker in the sequence

        Arguments:
            markers_mapping {Dict} -- Mapping of markers

            panel_in {int} -- First frame of the panel
            (from the whole sequence)

            sequence {Dict} -- Hiero Sequence
        """
        if panel_in in markers_mapping:
            tag = self.hiero_api.create_marker_tag(
                panel_in,
                markers_mapping[panel_in])
            sequence.addTagToRange(tag, panel_in, panel_in + 1)

    def add_comment(self, p, tags):
        """add_comment will add a tag comment to the list

        Arguments:
            p {Dict} -- Panel

            tags {List} -- List of all tags

        Returns:
            List -- List of all tags
        """
        comment_tag = self.get_comment_tag(p)
        if comment_tag is not None:
            tags.append(comment_tag)
        return tags

    def create_burnin(self, track, fr, to, burnin_name):
        """create_burnin will create a burnin and add it to the track

        Arguments:
            track {Dict} -- Hiero Track

            fr {int} -- Start of the burnin

            to {int} -- End of the burnin

            burnin_name {str} -- Burnin Name
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

    def pull_to_sequence(self,
                         show_tc,
                         seq_rev_tc,
                         seq_tracking_code,
                         fn_update):
        """pull_to_sequence will pull to hiero a project, sequence and
        sequence revision bin, as well as a new Sequence

        Arguments:
            show_tc {str} -- Show tracking code

            seq_rev_tc {str} -- Sequence rev tracking code

            seq_tracking_code {str} -- Sequence tracking code

            fn_update {Callable[[str], None]} -- Update callback

        Returns:
            Tuple[Dict, Dict, Dict] -- Seq, Seq bin, Seq rev bin
        """
        hiero_project_name = 'Flix_{0}'.format(show_tc)
        fn_update('Get / Create hiero project: {0}'.format(hiero_project_name))
        my_project = self.hiero_api.get_project(hiero_project_name)
        seq_bin_name = 'Flix_{0}'.format(seq_tracking_code)
        fn_update('Get / Create Sequence bin: {0}'.format(seq_bin_name))
        seq, seq_bin_reused = self.hiero_api.get_project_bin(
            my_project, seq_bin_name)
        if seq_bin_reused is False:
            clipsBin = my_project.clipsBin()
            clipsBin.addItem(seq)
        seqrev_bin_name = 'v{0}'.format(seq_rev_tc)
        fn_update('Get / Create Sequence Rev bin: {0}'.format(seqrev_bin_name))
        seq_rev_bin, seq_rev_bin_reused = self.hiero_api.get_seq_bin(
            seq, seqrev_bin_name)
        if seq_rev_bin_reused is False:
            seq.addItem(seq_rev_bin)

        sequence_name = 'Flix_{0}_v{1}'.format(
                seq_tracking_code,
                seq_rev_tc)
        fn_update('Create Sequence: {}'.format(sequence_name))
        sequence = self.hiero_api.create_sequence(
            sequence_name)
        seq_item = self.hiero_api.sequence_to_bin_item(sequence)
        seq_rev_bin.addItem(seq_item)
        return sequence, seq, seq_rev_bin


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = hiero_ui()
    main_view.show()
    sys.exit(app.exec_())
