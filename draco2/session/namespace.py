# vi: ts=8 sts=4 sw=4 et
#
# namespace.py: session namespace
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 222 $

from draco2.util.serialize import dumps, loads
from draco2.util.namespace import DictNamespace, NamespaceError
from draco2.core.model import SessionNamespace as SessionNamespaceObject


class SessionNamespace(DictNamespace):
    """Session namespace.

    A session namespace provides dictionary api access to a data
    store associated with a session. A session can have many namespaces,
    each with a different scope.

    The implementation is load/update/store: when the namespace is
    instantiated, all data in the database is copied. During a request,
    updates and deletes are tracked, and at the end of the request these
    changes are merged (flush()) with the database.
    """

    def __init__(self, session, scope, transaction):
        """Constructor."""
        super(SessionNamespace, self).__init__()
        self.m_session = session
        self.m_scope = scope
        self.m_transaction = transaction
        self.m_dirty = False
        self._load()

    def _load(self):
        """Load data from the database."""
        namespace = SessionNamespaceObject()
        namespace['id'] = self.m_session
        namespace['scope'] = self.m_scope
        namespace['data'] = dumps({})
        # Futher locking is not necessary as the session record has already
        # been locked.
        namespace = self.m_transaction.merge(namespace, lock=False)
        self.m_namespace = namespace
        data = loads(namespace['data'])
        self.update(data)

    def flush(self):
        """Sync data back to the database."""
        if not self.m_dirty:
            return
        self.m_namespace['data'] = dumps(self.copy())

    # Override any method that changes the dictionary and set the dirty
    # flag.

    def __setitem__(self, key, value):
        super(SessionNamespace, self).__setitem__(key, value)
        self.m_dirty = True

    def __delitem__(self, key):
        super(SessionNamespace, self).__delitem__(key)
        self.m_dirty = True

    def update(self, data):
        super(SessionNamespace, self).update(data)
        self.m_dirty = True

    def clear(self):
        super(SessionNamespace, self).clear()
        self.m_dirty = True

    def setdefault(self, key, value=None):
        ret = super(SessionNamespace, self).setdefault(key, value)
        self.m_dirty = True
        return ret

    def pop(self, key, value=None):
        ret = super(SessionNamespace, self).pop(key, value)
        self.m_dirty = True
        return ret

    def popitem(self):
        ret = super(SessionNamespace, self).popitem()
        self.m_dirty = True
        return ret
