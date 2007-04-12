# vi: ts=8 sts=4 sw=4 et
#
# obcache.py: transaction object cache
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.model.object import Object
from draco2.model.entity import Entity
from draco2.model.relationship import Relationship


class ObjectCache(object):
    """Object cache for entities and relationships.

    This cache is used by Transaction to ensure that there will always
    be only one instance of each unqiue object.
    """

    def __init__(self):
        self.m_objects = {}
        self.m_referenced = {}

    def _add_relationship(self, obj):
        assert isinstance(obj, Relationship)
        for role in obj.roles:
            name,ent,card,fk = role
            key = (ent.name, obj._foreign_key(name))
            try:
                self.m_referenced[key].append(obj)
            except KeyError:
                self.m_referenced[key] = [obj]

    def _delete_entity(self, obj):
        assert isinstance(obj, Entity)
        key = (obj.name, obj._primary_key())
        for rel in self.m_referenced.get(key, []):
            rel._set_state(rel.DELETED)

    def __iter__(self):
        """Iterate over values."""
        return self.m_objects.itervalues()

    def values(self):
        """Return all values (entities first)."""
        values = [ x for x in self if isinstance(x, Entity) ]
        values += [ x for x in self if isinstance(x, Relationship) ]
        return values

    def insert(self, obj):
        """Add an entity or a relationship to the cache."""
        if not isinstance(obj, Object):
            raise TypeError, 'Expecting `Object\' instance.'
        pk = obj._primary_key()
        if not pk:
            return
        key = (obj.name, tuple(pk))
        self.m_objects[key] = obj
        # A table cross-referencing object primary keys to relationship
        # instances is maintained. When an entity is deleted, this table
        # is used to also any possible the relationship instances pointing
        # to the entity.
        if isinstance(obj, Relationship):
            self._add_relationship(obj)

    def select(self, typ, pk):
        """Return an object of type `typ' and primary key `pk' from the
        cache. If the object is not found, None is returned."""
        if not issubclass(typ, Object):
            raise TypeError, 'Expecting `Object\' subclass.'
        if not pk:
            return
        key = (typ.name, tuple(pk))
        return self.m_objects.get(key)

    def delete(self, obj):
        """Add an entity or a relationship to the cache."""
        if not isinstance(obj, Entity) and not isinstance(obj, Relationship):
            raise TypeError, 'Expecting Entity or Relationship instance.'
        # The entity itself is left in place, so that the validation
        # code gets run.  If a new object with the same PK is
        # reinstated, insert() will take over the cache entry.
        if isinstance(obj, Entity):
            self._delete_entity(obj)

    def clear(self):
        """Clear the object cache."""
        self.m_objects = {}
        self.m_referenced = {}
