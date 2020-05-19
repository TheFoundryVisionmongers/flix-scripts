import os
import re
import sys
import tempfile
import time
from collections import OrderedDict
from typing import Dict, List, Tuple

from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                               QLineEdit, QMessageBox, QProgressDialog,
                               QPushButton, QVBoxLayout)

import flix_ui as flix_widget
import shotgun_ui as shotgun_widget


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

    def on_local_export(self):
        if self.wg_flix_ui.is_authenticated() is False:
            self.__error('you need to be authenticated to Flix')
            return

        mo_per_shots = self.wg_flix_ui.get_media_object_per_shots()
        if mo_per_shots is None:
            return
        
        _, episodic, show_tc = self.wg_flix_ui.get_selected_show()
        _, seq_rev_nbr, seq_tc = self.wg_flix_ui.get_selected_sequence()
        episode_tc = None
        if episodic:
            _, episode_tc = self.wg_flix_ui.get_selected_episode()

        # Create folders for export
        seq_rev_path = self.wg_shotgun_ui.create_folders(show_tc, seq_tc, seq_rev_nbr, episode_tc)

        for shot in mo_per_shots:
            # Create / retrieve path for local export per shot
            show_path, art_path, thumb_path = self.wg_shotgun_ui.get_shot_download_paths(seq_rev_path, shot)

            # Quicktime:
            mov_name = '{0}_v{1}_{2}.mov'.format(
                seq_tc, seq_rev_nbr, shot)
            mov_path = os.path.join(show_path, mov_name)
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                mov_path = mov_path.replace('\\', '\\\\')
            self.wg_flix_ui.get_flix_api().download_media_object(
                mov_path, mo_per_shots[shot].get('mov'))

            # Artworks:
            for mo in mo_per_shots[shot].get('artwork', []):
                self.wg_flix_ui.local_download(art_path, mo, seq_rev_nbr)
            # Thumbnails:
            for mo in mo_per_shots[shot].get('thumbnails', []):
                self.wg_flix_ui.local_download(thumb_path, mo, seq_rev_nbr)

    def on_shotgun_export(self, sg_password):
        if self.wg_flix_ui.is_authenticated() is False:
            self.__error('you need to be authenticated to Flix')
            return

        mo_per_shots = self.wg_flix_ui.get_media_object_per_shots()
        if mo_per_shots is None:
            return

        _, _, show_tc = self.wg_flix_ui.get_selected_show()
        _, seq_rev_nbr, seq_tc = self.wg_flix_ui.get_selected_sequence()
        # Create project / sequence / shot and version in Shotgun
        shot_to_file = self.wg_shotgun_ui.export_to_version(mo_per_shots.keys(), sg_password, show_tc, seq_rev_nbr, seq_tc)

        temp_folder = tempfile.gettempdir()
        for shot in shot_to_file:
            mov_path = os.path.join(temp_folder, shot_to_file[shot]['mov_name'])
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                mov_path = mov_path.replace('\\', '\\\\')
            # Download quictime from Flix
            self.wg_flix_ui.get_flix_api().download_media_object(
                mov_path, mo_per_shots[shot].get('mov'))
            # Upload quicktime to shotgun version
            self.wg_shotgun_ui.get_shotgun_api().upload_movie(shot_to_file[shot]['version'],
                                                              mov_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
