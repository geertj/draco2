# vi: ts=8 sts=4 sw=4 et
#
# image.py: Image class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os.path
import gd

from draco2.draw.color import RGBA, xRGBA
from draco2.draw.exception import *


class Image(object):
    """The Image object.

    An Image object contains the actual low-level image object (gdImage),
    methods for loading/saving and color management. To paint to the image
    you have to use the Painter object.
    """

    formats = ['jpeg', 'png', 'gif', 'gd', 'gd2', 'wbmp', 'xbm', 'xpm']
    content_types = { 'image/jpeg': 'jpeg', 'image/pjpeg': 'jpeg',
                      'image/x-png': 'png', 'image/png': 'png',
                      'image/gif': 'gif' }
    extensions = { 'jpg': 'jpeg', }

    def __init__(self, image):
	"""Create a new image out of a lowlevel gd.Image instance.
        
        You should not use this contructor yourself, instead use one of the
        alternate constructors below.
	"""
	self.m_image = image

    @classmethod
    def new(cls, width, height, truecolor=1):
	"""Create a new image of resolution `width' times `height' pixels
	and of color mode `truecolor'.
	"""
	image = gd.createImage(width, height, truecolor)
	return cls(image)

    @classmethod
    def load(cls, input, format=None):
	"""Loads and return an image from a file.
        
        The `file' parameter can be a file name or a file like object. If
        the file format cannot be deduced from a file name, you have to
        supply the `format' keyword argument.  Currently, the formats "png",
        "gif", "jpeg", "gd", "gd2", "wbmp", "xbm" and "xpm" are supported.
	"""
        if hasattr(input, 'read'):
	    input = gd.createStream(input)
            stream = True
        elif type(input) is str:
            fin = file(input, 'rb')
            input = gd.createStream(fin)
            stream = False
        else:
	    raise TypeError, 'Expecting a file name or a file like object.'
        if format is None:
            if stream:
                raise ValueError, 'No format or file name specified.'
            else:
                basename, ext = os.path.splitext(input)
                ext = ext.lower()
                format = cls.extensions.get(ext, ext)
        elif format in cls.content_types:
            format = cls.content_types[format]
        if format not in cls.formats:
            raise DrawError, 'Unsupported format: %s' % format
        try:
            image = gd.loadImage(input, format)
        except ValueError, err:
            raise DrawError, str(err)
        if not stream:
            fin.close()
	return cls(image)

    def save(self, output, format=None, **kwargs):
	"""Save the image to a file.
        
        The `file' parameter can be a file name or a file-like object. If
        the file format cannot be deduced from a file name, you have to
        supply the `format' keyword argument.
	"""
        if hasattr(output, 'write'):
	    if format is None:
		raise ValueError, 'No format specified.'
            output = gd.createStream(output)
            stream = True
        elif isinstance(output, str):
            if format is None:
                basename, ext = os.path.splitext(output)
                format = self._extmap.get(ext, ext)
            fout = file(output, 'wb')
            output = gd.createStream(fout)
            stream = False
        else:
            raise TypeError, 'Expecting a file name or a file like object.'
	if format == 'jpeg' and kwargs.has_key('quality'):
	    args += (kwargs['quality'],)
        else:
            args = ()
        if not stream:
            fout.close()
        self.m_image.save(output, format, *args)

    def copy(self):
	"""Return a copy of the image object."""
	new = Image.create(self.width(), self.height(), truecolor=self.truecolor())
	new._image().copy(self._image(), 0, 0, 0, 0, self.width(), self.height())
	return new

    def resize(self, width, height, smooth=1):
	"""Resize the image to `width' times `height' pixels.
        
        If `smooth' is nonzero, the image is smoothly interpolated.
	"""
	new = gd.createImage(width, height, self.truecolor())
	if not self.truecolor() and self.transparent() != -1:
	    r, g, b, a = xRGBA(self.get_color(self.transparent()))
	    trans = new.colorAllocate(r, g, b, a)
	    new.colorTransparent(trans)
	    new.rectangle(0, 0, width, height, trans, 1)
	new.copy(self.m_image, 0, 0, 0, 0, width, height, self.width(),
		 self.height(), smooth)
	self.m_image = new

    def crop(self, p, width, height):
        """Crop the image starting at upper left point `p' and width `w',
        height `h'.
        """
        new = gd.createImage(width, height, self.truecolor())
	if not self.truecolor() and self.transparent() != -1:
	    r, g, b, a = xRGBA(self.get_color(self.transparent()))
	    trans = new.colorAllocate(r, g, b, a)
	    new.colorTransparent(trans)
	    new.rectangle(0, 0, width, height, trans, 1)
	new.copy(self.m_image, 0, 0, p[0], p[1], width, height)
	self.m_image = new

    def convert_palette(self, ncolors, dither=1):
	"""Convert a truecolor image to indexed color with at most `ncolors'
	colors.
        
        If `dither' is nonzero, the image will be dithered.
	"""
	if not self.truecolor():
	    return
	self.m_image.trueColorToPalette(dither, ncolors)

    def convert_truecolor(self, bgcolor=None):
	"""Convert an indexed color image to a truecolor one.
        
        If the indexed color image has a transparent background, it is kept
        by default.  But because there is poor support amongst web browsers
        for truecolor images with transparency, the `bgcolor' parameter
        allows you to override the background color.
	"""
	if self.truecolor():
	    return
	new = gd.createImage(self.width(), self.height(), 1)
	if bgcolor is None:
	    if self.transparent() != -1:
		r, g, b, a = xRGBA(self.get_color(self.transparent()))
		bgcolor = RGBA(r, g, b, gd.AlphaTransparent)
	if bgcolor:
	    new.rectangle(0, 0, self.width(), self.height(), bgcolor, 1)
	new.copy(self.m_image, 0, 0, 0, 0, self.width(), self.height())
	self.m_image = new

    def _image(self):
	"""Return the low-level gdImage object."""
	return self.m_image


    # GET ATTRIBUTES

    def width(self):
	"""Returns the pixel width of the image."""
	return self.m_image.width

    def height(self):
	"""Returns the pixel height of the image."""
	return self.m_image.height
	
    def truecolor(self):
	"""Returns nonzero if the image is a truecolor image."""
	return self.m_image.truecolor

    def colors(self):
	"""If this in an indexed color image, return the number of colors 
	allocated in the color table. For a truecolor image the results
	of this method are undefined.
	"""
	if self.truecolor():
	    return 0
	else:
	    return self.m_image.colors

    def interlace(self):
	"""Returns nonzero if the image is interlaced, zero otherwise."""
	return self.m_image.interlace

    def transparent(self):
	"""If this is an indexed color image, return the index of the
	transparent color, or -1 if no transparent color has been set.
	For a truecolor image, this returns a fully transparent RGBA value.
	"""
	if self.truecolor():
	    return RGBA(0, 0, 0, gd.AlphaTransparent)
	else:
	    return self.m_image.transparent

    # COLOR MANAGEMENT ...

    def new_color(self, r, g, b, a=0):
        """If this is an indexed color image, allocate a new palette entry
        for the specified color and return its index. If no color can be
        allocated because the color table is full, -1 is returned. For a
        truecolor image this method is always successfull and returns the
        RGBA value for the given color.
	"""
	return self.m_image.colorAllocate(r, g, b, a)

    def get_color(self, color):
        """Indexed color: Return the color RGBA value of the palette entry
        `color'.  For a truecolor image this is a no-op and it simply
        returns `color'.
	"""
	return self.m_image.colorGet(color)

    def free_color(self, color):
        """For an indexed color image, this deallocates an entry from the
        palette. For a truecolor this method is a no-op.
	"""
	self.m_image.colorDeallocate(color)

    def find_color(self, r, g, b, a=0):
        """Indexed color: Look up the specified color in the image palette
        and return its index. If the color is not found, -1 is returned.
        For a truecolor image this method is always successfull and returns
        the RGBA value for the given color.
	"""
	return self.m_image.colorExact(r, g, b, a)

    def closest_color(self, r, g, b, a=0, metric='rgb'):
        """Indexed color: Find the color closest to the specified color in
        the image palette and return its index. The metric that determines
        closeness can be specified by the optional `metric' parameter. The
        default metric is "rgb" but "hwb" is also supported. These values
        correspond to the euclidian distance in the RGB and HWB color spaces
        respectively. If no colors have yet been allocated, -1 is returned.
        For a truecolor image this method is always successfull and returns
        the RGBA value for the given color.
	"""
	if metric == 'rgb':
	    return self.m_image.colorClosest(r, g, b, a)
	elif metric == 'hwb':
	    return self.m_image.colorClosestHWB(r, g, b)
	else:
	    raise DrawError, 'Unsupported metric.'

    def resolve_color(self, r, g, b, a=0):
        """Indexed color: Check if the specified color exists in the image
        palette. If it exists, its index is returned. If not, and there is
        room in the palette, a new color is allocated and its index is
        returned. If there's no room, the closest color is returned. Hence,
        this function always return a valid color index.  For a truecolor
        image this method simply returns the RGBA value for the given color.
	"""
	return self.m_image.colorResolve(r, g, b, a)

    def set_transparent(self, color):
        """Indexed color: Set the transparent color index to `color'. For a
        truecolor image this method is a no-op.
	"""
	self.m_image.colorTransparent(color)

    def set_savealpha(self, save):
        """Set or clear the save-alpha flag for the image. If `save' is
        nonzero, alpha channel information is included when the image is
        saved. This requires an output format that support this.
	"""
	self.m_image.saveAlpha(save)
