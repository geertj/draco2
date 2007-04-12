# vi: ts=8 sts=4 sw=4 et
#
# serialize.py: data serialization
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import cPickle


class Buffer(object):
    """Auxiliary object that can be used to pickle a `buffer'
    instance which is normally not pickle-able.
    """

    def __init__(self, buffer):
        self.string = str(buffer)

    def buffer(self):
        return buffer(self.string)


def dumps(data):
    """Serialize `data'. Returns a string."""
    return cPickle.dumps(data, 2)


def loads(serialized):
    """Load serialized data `serialized'. Returns a Python object."""
    if isinstance(serialized, buffer):
        serialized = str(serialized)
    return cPickle.loads(serialized)
