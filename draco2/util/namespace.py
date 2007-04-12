#
# namespace.py: Draco namespaces
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import thread
from draco2.core.exception import DracoError


class NamespaceError(DracoError):
    """Namespace violation."""


class Namespace(object):
    """Base class for all namespaces in Draco.

    Namespaces are (key, value) mappings identical to Python's dictionaries
    but with the restriction that keys must be strings.

    To implement a Namespace, a derived class has to define at least the
    functions __len__, __getitem__, __setitem__, __delitem__ and items().
    All other functins have default implementations in terms of these
    primitives. More methods can be defined as an optimization.
    """

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, name):
        raise NotImplementedError

    def __setitem__(self, name, value):
        raise NotImplementedError

    def __delitem__(self, name):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    def iterkeys(self):
        return iter(self.keys())

    __iter__ = iterkeys

    def items(self):
        return [ (key, self[key]) for key in self.keys() ]

    def iteritems(self):
        return iter(self.items())

    def values(self):
        return [ self[key] for key in self.keys() ]

    def itervalues(self):
        return iter(self.values())

    def has_key(self, name):
        try:
            self[name]
            return 1
        except KeyError:
            return 0

    __contains__ = has_key

    def update(self, ns):
        for key,value in ns.items():
            self[key] = value

    def clear(self):
        for key in self.keys():
            del self[key]

    def get(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            return value

    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    def pop(self, key, value=None):
        try:
            value = self[key]
            del self[key]
        except KeyError:
            if value is None:
                raise
        return value

    def popitem(self):
        try:
            key, value = self.items()[0]
        except IndexError:
            raise KeyError
        del self[key]
        return (key, value)

    def copy(self):
        dict = {}
        for key,value in self.items():
            dict[key] = value
        return dict


class DictNamespace(dict, Namespace):
    """A namespace using a dictionary as its backing store."""


class ReadOnlyNamespace(DictNamespace):
    """Read-only namespace with a dictionary as backing store."""

    def __setitem__(self, name, value):
        raise NamespaceError, 'Read-only namespace'

    def __delitem__(self, name):
        raise NamespaceError, 'Read-only namespace'

    def update(self, data):
        raise NamespaceError, 'Read-only namespace'

    def clear(self):
        raise NamespaceError, 'Read-only namespace'

    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            raise NamespaceError, 'Read-only namespace'

    def pop(self, key, value=None):
        raise NamespaceError, 'Read-only namespace'

    def popitem(self):
        raise NamespaceError, 'Read-only namespace'
