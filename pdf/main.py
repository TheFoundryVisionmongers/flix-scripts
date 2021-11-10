#
# Copyright (C) Foundry 2020
#

import getpass
import os
import pathlib
import sys
import tempfile
import traceback

import appdirs
import yaml
from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import (QApplication, QDialog, QErrorMessage,
                               QHBoxLayout, QMessageBox, QProgressDialog)

import flix_ui as flix_widget
import pdf_ui as pdf_widget


SETTINGS_FILE = pathlib.Path(appdirs.user_config_dir("Flix")) / ".contact_sheet"


class progress_canceled(Exception):
    """progress_canceled is an exception for the progress cancelled
    """
    pass


class main_dialogue(QDialog):

    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.export_path = None
        self.setWindowTitle('Flix Contact Sheet')
        self.settings = self.__read_settings()
        self.wg_flix_ui = flix_widget.flix_ui(self.settings)
        self.wg_pdf_ui = pdf_widget.pdf_ui(self.settings)
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

    def __read_settings(self):
        """Read the user's settings yaml"""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            pass
        except OSError:
            traceback.print_exc()

        return {}

    def __write_settings(self):
        """Write the user's settings yaml"""
        curr_settings = {
            **self.settings,
            "hostname": self.wg_flix_ui.hostname.text(),
            "username": self.wg_flix_ui.login.text(),
            "show": self.wg_flix_ui.show_list.currentText(),
            "sequence": self.wg_flix_ui.sequence_list.currentText(),
            "font": self.wg_pdf_ui.font,
            "font_size": self.wg_pdf_ui.wg_font_size.value(),
            "columns": self.wg_pdf_ui.wg_columns.value(),
            "rows": self.wg_pdf_ui.wg_rows.value(),
            "export_path": self.wg_pdf_ui.export_path.text(),
            "disclaimer": self.wg_pdf_ui.disclaimer.toPlainText(),
        }

        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w") as config_file:
                yaml.safe_dump(curr_settings, config_file)
        except OSError:
            traceback.print_exc()


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
                    font_size: int,
                    disclaimer: str):
        """on_generate will start the generatation of the contact sheet after
        retrieving all the data needed

        Arguments:
            font {str} -- Font path

            columns {int} -- Number of columns

            rows {int} -- Number of rows

            export_path {str} -- Export path (without the filename)

            font_size {int} -- Font size

            disclaimer {str} -- A disclaimer to print at the bottom of each page
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
                                          font_size,
                                          disclaimer)
        except progress_canceled:
            print('progress cancelled')

    def __generate_contact_sheet(self,
                                 font: str,
                                 columns: int,
                                 rows: int,
                                 export_path: str,
                                 rev_number: int,
                                 header: str,
                                 font_size: int,
                                 disclaimer: str):
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

            disclaimer {str} -- A disclaimer to print at the bottom of each page
        """
        self.__write_settings()

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
            output = self.wg_pdf_ui.generate_contact_sheet(font,
                                                           columns,
                                                           rows,
                                                           export_path,
                                                           panels,
                                                           header,
                                                           font_size,
                                                           disclaimer)
            output = pathlib.Path(output).absolute()
            self.__update_progress('', False)
            self.__info('Contact sheet successfully written to <a href="{}">{}</a>'.format(output.as_uri(), output.name))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
