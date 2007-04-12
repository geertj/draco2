# vi: ts=8 sts=4 sw=4 et
#
# font.py: draco2.draw font classes
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import gd


class Font(object):
    """Builtin GD font.

    Five builting fonts exist: "tiny", "small", "mediumbold", "large" and
    "giant". Example:

    >>> font = Font('tiny')
    >>> painter.set_font(font)
    """

    _fonts = { 'tiny': gd.FontTiny, 'small': gd.FontSmall,
    	       'mediumbold': gd.FontMediumBold, 'large': gd.FontLarge,
    	       'giant': gd.FontGiant }

    def __init__(self, font='mediumbold'):
	"""Construct a new builtin font.
        
        If no arguments are specified, the default MediumBold font is used.
	"""
	self.set_font(font)

    def font(self):
	"""Return the current font."""
	return self.m_font

    def set_font(self, font):
	"""Set the current font."""
	try:
	    self.m_gdfont = self._fonts[font.lower()]
	    self.m_font = font
	except KeyError:
	    raise ValueError, 'Illegal font name.'

    def _font(self):
	"""Return the low-level gd font."""
	return self.m_gdfont


class TTFont(Font):
    """A truetype font.

    A truetype font is specified by a file name in the font search path or
    the current directory, together with a point size. Example:

    >>> font = TTFont("verdana.ttf", 11)
    >>> painter.set_ttfont(font)
    """

    def __init__(self, font, pointsize):
	"""Construct a new truetype font.
        
        The `font' parameter specifies the file name of a truetype font, and
        `pointsize' specifies the point size to use.
	"""
	self.m_font = font
	self.m_pointsize = pointsize

    def font(self):
	"""Return the current font."""
	return self.m_font

    def set_font(self, font):
	"""Set the current font."""
	self.m_font = font

    def pointsize(self):
	"""Return the current point size."""
	return self.m_pointsize

    def set_pointsize(self, pointsize):
	"""Set the current point size."""
	self.m_pointsize = pointsize
