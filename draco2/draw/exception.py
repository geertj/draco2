# vi: ts=8 sts=4 sw=4 et
#
# exception.py: exceptions for draco2.draw
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2 import DracoError


class DrawError(DracoError):
    """Drawing related error."""
