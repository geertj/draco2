# vi: ts=8 sts=4 sw=4 et
#
# test_basic.py: tests for draco2.draw
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

from draco2.draw import *
from draco2.draw.test.support import DracoDrawTest


class TestBasic(DracoDrawTest):

    def test_hello_world(self):
        image = Image.new(300, 200, truecolor=1)
        painter = Painter(image)
        painter.set_pen(Pen(RGBA(0, 0, 0)))
        painter.set_brush(Brush(RGBA(255, 255, 255)))
        painter.draw_rectangle((0, 0), 300, 200)
        font = Font('mediumbold')
        painter.set_font(font)
        painter.draw_text((100, 100), 'Hello, world!')
        fobj = self.tempfile('w+b')
        image.save(fobj, 'png')
        fobj.seek(0)
        image2 = Image.load(fobj, 'png')
        assert image2.width() == 300
        assert image2.height() == 200
        assert image2.truecolor()
