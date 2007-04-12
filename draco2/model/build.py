# vi: ts=8 sts=4 sw=4 et
#
# build.py: build a model
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
from draco2.model.attribute import IntegerAttribute
from draco2.model.visit import ModelVisitor


class BuildVisitor(ModelVisitor):
    """Build a model that can be used at runtime."""

    def __init__(self):
        self.entities = set()
        self.relationships = set()

    def visit_entity(self, ent):
        ent.roles = []
        ent.name = '%s.%s' % (self.model.name, ent.name)
        for pk in ent.primary_key:
            if issubclass(pk, IntegerAttribute):
                pk.sequence_name = '%s_%s_seq' % (ent.name, pk.name)
            else:
                pk.sequence_name = None
        self.entities.add(ent)

    def visit_relationship(self, rel):
        pkey = []
        fkeys = []
        rel.name = '%s.%s' % (self.model.name, rel.name)
        for role,entity,card in rel.roles:
            # Create foreign keys attributes as derived classes of
            # the primary key using the `type' metaclass.
            fkey = []
            for pk in entity.primary_key:
                dict = {}
                dict['name'] = '%s_%s' % (role, pk.name)
                dict['default'] = None
                dict['nullok'] = False
                name = pk.__name__ + 'Reference'
                fk = type(name, (pk,), dict)
                pkey.append(fk)
                fkey.append(fk)
            fkeys.append(fkey)
        rel.primary_key = pkey
        rel.roles = [ role + (fk,) for role,fk in zip(rel.roles, fkeys) ]
        rel.attributes = rel.primary_key + rel.attributes
        self.relationships.add(rel)

    def visit_view(self, view):
        view.name = '%s.%s' % (self.model.name, view.name)

    def visit_model(self, model):
        for en in self.entities:
            for rel in self.relationships:
                for role,entity,card,fk in rel.roles:
                    if en is entity:
                        en.roles.append((role, rel, card, fk))
