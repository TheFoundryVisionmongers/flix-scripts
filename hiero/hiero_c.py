import re
from hiero.core import (Bin, BinItem, Format, Sequence, Tag, VideoTrack,
                        newProject, project, findProjectTags)
from hiero.ui import (activeSequence, windowManager)

class hiero_c:

    def __init__(self):
        self.preset_comment_tag = self.get_project_tag('Comment')
        self.preset_fr_tag_tag = self.get_project_tag('France')
        self.preset_ready_to_start_tag = self.get_project_tag(
            'Ready To Start')
        self.preset_ref_tag = self.get_project_tag('Reference')

    def get_project_tag(self, tag_name):
        tag = findProjectTags(
            project('Tag Presets'), tag_name)
        if len(tag) > 0:
            return tag[0]
        return tag

    def get_project(self, project_name):
        """get_project will reuse existing project depending of the
        project name or will create it
        project_name: project to find
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

    def create_comment_tag(self, comment):
        t = self.preset_comment_tag.copy()
        cleanr = re.compile(
            '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        comment = re.sub(cleanr, '', comment)
        t.setNote(comment)
        return t

    def create_marker_tag(self, in_time, marker_name):
        t = self.preset_ready_to_start_tag.copy()
        t.setNote(marker_name)
        t.metadata().setValue('tag.start', '{0}'.format(in_time))
        t.metadata().setValue('tag.length', '{0}'.format(1))
        t.setInTime(in_time)
        t.setOutTime(in_time + 1)
        return t

    def create_info_tag(self, note, visible=False):
        t = self.preset_fr_tag_tag.copy()
        t.setNote(note)
        t.setVisible(False)
        return t

    def add_dialogue_track_effect(self, track, track_item, settings):
        node = track.createEffect(
            effectType='Text2',
            trackItem=track_item,
            subTrackIndex=0).node()
        for name, value in settings.iteritems():
            node[name].setValue(value)

    def add_burnin_track_effect(self, track, fr, to, settings):
        node = track.createEffect(
            effectType='BurnIn',
            subTrackIndex=0,
            timelineIn=fr,
            timelineOut=to).node()
        for name, value in settings.iteritems():
            node[name].setValue(value)

    def create_video_track(self, name):
        return VideoTrack(name)

    def create_sequence(self, name):
        return Sequence(name)

    def sequence_to_bin_item(self, seq):
        return BinItem(seq)

    def get_item_tags_note(self, items, name):
        tags_notes = []
        for tag in items.tags():
            if tag.name() == name:
                tags_notes.append(tag.note())
        return tags_notes

    def get_active_sequence(self):
        return activeSequence()

    def new_window_manager(self):
        return windowManager()
