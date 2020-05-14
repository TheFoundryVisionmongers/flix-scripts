import re
from hiero.core import (Bin, BinItem, Format, Sequence, Tag, VideoTrack,
                        newProject, project, findProjectTags)
from hiero.ui import (activeSequence, windowManager)


class hiero_c:
    """hiero_c is an interface with Hiero to create tags, project, bins etc.
    """

    def __init__(self):
        self.preset_comment_tag = self.get_project_tag('Comment')
        self.preset_fr_tag_tag = self.get_project_tag('France')
        self.preset_ready_to_start_tag = self.get_project_tag(
            'Ready To Start')
        self.preset_ref_tag = self.get_project_tag('Reference')

    def get_project_tag(self, tag_name):
        """get_project_tag will retreive a preset tag

        Arguments:
            tag_name {str} -- tag name

        Returns:
            Dict -- Hiero Tag
        """
        tag = findProjectTags(
            project('Tag Presets'), tag_name)
        if len(tag) > 0:
            return tag[0]
        return tag

    def get_project(self, project_name):
        """get_project will reuse existing project depending of the
        project name or will create it

        Arguments:
            project_name {str} -- Project to find / create

        Returns:
            Dict -- Hiero Project
        """
        my_project = project(project_name)
        if my_project is None:
            my_project = newProject(project_name)
        f = Format(1000, 562, 1, 'flix')
        my_project.setOutputFormat(f)
        return my_project

    def add_track_item(
            self,
            track,
            track_item_name,
            source_clip,
            duration=12,
            tags=[],
            last_track_item=None):
        """add_track_item will add a trackitem to a track, it will
        add a source and tags

        Arguments:
            track {Dict} -- Track to add the new track item

            track_item_name {str} -- Name of the new track item

            source_clip {Dict} -- Clip to link to the track item

        Keyword Arguments:
            duration {int} -- Duration of the clip (default: {12})

            tags {list} -- list of tags to add (default: {[]})

            last_track_item {[type]} -- previous track item (default: {None})

        Returns:
            Dict -- New Track Item
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

    def get_project_bin(self, project_bin, bin_name):
        """get_project_bin will try to reuse a bin from a project depending
        on the bin_name or will create it

        Arguments:
            project_bin {Dict} -- Project Bin

            bin_name {str} -- Bin's name to find

        Returns:
            Dict -- Hiero Project Bin
        """
        b = project_bin.bins(bin_name)
        if len(b) > 0:
            b = b[0]
            return b, True
        return Bin(bin_name), False

    def get_seq_bin(self, host_b, bin_name):
        """get_seq_bin will try to reuse a bin from a project depending on
        the bin_name or will create it

        Arguments:
            host_b {Dict} -- Host Bin

            bin_name {[type]} -- Bin's name to find

        Returns:
            Dict -- Hiero Bin
        """
        b = host_b.bins()
        for seq_bin in b:
            if seq_bin.name() == bin_name:
                return seq_bin, True
        return Bin(bin_name), False

    def get_clips(self, seq_bin):
        """get_clips will retrieve all the clips from the bin

        Arguments:
            seq_bin {Dict} -- bin of the sequence

        Returns:
            [type] -- [description]
        """
        clips = {}
        for b in seq_bin.bins():
            for c in b.clips():
                clips[c.name()] = c.activeItem()
        return clips

    def create_comment_tag(self, comment):
        """create_comment_tag will create a comment tag

        Arguments:
            comment {str} -- Comment

        Returns:
            Dict -- Hiero Tag
        """
        t = self.preset_comment_tag.copy()
        cleanr = re.compile(
            '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        comment = re.sub(cleanr, '', comment)
        t.setNote(comment)
        return t

    def create_marker_tag(self, in_time, marker_name):
        """create_comment_tag will create a marker tag

        Arguments:
            in_time {int} -- Start of the marker tag

            marker_name {str} -- Marker Name

        Returns:
            Dict -- Hiero Tag
        """
        t = self.preset_ready_to_start_tag.copy()
        t.setNote(marker_name)
        t.metadata().setValue('tag.start', '{0}'.format(in_time))
        t.metadata().setValue('tag.length', '{0}'.format(1))
        t.setInTime(in_time)
        t.setOutTime(in_time + 1)
        return t

    def create_info_tag(self, note, visible=False):
        """create_info_tag will create an info tag

        Arguments:
            note {str} -- Content

        Keyword Arguments:
            visible {bool} -- Set tag bvisible or not (default: {False})

        Returns:
            Dict -- Hiero Tags
        """
        t = self.preset_fr_tag_tag.copy()
        t.setNote(note)
        t.setVisible(False)
        return t

    def add_dialogue_track_effect(self, track, track_item, settings):
        """add_dialogue_track_effect will create a dialogue track effect
        and set settings to his node

        Arguments:
            track {Dict} -- Track to add effect on

            track_item {Dict} -- Track Item

            settings {Dict} -- Settings to apply to the node
        """
        node = track.createEffect(
            effectType='Text2',
            trackItem=track_item,
            subTrackIndex=0).node()
        for name, value in settings.iteritems():
            node[name].setValue(value)

    def add_burnin_track_effect(self, track, fr, to, settings):
        """add_burnin_track_effect will create a burnin track effect
        and set settings to his node

        Arguments:
            track {Dict} -- Track to add effect on

            fr {int} -- Start of the burnin

            to {int} -- End of the burnin

            settings {Dict} -- Settings to apply to the node
        """
        node = track.createEffect(
            effectType='BurnIn',
            subTrackIndex=0,
            timelineIn=fr,
            timelineOut=to).node()
        for name, value in settings.iteritems():
            node[name].setValue(value)

    def create_video_track(self, name):
        """create_video_track will create a video track

        Arguments:
            name {str} -- Video track name

        Returns:
            Dict -- Hiero Video Track
        """
        return VideoTrack(name)

    def create_sequence(self, name):
        """create_sequence will create a sequence

        Arguments:
            name {str} -- Sequence name

        Returns:
            Dict -- Hiero Sequence
        """
        return Sequence(name)

    def sequence_to_bin_item(self, seq):
        """sequence_to_bin_item will make an Sequence as bin item

        Arguments:
            seq {Dict} -- Sequence

        Returns:
            Dict -- Hiero Bin Item
        """
        return BinItem(seq)

    def get_item_tags_note(self, item, name):
        """get_item_tags_note will get items tag's notes depending
        on the the tag name

        Arguments:
            items {Dict} -- Item

            name {str} -- Tag's name to get

        Returns:
            List -- List of tags
        """
        tags_notes = []
        for tag in item.tags():
            if tag.name() == name:
                tags_notes.append(tag.note())
        return tags_notes

    def get_active_sequence(self):
        """get_active_sequence will return the active Sequence

        Returns:
            Dict -- Hiero Active Sequence
        """
        return activeSequence()

    def get_window_manager(self):
        """get_window_manager will return the window manager

        Returns:
            Dict -- Hiero Window Manager
        """
        return windowManager()
