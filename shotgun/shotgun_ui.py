import os
import re
import sys
import tempfile
import time
from collections import OrderedDict
from typing import Dict, List, Tuple

from PySide2.QtCore import QCoreApplication, QSize, Qt, Signal
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                               QLineEdit, QMessageBox, QProgressDialog,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

import flix_ui as flix_widget
import shotgun as shotgun_api


class shotgun_ui(QWidget):

    e_local_export = Signal()
    e_shotgun_export = Signal(str)
    export_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        # Setup UI view
        v_main_box = QVBoxLayout()

        # Setup list for production handoff export option
        self.handoff_type_list = QComboBox()
        self.handoff_type_list.addItems(['Local Export', 'Shotgun Export'])
        self.handoff_type_label = QLabel('Handoff Type')
        self.handoff_type_label.setBuddy(self.handoff_type_list)
        self.handoff_type_list.currentTextChanged.connect(
            self.__on_handoff_type_changed)

        # Setup Local Export option
        self.export_layout = QHBoxLayout()
        self.export_path_button = QPushButton('Browse')
        self.export_path_button.clicked.connect(self.__browse_export_path)

        self.export_path, self.export_path_label = self.__create_line_label(
            '',
            'Export Path',
            200
        )
        self.__add_widget_to_layout(self.export_layout,
                                    self.export_path,
                                    self.export_path_button)

        # Setup Shotgun export option
        self.sg_hostname, self.sg_hostname_label = self.__create_line_label(
            'https://thomaslacroix.shotgunstudio.com',
            'Shotgun URL',
            350
        )
        self.sg_login, self.sg_login_label = self.__create_line_label(
            'thomas.lacroix@epitech.eu',
            'Username',
            200
        )

        pull = QPushButton('Export Latest')
        pull.clicked.connect(self.__pull_latest)

        self.__add_widget_to_layout(v_main_box,
                                    self.handoff_type_label,
                                    self.handoff_type_list,
                                    self.export_path_label)
        v_main_box.addLayout(self.export_layout)
        self.__add_widget_to_layout(v_main_box,
                                    self.sg_hostname_label,
                                    self.sg_hostname,
                                    self.sg_login_label,
                                    self.sg_login,
                                    pull)

        self.__update_ui_handoff_type('Local Export')
        self.setLayout(v_main_box)

    def get_shotgun_api(self):
        """get_shotgun_api will return the shotgun_api

        Returns:
            object -- Shotgun api
        """
        return self.shotgun

    def create_folders(
            self,
            show_tc: str,
            seq_tc: str,
            seq_rev_nbr: int,
            episode_tc: str = None) -> str:
        """create_folders will create the structure of folders from
        shows to sequence revision

        Arguments:
            show_tc {str} -- Show tracking code

            seq_tc {str} -- Sequence tracking code

            seq_rev_nbr {int} -- Sequence revision number

        Keyword Arguments:
            episode_tc {str} -- Episode tracking code (default: {None})

        Returns:
            str -- Sequence revision path
        """
        show_path = os.path.join(self.export_path.text(), show_tc)
        self.__create_folder(show_path)
        sequence_path = os.path.join(show_path, seq_tc)
        if episode_tc is not None:
            episode_path = os.path.join(show_path, episode_tc)
            self.__create_folder(episode_path)
            sequence_path = os.path.join(episode_path, seq_tc)
        self.__create_folder(sequence_path)
        sequence_revision_path = os.path.join(
            sequence_path, 'v{0}'.format(seq_rev_nbr))
        self.__create_folder(sequence_revision_path)
        return sequence_revision_path

    def get_shot_download_paths(
            self, export_path: str, shot: str) -> Tuple[str, str, str]:
        """get_shot_download_paths will create folders for show, artwork and thumbnails
        and return those paths

        Arguments:
            export_path {str} -- Base export path

            shot {str} -- Shot name

        Returns:
            Tuple[str, str, str] -- show_path, artwork_path, thumb_path
        """
        show_folder_path = os.path.join(export_path, shot)
        self.__create_folder(show_folder_path)
        artwork_folder_path = os.path.join(show_folder_path, 'artwork')
        self.__create_folder(artwork_folder_path)
        thumb_folder_path = os.path.join(show_folder_path, 'thumbnail')
        self.__create_folder(thumb_folder_path)
        return show_folder_path, artwork_folder_path, thumb_folder_path

    def export_to_version(
            self,
            shots: List,
            sg_password: str,
            show_tc,
            seq_rev_nbr,
            seq_tc) -> Dict:
        """export_to_version will export to shotgun a project, a sequence, a shot and version

        Arguments:
            shots {List} -- List of shots

            sg_password {str} -- Shotgun password

            show_tc {str} -- Show tracking code

            seq_rev_nbr {int} -- Sequence revision number

            seq_tc {str} -- Sequence tracking code

        Returns:
            Dict -- Mapping of shot to quicktime info with his corresponding shotgun version
        """
        sg_show = self.shotgun.get_project(show_tc)
        if sg_show is None:
            sg_show = self.shotgun.create_project(show_tc)
        sg_seq = self.shotgun.get_sequence(sg_show, seq_tc)
        if sg_seq is None:
            sg_seq = self.shotgun.create_seq(sg_show, seq_tc)

        shot_to_file = {}
        for shot_name in shots:
            sg_shot = self.shotgun.get_shot(sg_show, sg_seq, shot_name)
            if sg_shot is None:
                sg_shot = self.shotgun.create_shot(sg_show, sg_seq, shot_name)
            version = self.shotgun.get_version(sg_show, sg_shot)
            if version is None:
                new_version = 1
            else:
                ver = re.search('(.*)v([0-9]+)', version['code'])
                new_version = int(ver.group(2)) + 1
            version = self.shotgun.create_version(
                sg_show, sg_shot, new_version)
            mov_name = '{0}_v{1}_{2}.mov'.format(
                seq_tc, seq_rev_nbr, shot_name)
            shot_to_file[shot_name] = {
                'mov_name': mov_name, 'version': version}
        return shot_to_file

    def init_local_export(self) -> bool:
        """init_local_export will initialise the export

        Returns:
            bool -- If the export path is valid or not
        """
        if len(self.export_path.text()) <= 0:
            self.__info('You need to select an export path')
            return False
        if os.path.exists(self.export_path.text()) is False:
            self.__info('Invalid export path')
            return False
        return True

    def init_shotgun_export(self) -> bool:
        """init_shotgun_export will init the shotgun export

        Returns:
            bool -- Can login to shotgun
        """
        if self.sg_login.text() == '' or self.sg_hostname.text() == '':
            self.__info('You need to enter your shotgun info')
            return '', False
        sg_password, ok = QInputDialog().getText(self,
                                                 'Shotgun password',
                                                 'Shotgun password:',
                                                 QLineEdit.Password)
        if ok is False:
            return '', False
        self.shotgun = shotgun_api.shotgun(self.sg_hostname.text(),
                                           self.sg_login.text(),
                                           sg_password)
        return sg_password, True

    def __pull_latest(self):
        """__pull_latest will export the latest sequence revision
        """
        if self.selected_handoff_type == 'Local Export':
            if self.init_local_export():
                self.e_local_export.emit()
        else:
            sg_password, ok = self.init_shotgun_export()
            if ok:
                self.e_shotgun_export.emit(sg_password)

    def __create_line_label(self,
                            name: str,
                            label: str,
                            min_width: int = 200) -> Tuple[Dict,
                                                           Dict]:
        """__create_line_label will create a line edit button and his label

        Arguments:
            name {str} -- Default value

            label {str} -- Label name

        Keyword Arguments:
            min_width {int} -- Minium width (default: {200})

        Returns:
            Tuple[Dict, Dict] -- Line Edit, Label
        """
        line_edit = QLineEdit(name)
        line_edit.setMinimumWidth(min_width)
        label = QLabel(label)
        label.setBuddy(line_edit)
        return line_edit, label

    def __add_widget_to_layout(self, layout: Dict, *widgets: Dict):
        """__add_widget_to_layout will add all the widget to a layout
        __add_widget_to_layout(layout, widget1, widget2, widget3)

        Arguments:
            layout {Dict} -- Layout to add widget to

            widgets {*Dict} -- All the widgets to add
        """

        for w in widgets:
            layout.addWidget(w)

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

    def __on_handoff_type_changed(self, handoff_type: str):
        """__on_handoff_type_changed triggered when the handoff type changed

        Arguments:
            handoff_type {str} -- Handoff type from the event
        """
        self.__update_ui_handoff_type(handoff_type)

    def __browse_export_path(self):
        """__browse_export_path will create a dialog window to
        browse and set an export path
        """
        dialog = QFileDialog()
        export_p = None
        if self.export_path.text() is not '':
            if os.path.exists(self.export_path.text()):
                export_p = self.export_path.text()
        export_p = dialog.getExistingDirectory(dir=export_p)
        if len(export_p) < 1:
            return
        self.export_path.setText(export_p)

    def __update_ui_handoff_type(self, handoff_type: str):
        """__update_ui_handoff_type will update the UI depending
        of the handoff type

        Arguments:
            handoff_type {str} -- Handoff type
        """
        if handoff_type == 'Local Export':
            self.sg_hostname.hide()
            self.sg_hostname_label.hide()
            self.sg_login.hide()
            self.sg_login_label.hide()
            self.export_path_label.show()
            self.export_path.show()
            self.export_path_button.show()
        else:
            self.sg_hostname.show()
            self.sg_hostname_label.show()
            self.sg_login.show()
            self.sg_login_label.show()
            self.export_path_label.hide()
            self.export_path.hide()
            self.export_path_button.hide()
        self.selected_handoff_type = handoff_type

    def __create_folder(self, path: str):
        """__create_folder will create a folder if it does not exist

        Arguments:
            path {str} -- Path to create the folder
        """
        if not os.path.exists(path):
            os.makedirs(path)


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.setWindowTitle('Shotgun')

        main_layout = QVBoxLayout()
        widget_shotgun_ui = shotgun_ui()

        # Add shotgun Ui widget
        main_layout.addWidget(widget_shotgun_ui)
        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
