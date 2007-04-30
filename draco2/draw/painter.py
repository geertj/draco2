# vi: ts=8 sts=4 sw=4 et
#
# painter.py: the Painter class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import math
import gd

from draco2.draw.exception import *
from draco2.draw.image import Image
from draco2.draw.pen import Pen
from draco2.draw.brush import Brush
from draco2.draw.font import Font, TTFont


class Painter(object):
    """The Painter object.

    A Painter can paint shapes and text onto an Image. Supported shapes 
    are point, line, rectangle, polygon and various arcs. Text is supported
    with draw_text() in combination with 5 builtin fonts, or draw_texttt() with
    user supplied truetype fonts.

    The outline and fill colors and styles can be set by specifying a pen and 
    a brush, see set_pen() and set_brush(). A black pen and empty brush are 
    initially set up for the painter.

    A Painter also includes a simple coordinate transformation. Shapes can
    be translated and scaled, see translate() and scale().
    """

    RADIANS = 180.0/math.pi

    def __init__(self, image=None):
	"""Create a new painter.
        
        The painter is initialized with a default Pen, Brush and Font.
	"""
	self.set_pen(Pen())
	self.set_brush(Brush())
	self.set_font(Font())
        self.set_ttfont(None)
        self.set_alphablending(1)
	self.paint(image)

    def reset(self):
	"""Reset this painter."""
	self.translate(0,0)
	self.scale(1,1)

    def paint(self, image):
	"""Start painting on the image `image'.
        
        Coordinate transformations are reset but pens, brushes and fonts are
        kept.
        """
	if isinstance(image, Image):
	    self.m_image = image._image()
	elif image is None:
	    self.m_image = None
	else:
	    raise TypeError, 'Expecting an Image instance or None.'
	self.reset()

    def _check_image(self):
	if self.m_image is None:
	    raise DrawError, 'Not painting on any image.'


    # COORDINATE TRANSFORMATIONS

    def scale(self, sx, sy):
	"""Scales all drawing operations with a factor SX and SY."""
	self.m_sx = sx
	self.m_sy = sy

    def translate(self, dx, dy):
	"""Translates all drawing operations by (OFFX,OFFY)."""
	self.m_dx = dx
	self.m_dy = dy

    def scalex(self):
	return self.m_sx

    def scaley(self):
	return self.m_sy

    def offsetx(self):
	return self.m_dx

    def offsety(self):
	return self.m_dy

    def to_device(self, p):
        """Translates world coordinates to device (pixel) coordinates,
        rounded to the nearest integer value.
        """
        if isinstance(p[0], tuple) or isinstance(p[0], list):
	    xform = []
	    for i in p:
		xform.append(self.to_device(i))
	    return xform
	xd = int(p[0] * self.m_sx + self.m_dx + 0.5)
	yd = int(p[1] * self.m_sy + self.m_dy + 0.5)
	return xd, yd

    def to_world(self, p):
	"""Translates device (pixel) coordinates to world coordinates."""
        if isinstance(p[0], tuple) or isinstance(p[0], list):
	    xform = []
	    for i in p:
		xform.append(self.to_world(i))
	    return xform
	xw = ((p[0] - self.m_dx) / self.m_sx)
	yw = ((p[1] - self.m_dy) / self.m_sy)
	return xw, yw

    # STYLE

    def set_pen(self, pen):
	"""Set the active pen for the Painter.
        
        A pen determines how outlines are drawed. As a shortcut you can use
        set_pen(COLOR) to set a pen with color COLOR and style Pen.SOLID.
        """
        if pen is None or isinstance(pen, int):
	    pen = Pen(pen)
	elif not isinstance(pen, Pen):
	    raise TypeError, 'Expecting a Pen object.'
	self.m_pen = pen

    def pen(self):
	"""Return the current pen."""
	return self.m_pen

    def set_brush(self, brush):
	"""Set the active brush for the painter to `brush'.
        
        A brush deterimines how shapes are filled. As a shortcut you can use
        set_brush(COLOR) to set a brush with color `color' and style
        Brush.SOLID.
	"""
        if brush is None or isinstance(brush, int):
	    brush = Brush(brush)
	elif not isinstance(brush, Brush):
	    raise TypeError, 'Expecting a Brush object.'
	self.m_brush = brush

    def brush(self):
	"""Return the current brush."""
	return self.m_brush

    def set_font(self, font):
	"""Set the active builtin font for the painter."""
	if not isinstance(font, Font):
	    raise TypeError, 'Expecting a Font object.'
	self.m_font = font

    def font(self):
	"""Return the current font."""
	return self.m_font

    def set_ttfont(self, font):
	"""Set the active truetype font for the painter.
        
        The `font' parameter must be a TTFont instance.
	"""
	if font is not None and not isinstance(font, TTFont):
	    raise TypeError, 'Expecting a TTFont object.'
	self.m_ttfont = font

    def ttfont(self):
	"""Return the current truetype font."""
	return self.m_ttfont

    def set_alphablending(self, blend):
	"""Set the alpha blending flag to `blend'.
        
        If alpha blending is set, pixels are blended to the image in draw
        operations, if not, pixels are just copied.
	"""
        self.m_blend = blend

    def alphablending(self):
        """Return nonzero if alphablending is enabled."""
        return self.m_blend

    def _apply_image(self):
        """Apply the configured style to an image."""
        # Apply pen
        pen = self.m_pen
	if pen.style() == Pen.SOLID:
	    self.m_color = pen.color()
	elif pen.style() == Pen.PATTERNED:
	    if not pen.pattern():
		raise DrawError, 'Pen has no pattern set.'
	    self.m_color = gd.Styled
	    self.m_image.set_style(pen.pattern())
	elif pen.style() == Pen.DECORATED:
	    if not pen.decoration():
		raise DrawError, 'Pen has no decoration set.'
	    self.m_color = gd.Brushed
	    self.m_image.set_brush(pen.decoration())
	elif pen.style() == Pen.PATTERN_DECORATED:
	    if not pen.pattern() or not pen.decoration():
		raise DrawError, 'Pen has no style and decoration set.'
	    self.m_color = gd.StyledBrushed
	    self.m_image.set_style(pen.pattern())
	    self.m_image.set_brush(pen.decoration())
	self.m_image.setThickness(pen.width())
        # Apply brush
        brush = self.m_brush
	if brush.style() == Brush.SOLID:
	    self.m_bgcolor = brush.color()
	elif brush.style() == Brush.TILED:
	    if brush.tile() is None:
		raise DrawError, 'Brush has no tile set.'
	    self.m_bgcolor = gd.TILED
	    self.m_image.set_tile(brush.tile())
        # Alphablending
	self.m_image.alphaBlending(self.m_blend)

    # READ FUNCTIONS

    def get_pixel(self, p):
        """Read a pixel at location `p' and return the RGBA value."""
        self._check_image()
        self._apply_image()
        x,y = self.to_device(p)
        val = self.m_image.getPixel(x, y)
        rgba = self.m_image.colorGet(val)
        return rgba

    # DRAWING FUNCTIONS

    def draw_point(self, p):
	"""Draws a point at location `p'."""
	self._check_image()
        self._apply_image()
        if self.m_color is not None:
            x,y = self.to_device(p)
            self.m_image.setPixel(x, y, self.m_color)

    def draw_line(self, p1, p2):
	"""Draws a line between the points `p1' and `p2'."""
	self._check_image()
        self._apply_image()
        if self.m_color is not None:
            x1,y1 = self.to_device(p1)
            x2,y2 = self.to_device(p2)
            self.m_image.line(x1, y1, x2, y2, self.m_color)

    def draw_rectangle(self, p, w, h):
	"""Draws a rectangle with upper left corner `p', width `w' and
        height `h'.
	"""
	self._check_image()
        self._apply_image()
	if w == 0 or h == 0:
	    return
	x1,y1 = self.to_device(p)
	x2,y2 = self.to_device((p[0]+w-1, p[1]+h-1))
	# Find upper left corner. A transformation with a negative factor
	# could have changed which point is upper left.
	if x2 < x1:
	    x1, x2 = x2, x1
	if y2 < y1:
	    y1, y2 = y2, y1
	if self.m_bgcolor is not None:
	    self.m_image.rectangle(x1, y1, x2, y2, self.m_bgcolor, 1)
	if self.m_color is not None and self.m_color != self.m_bgcolor:
	    self.m_image.rectangle(x1, y1, x2, y2, self.m_color, 0)

    def draw_polygon(self, points):
	"""Draws a polygon with vertices `points'. The `points' parameter
        must be a sequence of points.
	"""
	self._check_image()
        self._apply_image()
	poly = self.to_device(points)
	if self.m_bgcolor is not None:
	    self.m_image.polygon(poly, self.m_bgcolor, 1)
	if self.m_color is not None and self.m_color != self.m_bgcolor:
	    self.m_image.polygon(poly, self.m_color, 0)

    def draw_ellipse(self, p, r1, r2):
	"""Draws an ellipse centered at point `p' with radius one `r1' and 
	radius two `r2'.
	"""
	self._check_image()
        self._apply_image()
	x, y = self.to_device(p)
	d1 = int(2 * r1 * self.m_sx + 0.5)
	d2 = int(2 * r2 * self.m_sy + 0.5)
	if self.m_bgcolor is not None:
	    self.m_image.filledArc(x, y, d1, d2, 0, 360, self.m_bgcolor, gd.Pie)
	if self.m_color is not None and self.m_color != self.m_bgcolor:
	    self.m_image.filledArc(x, y, d1, d2, 0, 360, self.m_color, gd.NoFill)

    def _transform_arc(self, r1, r2, angle, alen):
	"""Transforms arc parameters for use with gd."""
	# We use radiuses, GD uses diameters.
	d1 = int(abs(2*r1*self.m_sx) + 0.5)
	d2 = int(abs(2*r2*self.m_sy) + 0.5)
	# GDs definition of the angle is in degrees, ours in radians.
	a1 = int(angle * self.RADIANS + 0.5)
	a2 = int((angle + alen) * self.RADIANS  + 0.5)
	# Negative scale factors means mirroring!
	if self.m_sx < 0:
	    a1, a2 = 180-a2, 180-a1
	if self.m_sy < 0:
	    a1, a2 = -a2, -a1
	a1 = a1 % 360
	a2 = a2 % 360
	return d1, d2, a1, a2

    def draw_arc(self, p, r1, r2, angle, alen):
        """Draws an arc centered at point `p', with radius one `r1', radius
        two `r2', start angle `angle' and arc length `alen'.
        
        The `a' and `alen' parameters must be given in radians. An arc is a
        line and thus never filled, even if it spans 360 degrees.
	"""
	self._check_image()
        self._apply_image()
        if self.m_color is not None:
            x, y = self.to_device(p)
            d1, d2, a1, a2 = self._transform_arc(r1, r2, angle, alen)
            self.m_image.filledArc(x, y, d1, d2, a1, a2, self.m_color,
                        gd.Arc|gd.NoFill)

    def draw_pie(self, p, r1, r2, angle, alen):
	"""Draws a pie slice centered at point `p', with radius one `r1',
        radius two `r2', start angle `angle' and arc length `alen'.
        
        The `a' and `alen' parameters must be given in radians.  A pie is an
        arc with the two end points connected to the center point.
	"""
	self._check_image()
        self._apply_image()
	x, y = self.to_device(p)
	d1, d2, a1, a2 = self._transform_arc(r1, r2, angle, alen)
	if self.m_bgcolor is not None:
	    self.m_image.filledArc(x, y, d1, d2, a1, a2, self.m_bgcolor,
			gd.Edged)
	if self.m_color is not None and self.m_color != self.m_bgcolor:
	    self.m_image.filledArc(x, y, d1, d2, a1, a2, self.m_color,
			gd.Edged|gd.NoFill)

    def draw_chord(self, p, r1, r2, angle, alen):
	"""Draws a chord centered at point `p', with radius one `r1', radius
        two `r2', start angle `angle' and arc length `alen'.
        
        The `a' and `alen' parameters must be given in radians.  A chord is
        an arc with the two end points connected by at straight line.
	"""
	self._check_image()
        self._apply_image()
	x, y = self.to_device(p)
	d1, d2, a1, a2 = self._transform_arc(r1, r2, angle, alen)
	if self.m_bgcolor is not None:
	    self.m_image.filledArc(x, y, d1, d2, a1, a2, self.m_bgcolor,
			gd.Chord)
	if self.m_color is not None and self.m_color != self.m_bgcolor:
	    self.m_image.filledArc(x, y, d1, d2, a1, a2, self.m_color,
			gd.Chord|gd.NoFill)

    def draw_text(self, p, text, vertical=0):
	"""Draws the string `text' at point `p' using the current builtin font.
	If `vertical' is nonzero, the text is drawn vertically.

	NOTE: The font size is _not_ subject to coordinate transforms!
	"""
	self._check_image()
        self._apply_image()
        if self.m_color is not None:
            x, y = self.to_device(p)
            self.m_image.string(self.m_font._font(), x, y, text,
                        self.m_color, vertical)

    def draw_texttt(self, p, text, angle=0.0):
        """Draws the text string `text' at point `p' using the current
        truetype font.  The `angle' parameter specifies the angle in radians
        at which to draw the text.

        A bounding rectangle for the text in world coordinates is returned.
        NOTE: The font size is _not_ subject to coordinate transforms!
	"""
	self._check_image()
        self._apply_image()
	if self.m_ttfont is None:
	    raise DrawError, 'You must set a truetype font first.'
        if self.m_color is None:
            color = 0
            bbonly = 1
        else:
            color = self.m_color
            bbonly = 0
	x, y = self.to_device(p)
	rect = self.m_image.stringFT(color, self.m_ttfont.font(),
		    self.m_ttfont.pointsize(), angle, x, y, text, bbonly)
	xform = []
	for i in range(4):
	    xform.append(self.to_world((rect[2*i], rect[2*i+1])))
	return xform

    def fill(self, p, border=None):
	"""Flood fills a part of the image around point `p'.
        
        If `border' is not specified, the area around P of the same color as
        the pixel at P is filled. If border is specified, the area around P
        is filed until a border of color border is encountered.
	"""
	self._check_image()
        self._apply_image()
        if self.m_bgcolor is not None:
            x, y = self.to_device(p)
            if border is None:
                self.m_image.fill(x, y, self.m_bgcolor)
            else:
                self.m_image.fillToBorder(x, y, self.m_bgcolor, border)
