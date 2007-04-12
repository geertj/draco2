# vi: ts=8 sts=4 sw=4 et
#
# support.py: test support for draco2.draw
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import os
import tempfile


class DracoDrawTest(object):
    """Base class for draco2.draw tests."""

    def setup_method(cls, method):
        cls.files = []

    def tempfile(self, mode='r'):
        fd, name = tempfile.mkstemp()
        fobj = file(name, mode)
        os.close(fd)
        self.files.append(name)
        return fobj

    def teardown_method(cls, method):
        for name in cls.files:
            try:
                os.unlink(name)
            except OSError:
                pass
