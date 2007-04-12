# vi: ts=8 sts=4 sw=4 et
#
# schema.py: schema generation for models
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $


class Schema(object):
    """Schema object.

    The schema object is responsible for create database schema's
    for Draco models.
    """

    def __init__(self, model):
        """Constructor."""
        self.m_model = model

    def model(self):
        """Return the model."""
        return self.m_model

    def create(self, execute=True, init=True):
        """Return a set of SQL statements that create the model.

        If `execute' is true, the statement are executed.
        """
        from draco2.model.gensql import SQLChecker, SQLBuilder
        model = self.model()
        dialect = model.database().dialect()
        checker = SQLChecker(dialect)
        checker.visit(model)
        builder = SQLBuilder(dialect, init)
        builder.visit(model)
        statements = builder.result()
        if execute:
            self._execute(statements)
        return statements

    def drop(self, execute=True):
        """Return a set of SQL statements that drop the model

        If `execute' is true, the statement are executed.
        """
        from draco2.model.gensql import SQLChecker, SQLDestroyer
        model = self.model()
        dialect = model.database().dialect()
        checker = SQLChecker(dialect)
        checker.visit(model)
        destroyer = SQLDestroyer(dialect)
        destroyer.visit(model)
        statements = destroyer.result()
        if execute:
            self._execute(statements, ignore_errors=True)
        return statements

    def grant(self, principal, group=False, execute=True):
        """Return a set of SQL statements that grant a particular user
        access to the model.

        If `group' is true, `principal' refers to a group. If `execute'
        is specified, the statements are executed.
        """
        from draco2.model.gensql import SQLChecker, SQLGranter
        model = self.model()
        dialect = model.database().dialect()
        checker = SQLChecker(dialect)
        checker.visit(model)
        granter = SQLGranter(dialect, principal, group)
        granter.visit(model)
        statements = granter.result()
        if execute:
            self._execute(statements)
        return statements

    def revoke(self, principal, group=False, execute=True):
        """Return a set of SQL statements that revoke access from a
        particular user access from the model.

        If `group' is true, `principal' refers to a group. If `execute'
        is specified, the statements are executed.
        """
        from draco2.model.gensql import SQLChecker, SQLRevoker
        model = self.model()
        dialect = model.database().dialect()
        checker = SQLChecker(dialect)
        checker.visit(model)
        revoker = SQLRevoker(dialect, principal, group)
        revoker.visit(model)
        statements = revoker.result()
        if execute:
            self._execute(statements, ignore_errors=True)
        return statements
 
    def version(self):
        """Return the version of the schema in the database."""
        connection = self.model().database().connection('draco2')
        cursor = connection.cursor()
        query = 'SELECT version FROM draco2.schemas'
        query += ' WHERE name = %s'
        cursor.execute(query, (self.name,))
        row = cursor.fetchone()
        if row:
            return row[0]

    def _execute(self, statements, ignore_errors=False):
        """Execute a set of SQL statements."""
        connection = self.model().database().connection('draco2')
        cursor = connection.cursor()
        dbapi = self.model().database().dbapi()
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except dbapi.Error:
                if not ignore_errors:
                    raise
                connection.rollback()
        connection.commit()
