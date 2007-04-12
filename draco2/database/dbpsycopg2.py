# vi: ts=8 sts=4 sw=4 et
#
# dbpsycopg2.py: psycopg2 database adapter
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import re
import decimal
import psycopg2
import psycopg2.extensions as ppgext

from draco2.database import *
from draco2.database.manager import DatabaseManager
from draco2.database.dialect import DatabaseDialect


ppgext.register_type(ppgext.UNICODE)

# This is really a horrible HACK.
# 
# There are serious problems in which mod_python uses multiple interpreters.
# The problems are such that one can ask himself whether this actually means
# that mod_python and the way it uses multiple interpreters is fundamentaly
# flawed and unfixable.
#
# See this these postings:
# 
#   - http://www.mail-archive.com/python-dev@python.org/msg20175.html
#   - http://mail.python.org/pipermail/python-list/2004-January/244343.html
# 
# The summary is that extension modules are not really guaranteed to work as
# expected with multiple interpreters. For pure Python modules, each
# interpreter has a copy of that module. For C extension modules, there is one
# copy only that is shared between all interpreters. This means that extension
# modules cannot use global static variables.
# 
# Psycopg caches the type of the "decimal" module for typecasting purposes.
# Because the decimal type is a pure python type, this means that this python
# type (which is specific to the interpreter that first loaded psycopg) will
# now be shared with other, non-related interpreters. This causes problems,
# one of them being that isinstance(decimal, object) will only work in the
# first interpreter.
# 
# The horrible HACK we do here is to compile psycopg without support for the
# Decimal type, and we register our own pure Python type conversion routines.
# In these routines we re-import the decimal type (appears to be necessary,
# don't understand fully why) and return the _correct_ decimal type for the
# current interpreter.  Fortunately the other typecasting types used by
# psycopg are C types and therefore do not have this problem.

def cast_decimal(value, cursor):
    """SQL NUMERIC -> Python Decimal."""
    if value is None:
        return None
    from decimal import Decimal  # re-import!
    value = Decimal(value)
    return value

def adapt_decimal(object):
    """Python Decimal -> SQL."""
    return ppgext.AsIs(object)

NUMERIC = ppgext.new_type((1700,), 'NUMERIC', cast_decimal)
ppgext.register_type(NUMERIC)
ppgext.register_adapter(decimal.Decimal, adapt_decimal)


class Psycopg2DatabaseManager(DatabaseManager):
    """Psycopg2 database manager."""

    name = 'psycopg2'

    def __init__(self, dsn):
        """Constructor."""
        super(Psycopg2DatabaseManager, self).__init__(dsn)
        self.m_dialect = Psycopg2DatabaseDialect()

    def _configure(self, config):
        """Configure using the Draco configuration file."""
        super(Psycopg2DatabaseManager, self)._configure(config)

    def dbapi(self):
        """Return the Python DB API."""
        return psycopg2

    def dialect(self):
        """Return a DatabaseDialect instance. """
        return self.m_dialect

    def dump_command(self, schema=None, output=None):
        """Return a command that will dump the contents of `schema'
        to `output'.

        If no schema is specified the entire database must be dumped. If
        output is not specified, output should be written to standard
        output.
        """
        dsn = dict([i.split('=') for i in self.m_dsn.split()])
        dbname = dsn.get('dbname')
        if not dbname:
            return
        command = 'pg_dump --data-only'
        if schema:
            command += ' --schema=%s' % schema
        if output:
            command += ' --file=%s' % output
        command += ' %s' % dbname
        return command

    def set_isolation_level(self, connection, level):
        """Set the isolation level of `connection' to `level'."""
        dialect = self.dialect()
        if not dialect.is_isolation_level(level):
            m = 'Unknown transaction isolation level: %s'
            raise ValueError, m % level
        level = dialect.isolation_levels[level]
        connection.set_isolation_level(level)

    def set_client_encoding(self, connection, encoding):
        """Set the client encoding on the connection to `encoding'."""
        dialect = self.dialect()
        if not dialect.is_encoding(encoding):
            m = 'Unknown client encoding: %s'
            raise ValueError, m % encoding
        connection.set_client_encoding(encoding)

    def is_serialization_error(self, exception):
        """Return True if `exception' is a serialization error."""
        # This is a HACK but there's no other way.
        err = str(exception)
        return err.startswith('could not serialize access') or \
               err.startswith('deadlock detected')

    def serialization_error(self):
        """Return an instance of a serialization error."""
        err = DatabaseDBAPIError('could not serialize access')
        return err

    def is_primary_key_error(self, exception):
        """Return True if `exception' is a primary key error."""
        err = str(exception)
        return err.startswith('duplicate key violates')

    def primary_key_error(self):
        """Return an instance of a primary key error."""
        err = DatabaseDBAPIError('duplicate key violates')
        return err

    def _connect(self):
        """Create a new database connection."""
        dbapi = self.dbapi()
        try:
            connection = dbapi.connect(dsn=self.m_dsn)
            connection.set_client_encoding('UNICODE')
        except dbapi.Error, err:
            raise DatabaseInterfaceError, str(err)
        return connection


class Psycopg2DatabaseDialect(DatabaseDialect):
    """A database dialect for Psycopg2/PostgreSQL."""

    keywords = \
    set((
        'ALL', 'AND', 'ANY', 'AS', 'ASC', 'AUTHORIZATION',
        'BETWEEN', 'BOTH', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN',
        'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME',
        'CURRENT_TIMESTAMP', 'CURRENT_USER', 'DEFAULT', 'DEFERRABLE',
        'DESC', 'DISTINCT', 'ELSE', 'END', 'EXCEPT', 'FALSE', 'FOR',
        'FOREIGN', 'FROM', 'FULL', 'GRANT', 'GROUP', 'HAVING', 'IN',
        'INITIALLY', 'INNER', 'INTERSECT', 'INTO', 'IS', 'JOIN',
        'LEADING', 'LEFT', 'LIKE', 'NATURAL', 'NOT', 'NULL', 'ON',
        'ONLY', 'OR', 'ORDER', 'OUTER', 'OVERLAPS', 'PRIMARY',
        'REFERENCES', 'RIGHT', 'SELECT', 'SESSION_USER', 'SOME',
        'TABLE', 'THEN', 'TO', 'TRAILING', 'TRUE', 'UNION', 'UNIQUE',
        'USER', 'USING', 'WHEN', 'WHERE'
    ))
    isolation_levels = \
    {
        'READ UNCOMMITTED': ppgext.ISOLATION_LEVEL_READ_UNCOMMITTED,
        'READ COMMITTED': ppgext.ISOLATION_LEVEL_READ_COMMITTED,
        'REPEATABLE READ': ppgext.ISOLATION_LEVEL_REPEATABLE_READ,
        'SERIALIZABLE': ppgext.ISOLATION_LEVEL_SERIALIZABLE
    }
    encodings = \
    set((
        'SQL_ASCII', 'EUC_JP', 'EUC_CN', 'EUC_KR', 'JOHAB', 'EUC_TW',
        'UNICODE', 'MULE_INTERNAL', 'LATIN1', 'LATIN2', 'LATIN3', 'LATIN4',
        'LATIN5', 'LATIN6', 'LATIN7', 'LATIN8', 'LATIN9', 'LATIN10',
        'ISO_8859_5', 'ISO_8859_6', 'ISO_8859_7', 'ISO_8859_8', 'KOI8',
        'WIN', 'ALT', 'WIN1256', 'TCVN', 'WIN874'
    ))

    re_blob = re.compile('\s(BLOB|BINARY LARGE OBJECT)\s', re.I)


    def translate(self, query):
        head = query[:30].lstrip().upper()
        if head.startswith('CREATE TABLE'):
            query = self.re_blob.sub(' BYTEA ', query)
        return query
