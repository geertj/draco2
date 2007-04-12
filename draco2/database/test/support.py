# vi: ts=8 sts=4 sw=4 et
#
# support.py: test support for draco2.database
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import string
import random

from draco2.core.config import Config
from draco2.core.api import API
from draco2.database import DatabaseManager

api = API()
api.config = Config()
api.config.add_file(os.environ['TESTCONFIG'])
database = DatabaseManager._create(api)


class DatabaseTest(object):
    """Base class for database tests."""

    def setup_method(self, method):
        self.database = database
        self.dialect = self.database.dialect()
        self.dbapi = self.database.dbapi()
        self.connection = self.database.connection()
        self.cursor = self.connection.cursor()

    def teardown_method(self, method):
        self.database._finalize()


def random_data(size):
    """Generate a random string of `size' arbitrary bytes."""
    try:
        # Firsty try /dev/urandom as that's much faster.
        fin = file('/dev/urandom')
        buf = fin.read(size)
        fin.close()
        return buf
    except IOError:
        pass
    gen = random.SystemRandom()
    l = []
    for i in range(size):
        l.append(chr(gen.randrange(256)))
    return ''.join(l)


def random_string(size):
    """Generate a random string of `size' printable characters."""
    data = random_data(size)
    alphabet = string.lowercase + string.uppercase + string.digits
    table = ((256 // len(alphabet) + 1) * alphabet)[:256]
    data = data.translate(table)
    return data
