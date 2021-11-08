#
# Copyright (C) Foundry 2020
#

import copy
import os
import random
import string
from typing import Callable, Dict, List, Tuple

import matplotlib.font_manager as fontman
import reportlab.lib.pagesizes
import reportlab.pdfgen.canvas
from reportlab.lib.colors import black
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle


class Pdf(object):

    def __init__(self,
                 font,
                 columns,
                 rows,
                 export_path,
                 panels,
                 header_title,
                 font_size=8):
        self.row = rows
        self.column = columns
        self.margin_size = 25
        self.styles = getSampleStyleSheet()
        # Extract invalid chars for Windows filename
        filename = header_title
        for invalid_char in ['\\', '/', '*', '<', '>', ':', '?', '|']:
            filename = filename.replace(invalid_char, '')
        filename = '{}.pdf'.format(filename)
        self.output = os.path.join(export_path, filename)
        self.font_type_path = font
        self.font_size = font_size
        self.panels = panels
        self.title = header_title
        self.text_color = 'black'

    def build_canvas(self):
        """build_canvas will generate the contact sheet and save it
        """
        if os.path.exists(self.output):
            os.remove(self.output)

        # Initialise the canvas
        self.page_width, self.page_height = self.__get_page_size()
        self.canvas = reportlab.pdfgen.canvas.Canvas(self.output,
                                                     pagesize=self.page_size)
        self.canvas.setLineWidth(width=.6)
        rowCounter = 0
        colCounter = 0
        pageNumber = 1
        self.panel_vert_shift = 0
        self.text_gap = 60
        self.margin_header = 8
        self.header = 15
        self.full_header = self.header + self.margin_header

        # Load the font
        self.__load_font_type()

        # Set the header
        self.__set_header()

        # Set each panels (image / dialogue / New / etc.)
        for index, image_data in enumerate(self.panels):
            image = image_data['thumb']
            panel = ImageReader(image)
            panel_width, panel_height = self.__get_panel_size(panel)
            panel_x, panel_y = self.__get_panel_position(panel_width,
                                                         panel_height,
                                                         rowCounter,
                                                         colCounter)

            image_data.update({"panel_x": panel_x,
                               "panel_y": panel_y,
                               "panel_w": panel_width,
                               "panelH": panel_height})

            self.canvas.drawImage(panel,
                                  panel_x,
                                  panel_y,
                                  width=panel_width,
                                  height=panel_height)
            self.canvas.rect(panel_x,
                             panel_y,
                             width=panel_width,
                             height=panel_height)

            self.canvas.setFont(self.fontType, self.font_size)

            # Set the panel ID - Revision
            panel_label = "%04d - %02d" % (int(image_data['id']),
                                           int(image_data['rev']))
            self.canvas.drawString(panel_x, panel_y - 7, panel_label)

            # Set the panel position
            self.canvas.drawRightString(panel_x + panel_width,
                                        panel_y - 7, '%04d' % (index + 1))

            # Set the marker
            if image_data['marker'] is not None:
                self.canvas.drawString(panel_x, panel_y + panel_height + 2, image_data['marker'])

            # Set the dialogue
            self.__set_panel_dialogue(image_data)

            # Set the "New" icon published images
            self.__set_panel_new_icon(image_data)

            # Update current counters (rows / columns)
            colCounter += 1
            if colCounter == self.column:
                colCounter = 0
                rowCounter += 1

            # Handle next pages
            if rowCounter == self.row and not index == (len(self.panels) - 1):
                self.canvas.showPage()
                self.__set_header()
                pageNumber += 1
                rowCounter = 0

        # save the pdf
        self.canvas.save()

    def __set_panel_new_icon(self, panel_data: Dict):
        """__set_panel_new_icon will set the "new" for published panels only

        Arguments:
            panel_data (Dict): Panel informations
        """
        panel_x = panel_data.get("panel_x")
        panel_y = panel_data.get("panel_y")
        panel_h = panel_data.get("panelH")
        panel_w = panel_data.get("panel_w")
        if not panel_data.get('published', False):
            margin_width = 2 * 3
            margin_height = 2 * 2
            new_label_w = pdfmetrics.stringWidth('NEW',
                                                 self.fontType,
                                                 self.font_size) + margin_width
            new_label_h = self.font_size + margin_height
            new_label_x = panel_x + panel_w - new_label_w
            new_label_y = panel_y + panel_h
            self.canvas.setFillColorRGB(.05, .44, 0)
            self.canvas.setStrokeColor(black)
            self.canvas.setLineWidth(width=.6)
            self.canvas.rect(new_label_x,
                             new_label_y,
                             new_label_w,
                             new_label_h,
                             fill=True,
                             stroke=True)
            new_text_x = new_label_x + new_label_w / 2
            new_text_y = new_label_y + new_label_h / 4
            self.canvas.setFillColor(black)
            self.canvas.setFont(self.fontType, self.font_size)
            self.canvas.drawCentredString(new_text_x, new_text_y, 'NEW')

    def __load_font_type(self):
        """__load_font_type will load the provided font
        """
        letters = string.ascii_letters
        self.fontType = ''.join(random.choice(letters) for i in range(10))
        pdfmetrics.registerFont(TTFont(self.fontType, self.font_type_path))

    def __set_panel_dialogue(self, panel_data: Dict):
        """__set_panel_dialogue will set the dialogue (if any) under
        the panel

        Arguments:
            panel_data (Dict): Panel info
        """
        if len(panel_data.get('dialogue', '')) < 1:
            return

        panel_x = panel_data.get("panel_x")
        panel_y = panel_data.get("panel_y")
        panel_w = panel_data.get("panel_w")

        text_y = panel_y - self.text_gap
        text_height = self.text_gap
        if not self.image_gap_h < self.text_gap:
            text_height = self.image_gap_h
        text_width = panel_w * 2 / 3

        dialogue = self.__trim_text(
            text_width - 22,
            text_height,
            panel_data.get(
                'dialogue',
                ''),
            self.styles['BodyText'])
        dialogue = dialogue.replace('<', '&lt;')
        dialogue = dialogue.replace('>', '&gt;')
        dialogue = dialogue.replace("\n", "<br/>")
        if len(dialogue) > 0:
            dialogue = "\"" + dialogue + "\""

        p_info = {'textColor': self.text_color,
                  'fontSize': self.font_size,
                  'fontName': self.fontType,
                  'dialogue': dialogue}
        style = copy.deepcopy(self.styles['BodyText'])
        style.leading = self.font_size

        panel_name = Paragraph('''<para align=center spaceb=3>
                                 <font name=%(fontName)s
                                 size=%(fontSize)s color=%(textColor)s>
                                 %(dialogue)s</font></para>''' % p_info, style)

        data = [[panel_name]]

        table = Table(data, colWidths=text_width, rowHeights=self.text_gap)
        table.setStyle(TableStyle([('VALIGN', (-1, -1), (-1, -1), 'TOP')]))
        table.wrapOn(self.canvas, text_width, self.text_gap)
        table.drawOn(self.canvas, panel_x + panel_w / 6, text_y)

    def __get_page_size(self) -> Tuple[int, int]:
        """__get_page_size will get the page size

        Returns:
            Tuple[int, int] -- width, height
        """
        pagesizes_import = __import__("reportlab.lib.pagesizes",
                                      globals(),
                                      locals(),
                                      ['letter'])
        letter = getattr(pagesizes_import, 'letter')
        self.page_size = getattr(pagesizes_import, "landscape")(letter)

        return self.page_size[0], self.page_size[1]

    def __get_panel_size(self, panel: dict) -> Tuple[int, int]:
        """__get_panel_size will get the size of a panel depending
        on the rows / colums / margins / header etc.

        Arguments:
            panel (dict): Panel info

        Returns:
            Tuple[int, int]: panel_width, panel_height
        """
        o_width, o_height = panel.getSize()
        double_margin = self.margin_size * 2
        one_panel_per_page = (self.row == 1 and self.column == 1)
        # panel width without the margin from the page, still contains margins
        # between panels
        panel_w_with_margin = (self.page_width - double_margin) / self.column
        # panel height eithout the margin from the page, still contains marings
        # between panels
        panel_h_with_margin = (
            self.page_height - double_margin + self.text_gap) / self.row
        # margin width from all other panels columns in the page
        margin_w_from_other_columns = self.margin_size * \
            ((self.column - 1) / float(self.column))
        # margin height from all others panels rows in the page
        margin_h_from_other_rows = self.text_gap * \
            (self.row - 1) / float(self.row)

        if self.row >= self.column and not one_panel_per_page:
            panel_height = panel_h_with_margin - margin_h_from_other_rows
            panel_width = panel_height * o_width / float(o_height)
            panel_x = panel_width * self.column
            next_panel_margin = self.margin_size * (self.column + 1)
            if panel_x + next_panel_margin >= self.page_width:
                panel_width = panel_w_with_margin - margin_w_from_other_columns
                panel_height = panel_width * float(o_height) / o_width
        else:
            panel_width = panel_w_with_margin - margin_w_from_other_columns
            panel_height = panel_width * float(o_height) / o_width

        return panel_width, panel_height

    def __set_header(self):
        """__set_header will set the header
        """
        self.canvas.setFont(self.fontType, 8)
        self.canvas.setFillColorRGB(.68, .68, .68)
        self.canvas.rect(
            self.margin_size, (self.page_height - self.full_header),
            (self.page_width - (self.margin_size * 2)),
            self.header, fill=True, stroke=True)

        # header text
        self.canvas.setFillColor('black')
        title_split = simpleSplit(
            self.title, self.fontType, 8,
            (self.page_width - (self.margin_size * 2)))
        self.canvas.drawString(
            (self.margin_size * 1.25),
            self.page_height - self.margin_header - .75 * self.header,
            title_split[0])

    def __get_panel_position(self,
                             panel_w: int,
                             panel_h: int,
                             row_counter: int,
                             col_counter: int) -> Tuple[int, int]:
        """__get_panel_position will get the panel position depending
        on the rows / colums / margins / header etc.

        Arguments:
            panel_w (int): Panel width
            panel_h (int): Panel height
            row_counter (int): Current row
            col_counter (int): Current column

        Returns:
            Tuple[int, int]: panel_x, panel_y
        """
        # calculate the gap between each image based on image size and page
        # size
        self.image_gap_w = (
            (self.page_width - (self.margin_size * 2)) -
            (panel_w * self.column)) / (
            self.column - 1) if self.column > 1 else 0
        self.image_gap_h = (
            (self.page_height - ((self.full_header + self.margin_size))) -
            (panel_h * self.row)) / self.row if self.row > 1 else 30

        # calculate where each images x,y positions are
        panel_x = ((panel_w + self.image_gap_w) *
                   col_counter) + self.margin_size
        panel_y = (
            (self.page_height - (self.full_header + self.margin_size)) -
            ((panel_h + self.image_gap_h) * (row_counter + 1)))
        if row_counter == 0:
            panel_y_expected = (
                (self.page_height - (self.full_header + self.margin_size)) -
                (panel_h * (row_counter + 1)))
            if panel_y != panel_y_expected:
                self.panel_vert_shift = panel_y - panel_y_expected
        panel_y -= self.panel_vert_shift

        return panel_x, panel_y

    def __line_wrap(self,
                    combinedLines: List,
                    styleType: Dict) -> Tuple[int, int]:
        """__line_wrap will wrap all the lines and get the height / width

        Arguments:
            combinedLines (List): List of lines
            styleType (Dict): Style

        Returns:
            Tuple[int, int]: width, height
        """
        # Get overall width of text by getting stringWidth of longest line
        width = pdfmetrics.stringWidth(
            max(combinedLines),
            self.fontType, self.font_size)
        # Paragraph height can be calculated via line spacing and number of
        # lines.
        height = styleType.leading * len(combinedLines)
        return width, height

    def __trim_text(self,
                    max_w: int,
                    max_h: int,
                    text: str,
                    style: Dict) -> str:
        """__trim_text will trim a text and add epsilon if too long

        Arguments:
            max_w (int): Max width
            max_h (int): Max height
            text (str): Text to trim
            style (Dict): Style

        Returns:
            str: New str
        """
        lines = self.__break_lines(text, max_w)
        original_lines_length = len(lines)
        if lines:
            width, height = self.__line_wrap(lines, style)
            while int(height) > int(max_h) or int(width) > int(max_w):
                if height < max_h or len(lines) == 1:
                    break
                del lines[-1]
                width, height = self.__line_wrap(lines, style)
        new_str = " ".join(lines)
        if len(lines) < original_lines_length:
            new_str = new_str[:-3]
            new_str += "..."
        return new_str

    def __break_lines(self, textString: str, max_w: int) -> str:
        """__break_lines will break lines

        Arguments:
            textString (str): Text to break
            max_w (int): Max width

        Returns:
            str: New str
        """
        return simpleSplit(textString, self.fontType, self.font_size, max_w)


def get_system_fonts() -> List[str]:
    """get_system_fonts will get a list of all the fonts (.ttf) from the system

    Returns:
        List[str]: List of all the fonts
    """
    matches = list(
        filter(
            lambda path: str(path).lower().endswith('.ttf'),
            fontman.findSystemFonts()))
    matches = sorted(matches)
    return matches
