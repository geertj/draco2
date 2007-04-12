# vi: ts=8 sts=4 sw=4 et
#
# image.py: detect image size
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import struct


def get_image_info(fname):
    """Determine the image type and size of `fname'.
    
    The return value is a 3-tuple: format, width, height; or None
    if the image is not found or the size cannot be determined.
    """
    try:
        fin = file(fname, 'rb')
    except IOError:
        return
    head = fin.read(24)
    if len(head) != 24:
        return
    if head[:4] == '\x89PNG' and head[4:8] == '\r\n\x1a\n':
        # PNG
        w, h = struct.unpack('>ii', head[16:24])
        fmt = 'png'
    elif head[:6] in ('GIF87a', 'GIF89a'):
        # GIF
        w, h = struct.unpack('<HH', head[6:10])
        fmt = 'gif'
    elif head[:4] == '\xff\xd8\xff\xe0' and head[6:10] == 'JFIF':
        # JPEG
        try:
            fin.seek(0)  # Read 0xff next
            size = 2
            type = 0
            while not 0xc0 <= type <= 0xcf:
                fin.seek(size, 1)
                b = fin.read(1)
                while ord(b) == 0xff: 
                    b = fin.read(1)
                type = ord(b)
                size = struct.unpack('>H', fin.read(2))[0] - 2
            # We are at a SOFn block
            fin.seek(1, 1)  # Skip `precision' byte.
            h, w = struct.unpack('>HH', fin.read(4))
            fmt = 'jpeg'
        except (IOError, struct.error):
            return
    else:
        return
    return fmt, w, h
