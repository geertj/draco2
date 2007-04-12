# vi: ts=8 sts=4 sw=4 et
#
# test_namespace.py: namespace tests
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import py.test
from draco2.util.namespace import (Namespace, ReadOnlyNamespace,
                                   DictNamespace, NamespaceError)


class TestAbstract(object):

    namespace = Namespace()

    def test_generic(self):
        ns = self.namespace
        py.test.raises(NotImplementedError, ns.__len__)
        py.test.raises(NotImplementedError, ns.__getitem__, 'key')
        py.test.raises(NotImplementedError, ns.__setitem__, 'key', 'value')
        py.test.raises(NotImplementedError, ns.__delitem__, 'key')
        py.test.raises(NotImplementedError, ns.items)
        py.test.raises(NotImplementedError, ns.iteritems)
        py.test.raises(NotImplementedError, ns.keys)
        py.test.raises(NotImplementedError, ns.iterkeys)
        py.test.raises(NotImplementedError, ns.__iter__)
        py.test.raises(NotImplementedError, ns.values)
        py.test.raises(NotImplementedError, ns.itervalues)
        py.test.raises(NotImplementedError, ns.has_key, 'key')
        py.test.raises(NotImplementedError, ns.__contains__, 'key')
        py.test.raises(NotImplementedError, ns.update, {1: 1})
        py.test.raises(NotImplementedError, ns.get, 'key')
        py.test.raises(NotImplementedError, ns.setdefault, 'key')
        py.test.raises(NotImplementedError, ns.pop, 'key')
        py.test.raises(NotImplementedError, ns.popitem)
        py.test.raises(NotImplementedError, ns.copy)


class TestReadOnly(object):

    namespace = ReadOnlyNamespace({'key1': 'value1'})

    def test_readonly(self):
        ns = self.namespace
        assert len(ns) == 1
        assert ns.get('key1') == 'value1'
        assert ns.get('key2') == None
        py.test.raises(NamespaceError, ns.__setitem__, 'key2', 'value2')
        py.test.raises(NamespaceError, ns.__delitem__, 'key2')
        py.test.raises(KeyError, ns.__getitem__, 'key2')
        assert ns.items() == [('key1', 'value1')]
        items = [ it for it in ns.iteritems() ]
        assert items == [('key1', 'value1')]
        assert ns.keys() == ['key1']
        keys = [ ke for ke in ns.iterkeys() ]
        assert keys == ['key1']
        keys = [ el for el in ns.__iter__() ]
        assert keys == ['key1']
        assert ns.values() == ['value1']
        values = [ va for va in ns.itervalues() ]
        assert values == ['value1']
        assert ns.has_key('key1')
        assert not ns.has_key('key2')
        assert 'key1' in ns
        assert 'key2' not in ns
        py.test.raises(NamespaceError, ns.update, {'key2': 'value2'})
        assert not ns.has_key('key2')
        assert ns.setdefault('key1', 'value2') == 'value1'
        py.test.raises(NamespaceError, ns.setdefault, 'key2')
        assert not ns.has_key('key2')
        py.test.raises(NamespaceError, ns.pop,'key1')
        assert ns.has_key('key1')
        py.test.raises(NamespaceError, ns.popitem)
        assert ns.has_key('key1')
        ns1 = ns.copy()
        assert ns.items() == ns1.items()


class TestDict(object):

    namespace = DictNamespace()

    def test_read_write(self):
        ns = self.namespace
        ns['key1'] = 'value1'
        assert len(ns) == 1
        assert ns.get('key1') == 'value1'
        assert ns.get('key2') == None
        ns['key2'] = 'value2'
        assert ns['key2'] == 'value2'
        del ns['key2']
        py.test.raises(KeyError, ns.__getitem__, 'key2')
        assert ns.items() == [('key1', 'value1')]
        items = [ it for it in ns.iteritems() ]
        assert items == [('key1', 'value1')]
        assert ns.keys() == ['key1']
        keys = [ ke for ke in ns.iterkeys() ]
        assert keys == ['key1']
        keys = [ el for el in ns.__iter__() ]
        assert keys == ['key1']
        assert ns.values() == ['value1']
        values = [ va for va in ns.itervalues() ]
        assert values == ['value1']
        assert ns.has_key('key1')
        assert not ns.has_key('key2')
        assert 'key1' in ns
        assert 'key2' not in ns
        ns.update({'key2': 'value2'})
        assert ns['key2'] == 'value2'
        assert ns.setdefault('key2', 'value3') == 'value2'
        assert ns.setdefault('key3', 'value3') == 'value3'
        assert ns.has_key('key3')
        assert ns.pop('key3') == 'value3'
        assert not ns.has_key('key3')
        assert ns.popitem() in [('key1', 'value1'), ('key2', 'value2')]
        assert len(ns) == 1
        ns1 = ns.copy()
        assert ns.items() == ns1.items()
