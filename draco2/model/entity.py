# vi: ts=8 sts=4 sw=4 et
#
# entity.py: the Entity class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.model import *
from draco2.model.object import Object


class Entity(Object):
    """An entity in the Draco Model."""

    delete_unref = False

    def _primary_key_value(self, attr):
        """Return a new value for primary key `attr'."""
        assert attr.sequence_name
        cursor = self.transaction().cursor()
        dialect = self.transaction().model().database().dialect()
        query = dialect.translate('SELECT nextval(\'%s\')' % attr.sequence_name)
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            raise ModelDatabaseError, 'Sequence returned zero rows?'
        return row[0]

    def in_role(self, name, rel):
        """Return relationships where this entity is in `role'."""
        role = rel._get_role(name)
        name,ent,card,fk = role
        if ent is not type(self):
            raise ModelInterfaceError, 'Object has no role in relationship.'
        assert len(fk) == len(self.primary_key)
        transaction = self.transaction()
        fkcond = rel._foreign_key_condition(name)
        pktuple = self._primary_key()
        result = transaction.select(rel, fkcond, pktuple)
        return result

    def _insert(self):
        """Add the entity to a transaction."""
        if self._state() != self.ASSOCIATED:
            raise ModelInterfaceError, 'No transaction associated.'
        for at in self.m_attributes.values():
            if at.isnull() and type(at) in self.primary_key:
                at.set_value(self._primary_key_value(at))
        super(Entity, self)._insert()

    def _delete(self):
        """Delete the entity."""
        # The relationships involving this entity are also removed.
        # This will update the reference counts on the involved objects.
        transaction = self.transaction()
        for role in self.roles:
            name,rel,card,fk = role
            for relobj in self.in_role(name, rel):
                transaction.delete(relobj)
        super(Entity, self)._delete()

    def _check_roles(self, role1, roles2):
        """Check cardinaltiy of `role1' wrt. `role2'."""
        name1,rel1,card1,fk1 = role1
        cond = ' AND '.join(['%s=%%s' % at.name for at in fk1])
        values = self._primary_key()
        assert len(fk1) == len(values)
        fkcols = ','.join([ at.name for role2 in roles2 for at in role2[3] ])
        query = 'SELECT COUNT(*)'
        query += ' FROM %s' % rel1.name
        query += ' WHERE %s IN (SELECT %s FROM %s WHERE %s)' % \
                (fkcols, fkcols, rel1.name, cond)
        query += ' GROUP BY %s' % fkcols
        cursor = self.transaction().cursor()
        cursor.execute(query, values)
        result = cursor.fetchall()
        if len(result) == 0 and card1[0] > 0:
            m = 'Cardinality for role "%s" not in [%s:%s].'
            raise ModelIntegrityError, m % (name1, card1[0], card1[1])
        for res in result:
            count = res[0]
            if count < card1[0] or card1[1] is not None and count > card1[1]:
                m = 'Cardinality for role "%s" not in [%s:%s].'
                raise ModelIntegrityError, m % (name1, card1[0], card1[1])

    def _check_cardinality(self):
        """Check cardinality."""
        # XXX: cardinality checking is broken (again...)
        # Add a object on which another object exists existentially, but
        # the object itself doesn't depend on anything: error.
        return
        for role1 in self.roles:
            name1,rel1,card1,fk1 = role1
            roles2 = [ role2 for role2 in rel1.roles if role2[0] != name1 ]
            self._check_roles(role1, roles2)

    def _inc_refcount(self):
        """Increase reference count."""
        query = 'UPDATE %s' % self.name
        query += ' SET _refcount = _refcount + 1'
        query += ' WHERE %s' % self._primary_key_condition()
        cursor = self.transaction().cursor()
        cursor.execute(query, self._primary_key())

    def _dec_refcount(self):
        """Remove reference count."""
        query = 'UPDATE %s' % self.name
        query += ' SET _refcount = _refcount - 1'
        query += ' WHERE %s' % self._primary_key_condition()
        cursor = self.transaction().cursor()
        cursor.execute(query, self._primary_key())
