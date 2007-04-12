# vi: ts=8 sts=4 sw=4 et
#
# codec.py: managing codecs
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import codecs
from draco2.util.codec import search_codec


def init_codecs(options):
    codecs.register(search_codec)
