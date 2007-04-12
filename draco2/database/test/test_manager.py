# vi: ts=8 sts=4 sw=4 et
#
# test_manager.py: dabase manager tests
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.database.test.support import DatabaseTest


class TestManager(DatabaseTest):

    def test_connection(self):
        database = self.database
        c1 = database.connection()
        c2 = database.connection()
        assert c1 is not c2
        c3 = database.connection('Test')
        assert c1 is not c3
        assert c2 is not c3
        c4 = database.connection('Test')
        assert c3 is c4
