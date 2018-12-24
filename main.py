from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import *
from reportlab.pdfbase.ttfonts import *
from reportlab.pdfgen import canvas

import re
from PIL import Image
import os
import json

import webbrowser


class MyCanvas(canvas.Canvas):
    itemlist_point = '・'

    def __init__(self, filename, pagesize, font_name, font_path):
        # super init
        super().__init__(filename=filename, pagesize=pagesize)

        self.width, self.height = pagesize
        # register font
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        self.font_name = font_name

    def drawString_with_newline(self, x, current_y, text, font_size=40, colorRGB=(0,0,0)):
        self.setFont_all(font_size, colorRGB)

        draw_lines = text.split('\n')

        for line_num, draw_line in enumerate(draw_lines):

            self.drawString(
                x,
                # 真ん中ーフォントサイズの半分下げて真ん中にする＋ライン分上げるー行分下げる
                self.height / 2 - font_size / 2 + len(draw_lines) * font_size / 2 - font_size * line_num + current_y,
                draw_line
            )

    def drawHeader(self, current_x, current_y, text, font_size=35, colorRGB=(0,0,0)):
        self.setFont_all(font_size, colorRGB)
        self.drawRightString(self.width+current_x, self.height-font_size+current_y, text)

    def drawTitle(self, current_x, current_y, text, font_size=60, colorRGB=(0,0,0)):
        self.setFont_all(font_size, colorRGB)
        self.drawCentredString(self.width/2 + current_x, self.height/2 + current_y, text)

    def parse_text(self, text, x=50):
        re_header = re.compile(r'^(#+)\s(.*)$')
        re_itemlist = re.compile(r'^-\s(.*)$')
        re_blank = re.compile(r'^$')
        re_newline = re.compile(r'^.*\s{2}$')
        re_image = re.compile(r'^!\[(.*)\]\((.*)\)$')

        lines = text.split('\n')
        draw_text = ''
        for line_num, line in enumerate(lines):
            header = re_header.match(line)
            image = re_image.match(line)
            if header is not None:
                sharp_num = len(header.group(1))  # amount of #s
                if sharp_num == 1:
                    self.drawTitle(0, 0, header.group(2))
                    self.showPage()
                elif sharp_num >= 2:  # TODO: #の数ごとの挙動
                    self.drawHeader(-10, -10, header.group(2))
            elif image is not None:
                if self.pageHasData():
                    self.showPage()
                image_data = Image.open(image.group(2))
                self.drawInlineImage(image_data, (self.width-image_data.width)/2, (self.height-image_data.height)/2)
            else:
                itemlist = re_itemlist.match(line)
                if itemlist is not None:
                    draw_text += self.itemlist_point + itemlist.group(1) + '\n'
                elif re_newline.match(line) is not None:
                    print('new')
                    draw_text += '\n'
                elif re_blank.match(line) is not None:
                    print('lans')
                    self.drawString_with_newline(x, 0, draw_text.strip())
                    self.showPage()
                    draw_text = ''
                else:
                    draw_text += line+'\n'

    def setFont_all(self, font_size, colorRGB):
        self.setFont(self.font_name, font_size)
        self.setFillColorRGB(colorRGB[0], colorRGB[1], colorRGB[2])


j = json.loads(open('./config.json').read())
FONT_PATH = j['font_path']
FILENAME = j['output_name']
INPUT_FILE_NAME = j['input_path']

c = MyCanvas(filename=FILENAME, pagesize=landscape(A4), font_name='UDDigital', font_path=FONT_PATH)
c.setTitle(os.path.basename(FILENAME))

string = open(INPUT_FILE_NAME).read()

c.parse_text(string)

c.save()
webbrowser.open(url='file:'+os.path.abspath(FILENAME))
