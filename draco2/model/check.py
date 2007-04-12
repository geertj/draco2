# vi: ts=8 sts=4 sw=4 et
#
# check.py: check a model
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
from draco2.model.visit import ModelVisitor
from draco2.model.attribute import Attribute
from draco2.model.index import Index
from draco2.model.entity import Entity
from draco2.model.relationship import Relationship
from draco2.model.view import View
from draco2.model.transaction import Transaction


class CheckVisitor(ModelVisitor):
    """A visitor that check a model as defined by the user."""

    def visit_attribute(self, att):
        if not issubclass(att, Attribute):
            raise ModelDefinitionError, '%s: not an "Attribute"' % att
        if att.name is None:
            raise ModelDefinitionError, '%s: "name" not set' % att
        if not isinstance(att.name, str):
            raise ModelDefinitionError, '%s: "name" must be str' % att
        if att.type is None:
            raise ModelDefinitionError, '%s: "type" not set' % att
        if att.external_type is None:
            raise ModelDefinitionError, '%s: "external_type" not set' % att
        if not isinstance(att.external_type, str):
            raise ModelDefinitionError, '%s: "external_type" must be str' % att

    def visit_index(self, idx):
        if not issubclass(idx, Index):
            raise ModelDefinitionError, '%s: not an "Index"' % idx
        if idx.name is None:
            raise ModelDefinitionError, '%s: "name" not set' % idx
        if not isinstance(idx.name, str):
            raise ModelDefinitionError, '%s: "name" must be str' % idx
        if idx.type is not None and not isinstance(idx.type, str):
            raise ModelDefinitionError, '%s: "type" must be str' % idx

    def visit_entity(self, ent):
        if not issubclass(ent, Entity):
            raise ModelDefinitionError, '%s: not an "Entity"' % ent
        if ent.name is None:
            raise ModelDefinitionError, '%s: "name" not set' % ent
        if not isinstance(ent.name, str):
            raise ModelDefinitionError, '%s: "name" must be str' % ent
        if not ent.primary_key:
            raise ModelDefinitionError, '%s: no primary key specified' % ent
        for pk in ent.primary_key:
            if pk not in ent.attributes:
                raise ModelDefinitionError, '%s: primary key not in attributes' % ent
        names = set([at.name for at in ent.attributes])
        if len(names) != len(ent.attributes):
            raise ModelDefinitionError, '%s: attribute names not unique' % ent
        names = set([ix.name for ix in ent.indexes])
        if len(names) != len(ent.indexes):
            raise ModelDefinitionError, '%s: index names not unique' % ent

    def visit_relationship(self, rel):
        if not issubclass(rel, Relationship):
            m = 'Object is not a "Relationship: %s"'
            raise ModelDefinitionError, m % rel
        if rel.name is None:
            m = 'Property "name" not set in rel. %s'
            raise ModelDefinitionError, m % rel.__name__
        if not isinstance(rel.name, str):
            m = 'Property "name" must be str in rel. %s'
            raise ModelDefinitionError, m % rel.__name__
        if not rel.roles:
            m = 'Property "roles" not set in rel. %s'
            raise ModelDefinitionError, m % rel.__name__
        if not isinstance(rel.roles, list):
            m = 'Property "roles" must must be list in rel. %s'
            raise ModelDefinitionError, m % rel.__name__
        for role in rel.roles:
            if not isinstance(role, tuple) or len(role) != 3 \
                    or not isinstance(role[0], str) \
                    or not issubclass(role[1], Entity) \
                    or not isinstance(role[2], tuple) \
                    or not (isinstance(role[2][0], int) or role[2][0] is None) \
                    or not (isinstance(role[2][1], int) or role[2][1] is None):
                m = 'Roles must be [(str, Entity, (int, int))] in rel. %s'
                raise ModelDefinitionError, m % rel.__name__
        names = set([ ro[0] for ro in rel.roles])
        if len(names) != len(rel.roles):
            m = 'Role names not unique in rel. %s'
            raise ModelDefinitionError, m % rel.__name__
        names = set([at.name for at in rel.attributes])
        if len(names) != len(rel.attributes):
            m = 'Attribute names not unique in rel. %s'
            raise ModelDefinitionError, m % rel.__name__

    def visit_view(self, view):
        if not issubclass(view, View):
            raise ModelDefinitionError, '%s: not a "View"' % view
        if view.name is None:
            raise ModelDefinitionError, '%s: "name" not set' % view
        if not isinstance(view.name, str):
            raise ModelDefinitionError, '%s: "name" must be str' % view
        if view.query is None:
            raise ModelDefinitionError, '%s: "query" not set' % view
        if not isinstance(view.query, str):
            raise ModelDefinitionError, '%s: "query" must be str' % view

    def visit_model(self, mdl):
        # This given an import problem with metaclass:
        #if not issubclass(mdl, Model):
        #    raise ModelDefinitionError, '%s: not a "Model"'
        if mdl.name is None:
            raise ModelDefinitionError, '%s: "name" not set' % mdl
        if not isinstance(mdl.name, str):
            raise ModelDefinitionError, '%s: "name" must be str' % mdl
        if mdl.version is None:
            raise ModelDefinitionError, '%s: "version" not set' % mdl
        if not isinstance(mdl.version, int):
            raise ModelDefinitionError, '%s: "version" must be int' % mdl
        if not issubclass(mdl.transaction_factory, Transaction):
            raise ModelDefinitionError, \
                    '%s: "transaction_factory" not a "Transaction"' % mdl
        names = set()
        names.update(set([en.name for en in mdl.entities]))
        names.update(set([re.name for re in mdl.relationships]))
        if len(names) != len(mdl.entities) + len(mdl.relationships):
            raise ModelDefinitionError, \
                    '%s: entity/relationship names not unique' % mdl
