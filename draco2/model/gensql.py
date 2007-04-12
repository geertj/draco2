# vi: ts=8 sts=4 sw=4 et
#
# gensql.py: SQL generator
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


class SQLChecker(ModelVisitor):
    """Check that all names are OK with the SQL dialect."""

    def __init__(self, dialect):
        self.m_dialect = dialect

    def visit_model(self, mdl):
        if self.m_dialect.is_keyword(mdl.name):
            m = 'Value of property "name" is an SQL keyword in model %s'
            raise ModelDefinitionError, m % mdl.__name__

    def visit_attribute(self, att):
        if self.m_dialect.is_keyword(att.name):
            m = 'Value of property "name" is an SQL keyword in attr. %s'
            raise ModelDefinitionError, m % att.__name__

    def visit_index(self, idx):
        if self.m_dialect.is_keyword(idx.name):
            m = 'Value of property "name" is an SQL keyword in index %s'
            raise ModelDefinitionError, m % idx.__name__

    def visit_entity(self, ent):
        if self.m_dialect.is_keyword(ent.name):
            m = 'Value of property "name" is an SQL keyword in entity %s'
            raise ModelDefinitionError, m % ent.__name__

    def visit_relationship(self, rel):
        if self.m_dialect.is_keyword(rel.name):
            m = 'Value of property "name" is an SQL keyword in rel. %s'
            raise ModelDefinitionError, m % rel.__name__


class SQLGenerator(ModelVisitor):
    """Base class for SQL generating visitors."""

    def __init__(self, dialect):
        self.m_dialect = dialect
        self.m_result = []

    def emit(self, query):
        """Add an SQL statement `result' to the result."""
        query = self.m_dialect.translate(query)
        self.m_result.append(query)

    def result(self):
        """Return the compound SQL statement."""
        return self.m_result


class SQLBuilder(SQLGenerator):
    """Generate SQL code for a model."""

    def __init__(self, dialect, init=True):
        super(SQLBuilder, self).__init__(dialect)
        self.m_init = init

    def visit(self, model):
        """Visit a model."""
        query = 'CREATE SCHEMA %s' % model.name
        self.emit(query)
        super(SQLBuilder, self).visit(model)

    def visit_entity(self, ent):
        """Create SQL code for an Entity.

        The output consits of a table with columns for all attributes.
        Sequences are created for all attributes that constitute the
        primary key.
        """
        items = []
        dialect = self.m_dialect
        for at in ent.attributes:
            column = '%s %s' % (at.name, at.external_type)
            if at.width is not None:
                column += '(%d)' % at.width
            elif at.precision is not None:
                column += '(%d' % at.precision
                if at.scale is not None:
                    column += ',%d' % at.scale
                column += ')'
            column += ' DEFAULT %s' % dialect.sql_literal(at.default)
            items.append(column)
        refcount = '_refcount INTEGER NOT NULL DEFAULT 0'
        items.append(refcount)
        pkcols = ','.join([pk.name for pk in ent.primary_key])
        constr = 'PRIMARY KEY (%s)' % pkcols
        items.append(constr)
        query = 'CREATE TABLE %s (%s)' % (ent.name, ','.join(items))
        self.emit(query)
        for pk in ent.primary_key:
            if pk.sequence_name:
                query = 'CREATE SEQUENCE %s' % pk.sequence_name
                self.emit(query)
        for ix in ent.indexes:
            query = 'CREATE'
            if ix.unique:
                query += ' UNIQUE'
            query += ' INDEX %s ON %s' % (ix.name, ent.name)
            if ix.type:
                query += ' USING %s ' % ix.type
            ixcols = ','.join([at.name for at in ix.attributes])
            query += '(%s)' % ixcols
            self.emit(query)

    def visit_relationship(self, rel):
        """Output SQL code for a Relationship.

        The output consists of a table with columns for all attributes
        including foreign keys. The primary key of the table is a
        composite formed by all foreign keys.
        """
        items = []
        dialect = self.m_dialect
        for at in rel.attributes:
            column = '%s %s' % (at.name, at.external_type)
            if at.width is not None:
                column += '(%d)' % at.width
            elif at.precision is not None:
                column += '(%d' % at.precision
                if at.scale is not None:
                    column += ',%d' % at.scale
                column += ')'
            column += ' DEFAULT %s' % dialect.sql_literal(at.default)
            items.append(column)
        for name,ent,card,fk in rel.roles:
            fkcols = ','.join([at.name for at in fk])
            pkcols = ','.join([at.name for at in ent.primary_key])
            constr = 'FOREIGN KEY (%s) ' % fkcols
            constr += 'REFERENCES %s (%s) ' % (ent.name, pkcols)
            constr += 'ON DELETE RESTRICT'
            items.append(constr)
        pkcols = ','.join([pk.name for pk in rel.primary_key])
        constr = 'PRIMARY KEY (%s)' % pkcols
        items.append(constr)
        query = 'CREATE TABLE %s (%s)' % (rel.name, ','.join(items))
        self.emit(query)

    def visit_view(self, view):
        """Output SQL code for a View.

        No column renaming is performed. The view's query must name columns
        such that there are no duplicates.
        """
        query = 'CREATE VIEW %s AS %s' % (view.name, view.query)
        self.emit(query)

    def visit_model(self, model):
        """Output SQL code for a Model.

        This will output the model initialisation statements."""
        if self.m_init:
            for stmt in model.init_statements:
                self.emit(stmt)


class SQLDestroyer(SQLGenerator):
    """Remove all database objects relating to a model."""

    def visit_model(self, model):
        """Visit a model."""
        query = 'DROP SCHEMA %s CASCADE' % model.name
        self.emit(query)


class SQLGranter(SQLGenerator):
    """Grant access to a user or group.

    The output of this visitor is a set of GRANT statements that grant
    access to all required database objects required.
    """

    rights = { 'TABLE': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
               'SCHEMA': ['USAGE'] }

    def __init__(self, dialect, principal=None, group=False, grant=False):
        super(SQLGranter, self).__init__(dialect)
        self.m_principal = principal
        self.m_group = group
        self.m_grant = grant

    def grant(self, name, rights=None, type=None):
        if type is None:
            type = 'TABLE'
        if rights is None:
            rights = self.rights[type]
        rights = ','.join(rights)
        query = 'GRANT %s' % rights
        query += ' ON %s %s' % (type, name)
        if self.m_group:
            query += ' TO GROUP %s' % self.m_principal
        else:
            query += ' TO %s' % self.m_principal
        if self.m_grant:
            query += ' WITH GRANT OPTION'
        self.emit(query)

    def visit_entity(self, ent):
        self.grant(ent.name)
        for pk in ent.primary_key:
            if pk.sequence_name:
                self.grant(pk.sequence_name)

    def visit_relationship(self, rel):
        self.grant(rel.name)

    def visit_view(self, view):
        self.grant(view.name)

    def visit_model(self, model):
        self.grant(model.name, type='SCHEMA')


class SQLRevoker(SQLGenerator):
    """Revoke access to a user or group.

    The output of this visitor is a set of REVOKE statements that revokes
    all priviles from the database objects involved in this model.
    """

    def __init__(self, dialect, principal=None, group=False):
        super(SQLRevoker, self).__init__(dialect)
        self.m_principal = principal
        self.m_group = group

    def revoke(self, name, type=None):
        if type is None:
            type = 'TABLE'
        query = 'REVOKE ALL PRIVILEGES'
        query += ' ON %s %s' % (type, name)
        if self.m_group:
            query += ' FROM GROUP %s' % self.m_principal
        else:
            query += ' FROM %s' % self.m_principal
        self.emit(query)

    def visit_entity(self, ent):
        self.revoke(ent.name)
        for pk in ent.primary_key:
            if pk.sequence_name:
                self.revoke(pk.sequence_name)

    def visit_relationship(self, rel):
        self.revoke(rel.name)

    def visit_view(self, view):
        self.revoke(view.name)

    def visit_model(self, model):
        self.revoke(model.name, type='SCHEMA')
