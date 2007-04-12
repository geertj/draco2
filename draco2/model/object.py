# vi: ts=8 sts=4 sw=4 et
#
# object.py: defines the `Object' class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.model.exception import *
from draco2.util.namespace import Namespace


class Object(Namespace):
    """Base class for entities and relationships."""

    name = None
    primary_key = None
    attributes = None
    indexes = []

    # States for a database object
    FREE = 0  # Object not associated with any transaction
    ASSOCIATED = 1  # Object associated with a transaction but not in db
    INSERTED = 2  # Object is in the db and was created from this instance.
    SELECTED = 3  # Object is in the db but was previously created.
    UPDATED = 4  # Object was previously created and has now been updated.
    MERGED = 5  # The object's attributes are the result of a merge.
    DELETED = 6  # Object was previously created and has not been deleted.
    ORPHAN = 7  # Object's transaction does not exist anymore.

    c_pkcond = None

    def __init__(self, **kwargs):
        """Create a new database object."""
        self.m_state = self.FREE
        self.m_merge = None
        self.m_locked = False
        self.m_transaction = None
        self.m_attributes = {}
        for at in self.attributes:
            attr = at(self)
            self.m_attributes[attr.name] = attr
        self.m_pktuple = None
        self.m_extradata = {}
        self.update(kwargs)

    def _state(self):
        """Return the state of the object."""
        return self.m_state

    def _set_state(self, state):
        """Set the state of the object."""
        self.m_state = state

    def _locked(self):
        """Return True if the object is locked."""
        return self.m_locked

    def _set_locked(self, locked):
        """Set the locking state of the object."""
        self.m_locked = locked

    def transaction(self):
        """Return the transaction this object is part of."""
        return self.m_transaction

    def _set_transaction(self, transaction):
        """Set the transaction for the current object."""
        if self._state() != self.FREE \
                    and transaction is not self.m_transaction:
            raise ModelInterfaceError, 'A transaction is already associated.'
        self.m_transaction = transaction
        self.m_state = self.ASSOCIATED

    def _primary_key(self):
        """Return the primary key values as a tuple."""
        if self.m_pktuple:
            return self.m_pktuple
        values = []
        for at in self.primary_key:
            attr = self.m_attributes[at.name]
            values.append(attr.value())
        self.m_pktuple = tuple(values)
        return self.m_pktuple

    def _object_id(self):
        """Return a unique object identified for this object."""
        pk = self._primary_key()
        if None in pk:
            return None
        pks = '.'.join(map(str, pk))
        name = '%s.%s' % (self.name, pks)
        return name

    @classmethod
    def _primary_key_condition(cls):
        """Return a condition that selects the object's primary key."""
        if cls.c_pkcond:
            return cls.c_pkcond
        values = []
        for at in cls.primary_key:
            values.append('%s=%%s' % at.name)
        cls.c_pkcond = ' AND '.join(values)
        return cls.c_pkcond

    def _attributes(self):
        """Return the list of attributes."""
        return self.m_attributes

    def _select(self, row, description, locked=False):
        """Load values from a query result."""
        if self._state() != self.ASSOCIATED:
            raise ModelInterfaceError, 'No transaction associated.'
        names = [ de[0] for de in description ]
        for at in self.m_attributes.values():
            if at.name in names:
                value = row[names.index(at.name)]
                at.set_value(value)
            elif type(at) in self.primary_key:
                raise ModelInterfaceError, 'Primary key value not provided.'
            else:
                at._lazy = True
        self.m_extradata = dict(zip(names, row))
        self._set_state(self.SELECTED)
        self._set_locked(locked)

    def _insert(self):
        """Add the object to a transaction."""
        if self._state() != self.ASSOCIATED:
            raise ModelInterfaceError, 'No transaction associated.'
        transaction = self.transaction()
        cursor = transaction.cursor()
        self.pre_insert()
        columns = []
        values = []
        for at in self.m_attributes.values():
            if at.isnull():
                continue
            columns.append(at.name)
            values.append(at.value())
        query = 'INSERT INTO %s' % self.name
        query += ' (%s)' % ','.join(columns)
        query += ' VALUES (%s)' % ','.join(['%s'] * len(columns))
        transaction.retry(cursor.execute, query, values)
        self._set_state(self.INSERTED)
        self.post_insert()

    def _merge(self, func):
        if self._state() not in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED):
            raise ModelInterfaceError, 'Object does not exist in transaction.'
        self.m_merge = func
        self._set_state(self.MERGED)

    def _delete(self):
        """Delete the object."""
        if self._state() not in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED):
            raise ModelInterfaceError, 'Object does not exist.'
        transaction = self.transaction()
        cursor = transaction.cursor()
        self.pre_delete()
        query = 'DELETE FROM %s' % self.name
        pkval = self._primary_key()
        pkcond = self._primary_key_condition()
        query += ' WHERE %s' % pkcond
        transaction.retry(cursor.execute, query, pkval)
        self._set_state(self.DELETED)
        self.post_delete()

    def lock(self):
        """Lock the object. Commit the transaction to unlock."""
        transaction = self.transaction()
        cursor = transaction.cursor()
        pkat = ','.join([ at.name for at in self.primary_key ])
        query = 'SELECT %s' % pkat
        query += ' FROM %s' % self.name
        query += ' WHERE %s' % self._primary_key_condition()
        query += ' FOR UPDATE'
        transaction.retry(cursor.execute, query, self._primary_key())
        self._set_locked(True)

    def _commit(self):
        """Our transaction has committed."""
        if self._state() == (self.INSERTED, self.UPDATED, self.MERGED):
            self._set_state(self.SELECTED)
        self._set_locked(False)

    def _rollback(self):
        """Our transaction has rolled back."""
        self._set_state(self.ORPHAN)

    def _rebuild(self):
        """Rebuild object state in database."""
        transaction = self.transaction()
        typ = type(self)
        pkcond = self._primary_key_condition()
        pkval = self._primary_key()
        result = transaction.select(typ, pkcond, pkval)
        if self._state() in (self.INSERTED, self.SELECTED, self.UPDATED):
            if result:
                assert len(result) == 1
                assert result[0] == self  # virtue of object cache
                self._mput(self._attributes().values())
            else:
                self._set_state(self.ASSOCIATED)
                self._insert()
        elif self._state() == self.MERGED:
            func = self.m_merge
            if result:
                assert len(result) == 1
                assert result[0] is self
                attrs = self._attributes()
                data = dict(((key, attrs[key].value()) for key in attrs))
                func(self, data)
            else:
                self._set_state(self.ASSOCIATED)
                self._insert()
                self._merge(func)
        elif self._state() == self.DELETED:
            if result:
                assert len(result) == 1
                assert result[0] == self
                self._set_state(self.INSERTED)
                self._delete()
        if self._locked():
            self.lock()

    def _get(self, attr):
        """Get an attribute value from the database."""
        assert self._state() in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED)
        transaction = self.transaction()
        cursor = transaction.cursor()
        query = 'SELECT %s FROM %s' % (attr.name, self.name)
        pkval = self._primary_key()
        pkcond = self._primary_key_condition()
        query += ' WHERE %s' % pkcond
        transaction.retry(cursor.execute, query, pkval)
        row = cursor.fetchone()
        if not row:
            raise ModelInternalError, 'Object does not exist in database?'
        attr.set_value(row[0])
        attr._lazy = False

    def _mget(self, attrs):
        """Get multiple attributes from the database."""
        assert self._state() in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED)
        transaction = self.transaction()
        cursor = transaction.cursor()
        cols = ','.join([ at.name for at in attrs ])
        query = 'SELECT %s FROM %s' % (cols, self.name)
        pkval = self._primary_key()
        pkcond = self._primary_key_condition()
        query += ' WHERE %s' % pkcond
        transaction.retry(cursor.execute, query, pkval)
        row = cursor.fetchone()
        if not row:
            raise ModelInternalError, 'Object does not exist in database?'
        for ix,at in enumerate(attrs):
            at.set_value(row[0][ix])
            attr._lazy = False

    def _put(self, attr):
        """Put an attribute value in the database."""
        assert self._state() in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED)
        transaction = self.transaction()
        cursor = transaction.cursor()
        query = 'UPDATE %s SET %s = %%s' % (self.name, attr.name)
        query += ' WHERE %s' % self._primary_key_condition()
        args = (attr.value(),) + self._primary_key()
        transaction.retry(cursor.execute, query, args)

    def _mput(self, attrs):
        """Put multiple attributes in the database."""
        assert self._state() in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED)
        transaction = self.transaction()
        cursor = transaction.cursor()
        query = 'UPDATE %s SET ' % self.name
        query += ','.join([ '%s=%%s' % at.name for at in attrs ])
        args = [ at.value() for at in attrs ]
        query += ' WHERE %s' % self._primary_key_condition()
        args += self._primary_key()
        transaction.retry(cursor.execute, query, tuple(args))

    def __getitem__(self, key):
        """Return the value for attribute `key'."""
        try:
            attr = self.m_attributes[key]
        except KeyError:
            raise KeyError, 'No such attribute: %s' % key
        if attr._lazy:
            if self._state() == self.DELETED:
                raise ModelInterfaceError, 'Object was deleted.'
            self._get(attr)
        return attr.value()

    def __setitem__(self, key, value):
        """Set the attribute `key' to `value'."""
        if self._state() == self.DELETED:
            raise ModelInterfaceError, 'Object was deleted.'
        elif self._state() == self.ORPHAN:
            raise ModelInterfaceError, 'Object\'s transaction has finished.'
        try:
            attr = self.m_attributes[key]
        except KeyError:
            raise KeyError, 'No such attribute: %s' % key
        if value == attr.value():
            return
        elif type(attr) in self.primary_key and self._state() not in \
                    (self.FREE, self.ASSOCIATED):
            raise ModelInterfaceError, 'Changing value of primary key.'
        self.pre_update(attr)
        attr.set_value(value)
        attr.validate()
        self.post_update(attr)
        # Attribute changes go directly to the database. This way we
        # are sure that select() queries in the current transaction
        # will always find the correct objects, even if the query refers
        # to attributes that have been updated.
        if self._state() == self.FREE:
            return
        self._put(attr)
        if self._state() == self.SELECTED:
            self._set_state(self.UPDATED)

    def __delitem__(self, key):
        """Delete the attribute `key'.
    
        This has the effect of setting it to its default value.
        """
        if self._state() == self.DELETED:
            raise ModelInterfaceError, 'Object was deleted.'
        elif self._state() == self.ORPHAN:
            raise ModelInterfaceError, 'Object\'s transaction has finished.'
        try:
            attr = self.m_attributes[key]
        except KeyError:
            raise KeyError, 'No such attribute: %s' % key
        if attr.value() != attr.default:
            self.__setitem__(key, attr.default)

    def keys(self):
        return self.m_attributes.keys()

    def update(self, data):
        """Update multiple attributes in one go."""
        if self._state() == self.DELETED:
            raise ModelInterfaceError, 'Object was deleted.'
        elif self._state() == self.ORPHAN:
            raise ModelInterfaceError, 'Object\'s transaction has finished.'
        attrs = []
        for key,value in data.items():
            try:
                attr = self.m_attributes[key]
            except KeyError:
                raise KeyError, 'No such attribute: %s' % key
            if value != attr.value():
                if type(attr) in self.primary_key and self._state() not in \
                            (self.FREE, self.ASSOCIATED):
                    raise ModelInterfaceError, 'Changing value of primary key.'
                self.pre_update(attr)
                attr.set_value(value)
                attr.validate()
                self.post_update(attr)
                attrs.append(attr)
        if not attrs or self._state() == self.FREE:
            return
        self._mput(attrs)
        if self._state() == self.SELECTED:
            self._set_state(self.UPDATED)

    def pick(self, data):
        """The same as update(), but ignores non-existant attributes."""
        update = {}
        for at in self.m_attributes.values():
            if data.has_key(at.name):
                update[at.name] = data[at.name]
        self.update(update)

    def extra_data(self):
        """Return additional data that was passed when this object was
        created."""
        return self.m_extradata

    def _check_not_null_columns(self):
        """Check that all columns that cannot be NULL are set."""
        for at in self.m_attributes.values():
            if at.isnull() and not at.nullok:
                mesg = ' No value for attribute w/o default: %s' % at.name
                raise ModelIntegrityError, mesg

    def _check_cardinality(self):
        """Check cardinality."""

    def _validate(self):
        """Validate the object before the transaction commits."""
        assert self._state() in (self.INSERTED, self.SELECTED, self.UPDATED,
                                 self.MERGED, self.DELETED), \
                                 'state = %s' % self._state()
        if self._state() == self.INSERTED:
            self._check_not_null_columns()
            self._check_cardinality()
            self.validate_insert()
        elif self._state() in (self.UPDATED, self.MERGED):
            self.validate_update()
        elif self._state() == self.DELETED:
            self._check_cardinality()
            self.validate_delete()

    def validate_insert(self):
        """Called for newly inserted objects when the current
        transaction commits."""

    def validate_update(self):
        """Called for updated objects when the current transaction
        commits."""

    def validate_delete(self):
        """Called for deleted objects when the current transaction
        commits."""

    def pre_insert(self):
        """Trigger called prior to object insertion."""

    def post_insert(self):
        """Trigger called after object insertion."""

    def pre_update(self, attr):
        """Trigger called prior to an attribute update."""

    def post_update(self, attr):
        """Trigger called after an attribute update."""

    def pre_delete(self):
        """Trigger called prior to object deletion."""

    def post_delete(self):
        """Trigger called after object deletion."""
