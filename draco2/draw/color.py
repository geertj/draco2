# vi: ts=8 sts=4 sw=4 et
#
# color.py: color functions
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


def RGBA(r, g, b, a=0):
    """Construct an RGBA value from an RGBA tuple.

    The A argument is optional and defaults to 0 (opaque).
    """
    return gd.trueColorCompose(r, g, b, a)


def xRGBA(color):
    """
    Extract an RGBA tuple from a RGBA value.

    This function always returns a 4-tuple, even if the original
    color had no A value.
    """
    return gd.trueColorExtract(color)
