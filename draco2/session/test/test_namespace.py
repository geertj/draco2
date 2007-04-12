# vi: ts=8 sts=4 sw=4 et
#
# test_namespace.py: database namespace tests
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import random
import datetime
import py.test

from draco2.core.model import DracoModel
from draco2.session.namespace import SessionNamespace, NamespaceError
from draco2.database.test.support import DatabaseTest, random_data


class OldStyleClass:
    a = 10
    def __init__(self):
        self.b = 20
    def __eq__(self, other):
        return type(self) is type(other) and self.a == other.a \
                    and self.b == other.b


class NewStyleClass(object):
    a = 30
    def __init__(self):
        self.b = 40
    def __eq__(self, other):
        return type(self) is type(other) and self.a == other.a \
                    and self.b == other.b


class TestNamespace(DatabaseTest):

    def setup_method(self, method):
        super(TestNamespace, self).setup_method(method)
        self.model = DracoModel(self.database)
        self.schema = self.model.schema()
        self.schema.drop()
        self.schema.create()
        self.transaction = self.model.transaction()
        self.namespace = SessionNamespace('sessionid', 'myscope',
                                          self.transaction)

    def teardown_method(self, method):
        self.transaction.commit()
        self.schema.drop()
        super(TestNamespace, self).teardown_method(method)

    def test_simple(self):
        ns = self.namespace
        ns['key'] = 'value'
        ns.flush(); ns._load()
        assert ns['key'] == 'value'
 
    def test_types(self):
        ns = self.namespace
        data = []
        data.append(None)
        data.append(True)
        data.append(False)
        data.append(10)
        data.append(1000000000000000000L)
        data.append(3.1415)
        data.append('value')
        data.append((1,2,3))
        data.append([1,2,3])
        data.append({1:2, 3:4})
        data.append(datetime.timedelta())
        data.append(datetime.date.today())
        data.append(datetime.datetime.now())
        data.append(datetime.time())
        data.append(OldStyleClass())
        data.append(NewStyleClass())
        for i,val in enumerate(data):
            ns['key_%d' % i] = val
        ns.flush(); ns._load()
        for i,val in enumerate(data):
            assert ns['key_%d' % i] == val

    def test_binary(self):
        ns = self.namespace
        data = []
        for i in range(10):
            blob = random_data(random.randrange(100000))
            data.append(blob)
        for i,val in enumerate(data):
            ns['key_%d' % i] = val
        ns.flush(); ns._load()
        for i,val in enumerate(data):
            assert ns['key_%d' % i] == val
