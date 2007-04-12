# vi: ts=8 sts=4 sw=4 et
#
# singleton.py: singleton base class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import threading
import logging

lock = threading.Lock()


def singleton(cls, *args, **kwargs):
    """Create a singleton instance of `object'."""
    try:
        factory = kwargs['factory']
    except KeyError:
        factory = cls
    lock.acquire()
    try:
        # Don't use hasattr(cls, 'instance') as that looks in
        # superclasses breaking inheritance of singletons.
        if not cls.__dict__.has_key('instance'):
            cls.instance = factory(*args)
        if hasattr(cls.instance, '_initialize'):
            cls.instance._initialize()
    finally:
        lock.release()
    return cls.instance
