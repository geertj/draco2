# vi: ts=8 sts=4 sw=4 et
#
# transaction.py: defines the Transaction class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import time
import logging
import random

from draco2.util.serialize import Buffer
from draco2.database import DatabaseDBAPIError
from draco2.model.exception import *
from draco2.model.object import Object
from draco2.model.entity import Entity
from draco2.model.relationship import Relationship
from draco2.model.obcache import ObjectCache


class Transaction(object):
    """All objects in a Draco model are part of a transaction.

    A transaction is the only way to query, insert and delete
    objects in a database.
    """

    finalization_policies = set(('ROLLBACK', 'COMMIT'))

    def __init__(self, model):
        """Create a new transaction for `model'."""
        self.m_model = model
        self.m_connection = None
        self.m_obcache = ObjectCache()
        self.m_retry = True
        self.set_isolation_level('SERIALIZABLE')
        self.set_finalization_policy('ROLLBACK')

    def _finalize(self):
        """Finalize the transaction."""
        if self.m_finalization_policy == 'COMMIT':
            self.commit()
        elif self.m_finalization_policy == 'ROLLBACK':
            self.rollback()

    def model(self):
        """Return the model this transaction belongs to."""
        return self.m_model

    def _connect(self):
        """Connect to the database."""
        database = self.m_model.database()
        connection = database.connection()
        self.m_connection = connection

    def cursor(self):
        """Return a new cursor."""
        if self.m_connection is None:
            self._connect()
        return self.m_connection.cursor()

    def set_isolation_level(self, level):
        """Set the transaction isolation level."""
        if self.m_connection is None:
            self._connect()
        database = self.model().database()
        database.set_isolation_level(self.m_connection, level)

    def set_finalization_policy(self, policy):
        """Set the transaction finalization policy to 'policy'.

        The finalization policy can be either 'ROLLBACK' (the default)
        or 'COMMIT'.
        """
        if policy.upper() not in self.finalization_policies:
            m = 'Illegal finalization policy: %s'
            raise ValueError, m % policy
        self.m_finalization_policy = policy.upper()

    def _what_clause(self, typ, alias, attrs, extra_attrs):
        """Return a what clause (SELECT ....) selecting the attributes
        selected by `attrs' of object `typ'.
        """
        if not typ.attributes:
            columns = [ '*' ]
        elif attrs is None:
            # This includes the primary keys.
            columns = [ at.name for at in typ.attributes ]
            columns = [ '%s.%s' % (alias, col) for col in columns ]
        else:
            # Add primary keys explicitly.
            columns = [ at.name for at in typ.primary_key ]
            columns += [ at for at in attrs if at not in columns ]
            columns = [ '%s.%s' % (alias, col) for col in columns ]
        if extra_attrs:
            columns += extra_attrs
        return ','.join(columns)

    def _what_alias(self, desc):
        """Return the alias to use in the what clause."""
        if isinstance(desc, type) and issubclass(desc, Object):
            return desc.name
        while True:
            desc, rolename, rel, kind = desc
            if isinstance(desc, type) and issubclass(desc, Object):
                return rolename

    def _join_condition(self, rolename, rel):
        """Return a join condition (ON ....), joining the relationship
        table `rel' to the entity table of its `role' role.
        """
        role = rel._get_role(rolename)
        name,ent,card,fk = role
        assert len(fk) == len(ent.primary_key)
        cond = []
        for fkat,pkat in zip(fk, ent.primary_key):
            cond.append('%s.%s = %s.%s' %
                        (rel.name, fkat.name, rolename, pkat.name))
        cond = ' AND '.join(cond)
        return cond

    def _from_clause(self, desc):
        """Return a from clause (FROM ....), specified by desc.

        The `desc' parameter may be a single entity, or a tuple of
        (desc, rolename, relationship, kind).
        """
        if isinstance(desc, type) and issubclass(desc, Object):
            return desc.name
        desc, rolename, rel, kind = desc
        t1 = self._from_clause(desc)
        if isinstance(desc, type) and issubclass(desc, Object):
            t1 = '%s AS %s' % (t1, rolename)
        t2 = rel.name
        cond = self._join_condition(rolename, rel)
        clause = '%s %s JOIN %s ON %s' % (t1, kind, t2, cond)
        for role in rel.roles:
            if role[0] == rolename:
                continue
            name,ent,card,fks = role
            t2 = ent.name
            cond = self._join_condition(name, rel)
            clause += ' %s JOIN %s AS %s ON %s' % (kind, t2, name, cond)
        clause = '(%s)' % clause
        return clause

    def _select(self, typ, query, args, lock=False):
        """Do a low-level select query."""
        result = []
        cursor = self.cursor()
        self.retry(cursor.execute, query, args)
        pkcols = [ at.name for at in typ.primary_key ]  # can be empty
        columns = [ de[0] for de in cursor.description ]
        while True:
            row = cursor.fetchone()
            if not row:
                break
            if pkcols:
                # The object cache is used to guarantee that no two
                # python objects point to the same database object.
                try:
                    pk = [ row[columns.index(pk)] for pk in pkcols ]
                except ValueError:
                    raise ModelInternalError, 'Query did not return primary key.'
                obj = self.m_obcache.select(typ, pk)
            else:
                obj = None
            if obj is None:
                obj = typ()
                obj._set_transaction(self)
                obj._select(row, cursor.description, lock)
            if pkcols:
                self.m_obcache.insert(obj)
            result.append(obj)
        return result

    def count(self, typ, where=None, args=None, join=None):
        """Select the number of objects that match a certain query.

        This function mimics the SQL SELECT COUNT(*) construct.
        """
        if isinstance(typ, basestring):
            typ = self.model().object(typ)
        elif not issubclass(typ, Object):
            raise TypeError, 'Expecting `Object\' subclass or object name.'
        if join is None:
            join = typ
        alias = self._what_alias(join)
        query = 'SELECT COUNT(*) '
        query += 'FROM %s ' % self._from_clause(join)
        if where is not None:
            query += ' WHERE %s' % where
        cursor = self.cursor()
        self.retry(cursor.execute, query, args)
        row = cursor.fetchone()
        assert row is not None
        return row[0]

    def select(self, typ, where=None, args=None, order=None, offset=None,
               limit=None, join=None, lock=False, attrs=None, extra_attrs=None):
        """Select an object from the current transaction.

        The keyword interface mimics the SQL SELECT command.
        """
        if isinstance(typ, basestring):
            typ = self.model().object(typ)
        elif not issubclass(typ, Object):
            raise TypeError, 'Expecting `Object\' subclass or object name.'
        if join is None:
            join = typ
        alias = self._what_alias(join)
        query = 'SELECT %s ' % self._what_clause(typ, alias, attrs, extra_attrs)
        query += 'FROM %s ' % self._from_clause(join)
        if where is not None:
            query += ' WHERE %s' % where
        if order is not None:
            query += ' ORDER BY %s ' % order
        if offset is not None:
            query += ' OFFSET %d' % offset
        if limit is not None:
            query += ' LIMIT %d' % limit
        if lock:
            query += ' FOR UPDATE'
        results = self._select(typ, query, args, lock)
        return results

    def insert(self, obj):
        """Insert an object in the transaction.

        The object must be a new object, i.e. it must not have been
        selected from or inserted into any transaction before.
        """
        obj._set_transaction(self)
        obj._insert()
        self.m_obcache.insert(obj)

    def _merge(self, obj, func, lock):
        """Internal helper function for merge()."""
        pkcond = obj._primary_key_condition()
        pkval = obj._primary_key()
        database = self.model().database()
        result = self.select(type(obj), pkcond, pkval, lock=lock)
        if result:
            assert len(result) == 1
            ret = result[0]
            if func is not None:
                func(ret, obj)
        else:
            try:
                self.insert(obj)
            except DatabaseDBAPIError, err:
                if database.is_primary_key_error(err):
                    raise database.serialization_error()
                raise
            ret = obj
        ret._merge(func)
        return ret

    def merge(self, obj, func=None, lock=False):
        """Merge is a special kind of insert that merges data using a merge
        function in case an object with the same primary key already exists.

        When this method returns, an object with the primary key of `obj' is
        guaranteed to exist in the transaction. A reference to that object
        is returned. Note that this reference may be different from `obj' in
        case an object was already present.
        """
        for val in obj._primary_key():
            if val is None:
                raise ModelInterfaceError, 'Primary key value not provided.'
        ret = self.retry(self._merge, obj, func, lock)
        return ret

    def delete(self, obj):
        """Delete an object from the transaction.

        The object must be part of the current transaction.
        """
        if obj.transaction() is not self:
            raise ModelInterfaceError, 'Object is not part of this transaction.'
        obj._delete()
        # This does not actually delete the object from the cache, but
        # removes relationships that reference it. See the comments in
        # obcache.py.
        self.m_obcache.delete(obj)

    def entity(self, typ, pk):
        """Return an entity by its primary key."""
        result = self.select(typ, typ._primary_key_condition(), pk)
        if not result:
            raise ModelInterfaceError, 'Object does not exist.'
        assert len(result) == 1
        return result[0]

    def retry(self, func, *args):
        """Execute a query, with logic that retries failed transactions
        due to serializability errors."""
        # Do not retry nested functions
        if not self.m_retry:
            return func(*args)
        self.m_retry = False
        logger = logging.getLogger('draco2.model.transaction')
        database = self.model().database()
        generator = random.SystemRandom()
        # Try 10 times with a delay of up to 0.4 seconds
        for i in range(10):
            if i > 0:
                logger.info('Replaying aborted transaction.')
                time.sleep(0.4 * generator.random())
                try:
                    self._rebuild()
                except DatabaseDBAPIError, err:
                    if database.is_serialization_error(err) and i != 9:
                        continue  # try again
                    raise
            try:
                ret = func(*args)
            except DatabaseDBAPIError, err:
                if database.is_serialization_error(err) and i != 9:
                    continue
                raise
            else:
                break
        self.m_retry = True
        return ret

    def _rebuild(self):
        """Rebuild the transaction.

        This function may be called when a serialization error has occurred.
        It will re-build the database state in a new SQL level transaction.
        """
        self.m_connection.rollback()
        # Entities first, then relationships. Relationships may depend
        # on entities.
        objects = self.m_obcache.values()
        for ob in objects:
            ob._rebuild()

    def commit(self):
        """Commit the transaction."""
        # don't use iterator: _validate() may change transaction
        for ob in self.m_obcache.values():
            ob._validate()
        for ob in self.m_obcache:
            ob._commit()
        self.m_connection.commit()

    def rollback(self):
        """Rollback the transaction."""
        for ob in self.m_obcache:
            ob._rollback()
        self.m_obcache.clear()
        self.m_connection.rollback()

    def _dump_dict(self, dict):
        """Helper for .dump()."""
        for key,value in dict.items():
            if isinstance(value, buffer):
                dict[key] = Buffer(value)
        return dict

    def _load_dict(self, dict):
        """Helper for .load()."""
        for key,value in dict.items():
            if isinstance(value, Buffer):
                dict[key] = value.buffer()
        return dict

    def dump(self):
        """Serialize the current transaction."""
        data = []
        objects = self.m_obcache.values()
        for ob in objects:
            if ob._state() in (ob.INSERTED, ob.SELECTED, ob.UPDATED,
                              ob.DELETED):
                entry = (ob.name, ob._state(), ob._primary_key(),
                         self._dump_dict(ob.copy()))
                data.append(entry)
        return data

    def load(self, data):
        """Load the current transaction from a previous dump."""
        model = self.model()
        for name,state,pk,items in data:
            cls = model.object(name)
            if not cls:
                raise ModelInterfaceError, 'Unknown object %s' % name
            items = self._load_dict(items.copy())
            if state == cls.INSERTED:
                result = self.select(cls, cls._primary_key_condition(), pk)
                if result:
                    # Loading the same object twice: ok, but update
                    assert len(result) == 1
                    obj = result[0]
                    obj.update(items)
                else:
                    obj = cls()
                    obj.update(items)
                    self.insert(obj)
            elif state in (cls.SELECTED, cls.UPDATED):
                result = self.select(cls, cls._primary_key_condition(), pk)
                if result:
                    assert len(result) == 1
                    obj = result[0]
                    obj.update(items)
                else:
                    # Re-create object if it was deleted.
                    obj = cls()
                    obj.update(items)
                    self.insert(obj)
            elif state == cls.DELETED:
                result = self.select(cls, cls._primary_key_condition(), pk)
                if result:
                    assert len(result) == 1
                    obj = result[0]
                    self.delete(obj)
                else:
                    # Allow other transaction to delete this object.
                    pass

    def extract_messages(self):
        """Extract messages for translation.

        The return value is a list of (message, context, name) tuples. Only
        objects that have been modified in this transaction are included.
        """
        messages = []
        for obj in self.m_obcache:
            for att in obj.attributes:
                if not att.translate:
                    continue
                message = obj[att.name]
                if not message:
                    continue
                if att.translate_byname:
                    name = '%s.%s' % (obj._object_id(), att.name)
                    context = None
                else:
                    name = None
                    context = att.translation_context
                messages.append((message, context, name))
        return messages
