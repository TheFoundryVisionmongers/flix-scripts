#
# Copyright (C) Foundry 2020
#

import os
import sys
import tempfile

from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import (QApplication, QDialog, QErrorMessage,
                               QHBoxLayout, QMessageBox, QProgressDialog)

import flix_ui as flix_widget
import shotgun_ui as shotgun_widget


class progress_canceled(Exception):
    """progress_canceled is an exception for the progress cancelled
    """
    pass


class main_dialogue(QDialog):

    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.export_path = None
        self.setWindowTitle('Flix Production Handoff')
        self.wg_flix_ui = flix_widget.flix_ui()
        self.wg_shotgun_ui = shotgun_widget.shotgun_ui()

        self.wg_shotgun_ui.e_local_export.connect(self.on_local_export)
        self.wg_shotgun_ui.e_shotgun_export.connect(self.on_shotgun_export)

        # Setup UI view
        h_main_box = QHBoxLayout()
        h_main_box.addWidget(self.wg_flix_ui)
        h_main_box.addWidget(self.wg_shotgun_ui)
        self.setLayout(h_main_box)

    def __error(self, message: str):
        """__error will show a error message with a given message

        Arguments:
            message {str} -- Message to show
        """
        err = QErrorMessage(self.parent())
        err.setWindowTitle('Flix')
        err.showMessage(message)
        err.exec_()

    def __info(self, message: str):
        """__info will show a message with a given message

        Arguments:
            message {str} -- Message to show
        """
        msgbox = QMessageBox(self.parent())
        msgbox.setWindowTitle('Flix')
        msgbox.setText(message)
        msgbox.exec_()

    def __update_progress(self,
                          message: str,
                          skip_step: bool = True):
        """update_progress will update the progress message
        and will return False if the progress is 'canceled' by the user

        Arguments:
            message {str} -- Message to show in the progress

            skip_step {bool} -- Will skip the step (default: {True})
        """
        next_value = self.progress_start
        if skip_step is False:
            next_value = next_value + 1
        self.progress_start = next_value
        self.progress.setValue(next_value)
        self.progress.setLabelText(message)
        self.progress.repaint()
        QCoreApplication.processEvents()
        if self.progress.wasCanceled():
            raise progress_canceled

    def __init_progress(self, steps: int):
        """__init_progress will init the progress bar

        Arguments:
            steps {int} -- Number of step of the progress bar
        """
        self.progress = QProgressDialog('Operation in progress.',
                                        'Stop',
                                        0,
                                        steps)
        self.progress_start = 0
        self.progress.setMinimumWidth(400)
        self.progress.setMinimumHeight(100)
        self.progress.show()

    def on_local_export(self):
        """on_local_export will export the latest sequence revision locally
        It is going to fetch the needed information from Flix_ui and will
        create folders from shotgun_ui associated to the show / episode / sequence, will
        generate a quicktime per shot and will download it as well as the
        artworks and thumbnails
        """
        if self.wg_flix_ui.is_authenticated() is False:
            self.__error('you need to be authenticated to Flix')
            return

        self.__init_progress(2)

        try:
            self.__update_progress('get media objects per shots', False)
            mo_per_shots = self.wg_flix_ui.get_media_object_per_shots(
                self.__update_progress)
            if mo_per_shots is None:
                return

            self.progress.setRange(0, 3 + len(mo_per_shots) * 4)
            self.progress.repaint()
            QCoreApplication.processEvents()

            self.__update_progress('get flix info', False)
            _, episodic, show_tc = self.wg_flix_ui.get_selected_show()
            _, seq_rev_nbr, seq_tc = self.wg_flix_ui.get_selected_sequence()
            episode_tc = None
            if episodic:
                _, episode_tc = self.wg_flix_ui.get_selected_episode()

            # Create folders for export
            self.__update_progress('create folders for export', False)
            seq_rev_path = self.wg_shotgun_ui.create_folders(
                show_tc, seq_tc, seq_rev_nbr, episode_tc)

            for shot in mo_per_shots:
                # Create / retrieve path for local export per shot
                self.__update_progress(
                    'create path for shot {0}'.format(shot), False)
                show_path, art_path, thumb_path = self.wg_shotgun_ui.get_shot_download_paths(
                    seq_rev_path, shot)

                # Quicktime:
                self.__update_progress(
                    'download quicktime for shot {0}'.format(shot), False)
                mov_name = '{0}_v{1}_{2}.mov'.format(
                    seq_tc, seq_rev_nbr, shot)
                mov_path = os.path.join(show_path, mov_name)
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    mov_path = mov_path.replace('\\', '\\\\')
                self.wg_flix_ui.get_flix_api().download_media_object(
                    mov_path, mo_per_shots[shot].get('mov'))

                # Artworks:
                self.__update_progress(
                    'download artworks for shot {0}'.format(shot), False)
                for mo in mo_per_shots[shot].get('artwork', []):
                    self.wg_flix_ui.local_download(art_path, mo, seq_rev_nbr)
                # Thumbnails:
                self.__update_progress(
                    'download thumbnails for shot {0}'.format(shot), False)
                for mo in mo_per_shots[shot].get('thumbnails', []):
                    self.wg_flix_ui.local_download(thumb_path, mo, seq_rev_nbr)
        except progress_canceled:
            print('progress cancelled')
            return
        self.__info('Latest sequence revision exported locally')

    def on_shotgun_export(self, sg_password: str):
        """on_shotgun_export will export a the latest sequence revision to
        shotgun. Will first retrieve all the media info per shots from flix_ui,
        and will start creating or reusing projects / sequence / shots and version per shot from
        shotgun_ui, It will then export a quicktime per shot from flix_ui and will upload it to shotgun

        Arguments:
            sg_password {str} -- Shotgun password
        """
        if self.wg_flix_ui.is_authenticated() is False:
            self.__error('you need to be authenticated to Flix')
            return

        self.__init_progress(2)

        try:
            self.__update_progress('get media object per shots', False)
            mo_per_shots = self.wg_flix_ui.get_media_object_per_shots(
                self.__update_progress)
            if mo_per_shots is None:
                return

            self.progress.setRange(0, 2 + len(mo_per_shots) * 2)
            self.progress.repaint()
            QCoreApplication.processEvents()

            _, _, show_tc = self.wg_flix_ui.get_selected_show()
            _, seq_rev_nbr, seq_tc = self.wg_flix_ui.get_selected_sequence()
            # Create project / sequence / shot and version in Shotgun
            self.__update_progress('push to shotgun', False)
            shot_to_file = self.wg_shotgun_ui.export_to_version(
                mo_per_shots.keys(),
                sg_password,
                show_tc,
                seq_rev_nbr,
                seq_tc,
                self.__update_progress)

            temp_folder = tempfile.gettempdir()
            for shot in shot_to_file:
                self.__update_progress(
                    'download quicktime for shot {0}'.format(shot), False)
                mov_path = os.path.join(
                    temp_folder, shot_to_file[shot]['mov_name'])
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    mov_path = mov_path.replace('\\', '\\\\')
                # Download quictime from Flix
                self.wg_flix_ui.get_flix_api().download_media_object(
                    mov_path, mo_per_shots[shot].get('mov'))
                # Upload quicktime to shotgun version
                self.__update_progress(
                    'upload quicktime to shotgun for shot {0}'.format(shot), False)
                self.wg_shotgun_ui.get_shotgun_api().upload_movie(
                    shot_to_file[shot]['version'], mov_path)
        except progress_canceled:
            print('progress cancelled')
            return
        self.__info('Latest sequence revision exported to shotgun')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
