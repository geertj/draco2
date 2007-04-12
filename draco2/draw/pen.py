# vi: ts=8 sts=4 sw=4 et
#
# pen.py: the Pen class
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


class Pen(object):
    """The Pen object.

    A Pen defines how a Painter should draw lines and outlines of shapes.
    Example:

    >>> pen = Pen(RGBA(255,0,0))
    >>> painter.set_pen(pen)
    """

    SOLID = 0
    PATTERNED = 1
    DECORATED = 2
    PATTERN_DECORATED = 3

    def __init__(self, color=None, style=SOLID, width=1, pattern=None,
		 decoration=None):
	"""Intialise the Pen.
        
        By default, a Pen with style Pen.SOLID and color black is created.
        You can specify a different color with COLOR.
	"""
	self.set_color(color)
	self.set_style(style)
	self.set_width(width)
	self.set_pattern(pattern)
	self.set_decoration(decoration)

    def color(self):
	"""Return the current pen color."""
	return self.m_color

    def set_color(self, color):
	"""Set the color of this Pen.
        
        The `color' parameter must be an RGBA value for painting on a
        truecolor image, or a color index for an indexed color image.
        Additionally, `color' can be None in which case no pixels are
        touched.
	"""
	self.m_color = color

    def style(self):
	"""Return the current pen style."""
	return self.m_style
    
    def set_style(self, style):
	"""
	Set the style for this Pen.
        
        The `style' parameter can be one of:
	  - Pen.SOLID: Draws a solid line.
	  - Pen.PATTERNED: Draws a patterned line, see set_pattern().
	  - Pen.DECORATED: Draws a decorated line, see set_decoration().
	  - Pen.PATTERN_DECORATED: Draws a patterned and decorated line.
	"""
	if style > self.PATTERN_DECORATED:
	    raise ValueError, 'Illegal style parameter.'
	self.m_style = style

    def width(self):
	"""Return the current pen width."""
	return self.m_width

    def set_width(self, width):
	"""Sets the pen width."""
	if width < 1:
	    raise ValueError, 'Expecting a width > 1.'
	self.m_width = width

    def pattern(self):
	"""Return the current pattern."""
	return self.m_pattern

    def set_pattern(self, pattern):
	"""Set the pattern for this Pen.
        
        The `pattern' argument must be a sequence of integers, specifying
        the colors of subsequent pixels in the line.  The color can be the
        special value Pen.Transparent for a transparent pixel.
	"""
        if isinstance(pattern, list) or isinstance(pattern, tuple):
            pattern = list(pattern)
            for i in range(len(pattern)):
                if pattern[i] is None:
                    pattern[i] = gd.Transparent
                elif not isinstance(pattern[i], int):
                    raise TypeError, 'Expecting a sequence of integers.'
        elif pattern is not None:
            raise TypeError, 'Expecting None or a sequence.'
	self.m_pattern = pattern

    def decoration(self):
	"""Return the current decoration."""
	return self.m_decoration

    def set_decoration(self, decoration):
	"""Sets a decoration for this Pen.
        
        The `decoration' argument must be an Image object. The Image is
        drawn at every pixel of the line. 
	"""
	if decoration is not None and not isinstance(decoration, Image):
	    raise TypeError, 'Expecting an Image object.'
	self.m_decoration = decoration
