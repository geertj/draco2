# vi: ts=8 sts=4 sw=4 et
#
# relationship.py: defines the Relationship class
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
from draco2.model.object import Object


class Relationship(Object):
    """A relationship in the Draco model."""

    attributes = []
    roles = None

    c_fkcond = {}

    @classmethod
    def _get_role(cls, role):
        """Return the role `role'."""
        for ro in cls.roles:
            if ro[0] == role:
                return ro
        raise KeyError, 'No such role: %s' % role

    def _foreign_key(self, role):
        """Return the foreign key tuple for `role'."""
        name,ent,card,fk = self._get_role(role)
        assert len(fk) == len(ent.primary_key)
        values = [ self[at.name] for at in fk ]
        return tuple(values)

    @classmethod
    def _foreign_key_condition(cls, role):
        """Return a condition that selects `role'."""
        if role in cls.c_fkcond:
            return cls.c_fkcond[role]
        name,ent,card,fk = cls._get_role(role)
        assert len(fk) == len(ent.primary_key)
        values = [ '%s=%%s' % at.name for at in fk ]
        cls.c_fkcond[name] = ' AND '.join(values)
        return cls.c_fkcond[name]

    def role(self, name):
        """Return the entity for `role'."""
        if self._state() == self.DELETED:
            raise ModelInterfaceError, 'Object was deleted.'
        role = self._get_role(name)
        if not role:
            raise ModelInterfaceError, 'No such role: %s' % name
        name,ent,card,fk = role
        assert len(fk) == len(ent.primary_key)
        condition = ' AND '.join(['%s=%%s' % at.name for at in ent.primary_key])
        values = [self[at.name] for at in fk ]
        transaction = self.transaction()
        result = transaction.select(ent, condition, values)
        if len(result) != 1:
            raise ModelInternalError, 'Referenced object is deleted?'
        return result[0]

    def set_role(self, name, obj):
        """Put object `obj' in role `role'."""
        if self._state() != self.FREE:
            raise ModelInterfaceError, 'Relationship already associated.'
        role = self._get_role(name)
        if not role:
            raise ModelInterfaceError, 'No such role: %s' % name
        name,ent,card,fk = role
        if not isinstance(obj, ent):
            raise TypeError, 'Illegal type for role %s' % name
        if obj._state() not in (self.INSERTED, self.SELECTED, self.UPDATED,
                                self.DELETED):
            raise ModelInterfaceError, 'Entity does not exist.'
        assert len(fk) == len(ent.primary_key)
        for fkat,pkat in zip(fk, ent.primary_key):
            attr = self.m_attributes[fkat.name]
            attr.set_value(obj[pkat.name])

    def _insert(self):
        """Insert the relationship into a transaction."""
        if self._state() != self.ASSOCIATED:
            raise ModelInterfaceError, 'No transaction associated.'
        for role in self.roles:
            name,ent,card,fk = role
            for at in fk:
                assert at.name in self.m_attributes
                if self.m_attributes[at.name].isnull():
                    mesg = 'Role has not been set: %s' % name
                    raise ModelInterfaceError, mesg
        super(Relationship, self)._insert()
        for role in self.roles:
            name,ent,card,fk = role
            obj = self.role(name)
            obj._inc_refcount()

    def _delete(self):
        """Delete the relationship."""
        if self._state() not in (self.INSERTED, self.SELECTED, self.UPDATED):
            raise ModelInterfaceError, 'Object does not exist.'
        for role in self.roles:
            name,ent,card,fk = role
            obj = self.role(name)
            obj._dec_refcount()
        super(Relationship, self)._delete()

    def _check_roles(self, role1, roles2):
        """Check the cardinality of `role1' with respect to `roles2'."""
        name1,ent1,card1,fk1 = role1
        pkcond = ' AND '.join(['%s=%%s' % at.name for at in ent1.primary_key])
        assert len(ent1.primary_key) == len(fk1)
        pkvals = [ self[at.name] for at in fk1 ]
        query = 'SELECT COUNT(*)'
        query += ' FROM %s' % ent1.name
        query += ' WHERE %s' % pkcond
        cursor = self.transaction().cursor()
        cursor.execute(query, pkvals)
        row = cursor.fetchone()
        if row is None:
            raise ModelInternalError, 'COUNT(*) returns zero rows?'
        count = row[0]
        if count == 0:
            return
        fkcond = [ '%s=%%s' % at.name for role2 in roles2 for at in role2[3] ]
        fkcond = ' AND '.join(fkcond)
        fkvals = [ self[at.name] for role2 in roles2 for at in role2[3] ]
        query = 'SELECT COUNT(*)'
        query += ' FROM %s' % self.name
        query += ' WHERE %s' % fkcond
        cursor = self.transaction().cursor()
        cursor.execute(query, fkvals)
        row = cursor.fetchone()
        if not row:
            raise ModelInteralError, 'COUNT(*) returns zero rows?'
        if count < card1[0] or card1[1] is not None and count > card1[1]:
            m = 'Cardinality of role "%s" not in [%s:%s].'
            raise ModelIntegrityError, m % (name, card[0], card[1])

    def _check_cardinality(self):
        """Check cardinality of this relationship."""
        for role1 in self.roles:
            roles2 = [ role2 for role2 in self.roles if role2 != role1 ]
            self._check_roles(role1, roles2)
