#
# Copyright (C) Foundry 2020
#

import getpass
import os
import pathlib
import sys
import tempfile

import yaml
from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import (QApplication, QDialog, QErrorMessage,
                               QHBoxLayout, QMessageBox, QProgressDialog)

import flix_ui as flix_widget
import pdf_ui as pdf_widget


SETTINGS_FILE_NAME = ".flix-contact-sheet"


class progress_canceled(Exception):
    """progress_canceled is an exception for the progress cancelled
    """
    pass


class main_dialogue(QDialog):

    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.export_path = None
        self.setWindowTitle('Flix Contact Sheet')
        settings = self._read_settings()
        self.wg_flix_ui = flix_widget.flix_ui(settings)
        self.wg_pdf_ui = pdf_widget.pdf_ui(settings)
        self.wg_pdf_ui.e_generate.connect(self.on_generate)

        # Setup UI view
        h_main_box = QHBoxLayout()
        h_main_box.addWidget(self.wg_flix_ui)
        h_main_box.addWidget(self.wg_pdf_ui)
        self.setLayout(h_main_box)

        # Set cursor in the first empty field
        if not self.wg_flix_ui.hostname.text():
            self.wg_flix_ui.hostname.setFocus()
        elif not self.wg_flix_ui.login.text():
            self.wg_flix_ui.login.setFocus()
        else:
            self.wg_flix_ui.password.setFocus()

    def closeEvent(self, event):
        self._write_settings()

    @property
    def settings_path(self):
        try:
            home_dir = str(pathlib.Path.home())
            return os.path.join(home_dir, SETTINGS_FILE_NAME)
        except:
            return None

    def _read_settings(self):
        """Read the user's settings yaml

        """
        if not self.settings_path:
            return {}

        settings = {}
        try:
            if os.path.exists(self.settings_path):
                settings = yaml.safe_load(open(self.settings_path, 'r'))
            else:
                print("No settings file: {}".format(self.settings_path))

        except Exception as err:
            sys.stderr.write(err)

        return settings

    def _write_settings(self):
        """Write the user's settings yaml

        """
        if not self.settings_path:
            return

        settings = self._read_settings()
        curr_settings = {
            "hostname": self.wg_flix_ui.hostname.text(),
            "username": self.wg_flix_ui.login.text(),
            "show": self.wg_flix_ui.show_list.currentText(),
            "sequence": self.wg_flix_ui.sequence_list.currentText(),
            "font_size": self.wg_pdf_ui.wg_font_size.text(),
            "columns": self.wg_pdf_ui.wg_columns.text(),
            "rows": self.wg_pdf_ui.wg_rows.text(),
            "export_path": self.wg_pdf_ui.export_path.text()
        }

        # Only overwrite settings if the user inputted something
        for key, setting in curr_settings.items():
            if setting:
                settings[key] = setting

        try:
            with open(self.settings_path, "w") as config_file:
                config_file.write(yaml.dump(settings))

        except Exception as err:
            sys.stderr.write(err)

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

    def on_generate(self,
                    font: str,
                    columns: int,
                    rows: int,
                    export_path: str,
                    font_size: int):
        """on_generate will start the generatation of the contact sheet after
        retrieving all the data needed

        Arguments:
            font {str} -- Font path

            columns {int} -- Number of columns

            rows {int} -- Number of rows

            export_path {str} -- Export path (without the filename)

            font_size {int} -- Font size
        """
        if self.wg_flix_ui.is_authenticated() is False:
            self.__error("You need to be authenticated")
            return
        seq_rev = self.wg_flix_ui.get_selected_sequence_rev()
        if seq_rev is None:
            self.__error("You need to select a sequence revision")
            return
        rev_number = seq_rev.get('revision')

        episode_id = None
        _, episodic, show_tc = self.wg_flix_ui.get_selected_show()
        _, _, seq_tc = self.wg_flix_ui.get_selected_sequence()

        header = '{0} - {1} -- Revision: {2} - {3}'.format(
            show_tc,
            seq_tc,
            rev_number,
            seq_rev.get('comment'))
        if episodic:
            _, epi_tc = self.wg_flix_ui.get_selected_episode()
            header = '{0} - {1} - {2} -- Revision: {3} - {4}'.format(
                show_tc,
                epi_tc,
                seq_tc,
                rev_number,
                seq_rev.get('comment', ''))
        try:
            self.__generate_contact_sheet(font,
                                          columns,
                                          rows,
                                          export_path,
                                          rev_number,
                                          header,
                                          font_size)
        except progress_canceled:
            print('progress cancelled')

    def __generate_contact_sheet(self,
                                 font: str,
                                 columns: int,
                                 rows: int,
                                 export_path: str,
                                 rev_number: int,
                                 header: str,
                                 font_size: int):
        """__generate_contact_sheet will download all the files and start
        generate the contact sheet

        Arguments:
            font {str} -- Font path

            columns {int} -- Number of columns

            rows {int} -- Number of rows

            export_path {str} -- Export path (without the filename)

            rev_number {int} -- Revision number

            header {str} -- Title of the header

            font_size {int} -- Font size
        """
        self.__init_progress(4)

        # Get panels from from sequence revision
        self.__update_progress('Getting panels from sequence revision', False)
        panels = self.wg_flix_ui.get_panels_with_thumbs(self.__update_progress)

        # Create temp folder
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Download thumbnails
            self.__update_progress('Downloading thumbnails', False)
            for p in panels:
                self.__update_progress(
                    'Downloading thumbnails for panel {}-{}'.format(p['id'],
                                                                    p['rev']))
                mo_path = self.wg_flix_ui.local_download(tmpdirname,
                                                         p.get('mo', None),
                                                         rev_number)
                p['thumb'] = mo_path

            # Generate contact sheet
            self.__update_progress(
                'Generating contact sheet (this might take some time)',
                False)
            self.wg_pdf_ui.generate_contact_sheet(font,
                                                  columns,
                                                  rows,
                                                  export_path,
                                                  panels,
                                                  header,
                                                  font_size)
            self.__update_progress('', False)
            self.__info('Contact sheet successfully created')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
