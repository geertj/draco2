# vi: ts=8 sts=4 sw=4 et
#
# brush.py: the Brush class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.draw.image import Image


class Brush(object):
    """The Brush object.

    A Brush defines how a Painter should fill shapes. Example:

    >>> brush = Brush(RGBA(255,0,0))
    >>> painter.set_brush(brush)
    """

    SOLID = 0
    TILED = 1

    def __init__(self, color=None, style=SOLID, tile=None):
	"""Initializes this brush.

        By default, a brush with no color and style Brush.SOLID is created.
	"""
	self.set_color(color)
	self.set_style(style)
	self.set_tile(tile)

    def color(self):
	"""Return the current color."""
	return self.m_color

    def set_color(self, color):
	"""Set the color of the Brush.

        The `color' parameter must be an RGBA value for painting on a
        truecolor image, or a color index for an indexed color image.
        Additionally, `color' can be None in which case no pixels are
        touched.
	""" 
	self.m_color = color

    def style(self):
	"""Return the current style."""
	return self.m_style

    def set_style(self, style):
	"""Set the style for the brush.
        
        The `style' parameter can be one of:
	  - Brush.SOLID: Shapes are filled with a solid colo, see .set_color().
	  - Brush.TILED: Shapes are filled with an Image tile, see .set_tile().
	"""
	if style > self.TILED:
	    raise ValueError, 'Illegal style value.'
	self.m_style = style

    def tile(self):
	"""Return the current tile."""
	return self.m_tile

    def set_tile(self, tile):
	"""Set the fill tile for this brush."""
	if tile is not None and not isinstance(tile, Image):
	    raise TypeError, 'Expecting an "Image" instance or None.'
	self.m_tile = tile
