#
# Copyright (C) Foundry 2020
#

import os
import re
import sys
import tempfile
import time
from collections import OrderedDict
from typing import Callable, Dict, List, Tuple

from PySide2.QtCore import QRegExp, QSize, Qt, Signal
from PySide2.QtGui import QPixmap, QRegExpValidator
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QErrorMessage,
                               QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSizePolicy,
                               QVBoxLayout, QWidget)

import pdf as pdf_api


class pdf_ui(QWidget):
    """pdf_ui is a widget that allow you to create a contact sheet

    e_generate: font_path, columns, rows, export_path, font_size
    """

    e_generate = Signal(str, int, int, str, int)

    export_path = None
    font = None

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self.system_fonts = pdf_api.get_system_fonts()

        # Setup UI view
        v_main_box = QVBoxLayout()

        # Setup list for production handoff export option
        self.fonts_list = QComboBox()
        for f in self.system_fonts:
            self.fonts_list.addItem(f)
        self.fonts_list_label = QLabel('Font')
        self.fonts_list_label.setBuddy(self.fonts_list)
        self.fonts_list.currentTextChanged.connect(
            self.__on_font_changed)
        if len(self.system_fonts) > 0:
            self.__on_font_changed(self.system_fonts[0])

        self.wg_font_size, self.wg_font_size_label = self.__create_line_label(
            self.settings.get("font_size", '8'),
            'Font Size (1-8)',
            200,
            "[1-8]")
        self.wg_columns, self.wg_columns_label = self.__create_line_label(
            self.settings.get("columns", '3'),
            'Columns (1-5)',
            350,
            "[1-5]")
        self.wg_rows, self.wg_rows_label = self.__create_line_label(
            self.settings.get("rows", '3'),
            'Rows (1-5)',
            200,
            "[1-5]")

        # Setup Local Export option
        self.export_layout = QHBoxLayout()
        self.export_path_button = QPushButton('Browse')
        self.export_path_button.clicked.connect(self.__browse_export_path)

        self.export_path, self.export_path_label = self.__create_line_label(
            self.settings.get("export_path", ''),
            'Export Path',
            200
        )
        self.__add_widget_to_layout(self.export_layout,
                                    self.export_path,
                                    self.export_path_button)

        generate_btn = QPushButton('Generate Contact Sheet')
        generate_btn.clicked.connect(self.__generate)

        self.__add_widget_to_layout(v_main_box,
                                    self.fonts_list_label,
                                    self.fonts_list,
                                    self.wg_font_size_label,
                                    self.wg_font_size,
                                    self.wg_columns_label,
                                    self.wg_columns,
                                    self.wg_rows_label,
                                    self.wg_rows,
                                    self.export_path_label)
        v_main_box.addLayout(self.export_layout)
        self.__add_widget_to_layout(v_main_box, generate_btn)

        self.setLayout(v_main_box)

    def generate_contact_sheet(self,
                               font,
                               columns,
                               rows,
                               export_path,
                               panels,
                               header,
                               font_size):
        pdf = pdf_api.Pdf(
            font,
            columns,
            rows,
            export_path,
            panels,
            header,
            font_size)
        return pdf.build_canvas()

    def __create_line_label(self,
                            name: str,
                            label: str,
                            min_width: int = 200,
                            reg_exp: str = None) -> Tuple[Dict,
                                                          Dict]:
        """__create_line_label will create a line edit button and his label

        Arguments:
            name {str} -- Default value

            label {str} -- Label name

            min_width {int} -- Minium width (default: {200})

        Returns:
            Tuple[Dict, Dict] -- Line Edit, Label
        """
        line_edit = QLineEdit(name)
        line_edit.setMinimumWidth(min_width)
        if reg_exp is not None:
            rx = QRegExp(reg_exp)
            validator = QRegExpValidator(rx, self)
            line_edit.setValidator(validator)
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

    def __browse_export_path(self):
        """__browse_export_path will create a dialog window to
        browse and set an export path
        """
        dialog = QFileDialog()
        export_p = None
        if self.export_path.text() != '':
            if os.path.exists(self.export_path.text()):
                export_p = self.export_path.text()
        export_p = dialog.getExistingDirectory(dir=export_p)
        if len(export_p) < 1:
            return
        self.export_path.setText(export_p)

    def __on_font_changed(self, ft: str):
        """__on_font_changed is triggered when the font changed

        Arguments:
            ft {str} -- Font path
        """
        self.font = ft

    def __generate(self):
        """__generate is triggered when the generate button is clicked.
        It will ensure the font, rows, columns and font size are set correctly
        before emitting a signal to e_generate
        """
        if self.font is None:
            self.__error("You need to select a font")
            return
        if int(self.wg_columns.text()) < 1 or int(self.wg_rows.text()) < 1:
            self.__error("You need to set columns / rows within 1-5")
            return
        if self.export_path is None or self.export_path.text() == '':
            self.__error("You need to select an export path")
            return
        if int(self.wg_font_size.text()) < 1:
            self.__error("You need to set columns / rows within 1-8")
            return
        self.e_generate.emit(self.font,
                             int(self.wg_columns.text()),
                             int(self.wg_rows.text()),
                             self.export_path.text(),
                             int(self.wg_font_size.text()))


class main_dialogue(QDialog):
    def __init__(self, parent=None):
        super(main_dialogue, self).__init__(parent)
        self.setWindowTitle('PDF')

        main_layout = QVBoxLayout()
        widget_pdf_ui = pdf_ui()

        # Add pdf Ui widget
        main_layout.addWidget(widget_pdf_ui)
        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_view = main_dialogue()
    main_view.show()
    sys.exit(app.exec_())
