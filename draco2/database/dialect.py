# vi: ts=8 sts=4 sw=4 et
#
# dialect.py: database dialects
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class DatabaseDialect(object):
    """Base class for database dialects.

    This class tries to implement standard SQL-92.
    """

    # All SQL92 reserved keywords, from the Postgres docs
    keywords = \
    set((
        'ABSOLUTE', 'ACTION', 'ADD', 'ALL', 'ALLOCATE',
        'ALTER', 'AND', 'ANY', 'ARE', 'AS', 'ASC', 'ASSERTION', 'AT',
        'AUTHORIZATION', 'AVG', 'BEGIN', 'BETWEEN', 'BIT', 'BIT_LENGTH',
        'BOTH', 'BY', 'CASCADE', 'CASCADED', 'CASE', 'CAST', 'CATALOG',
        'CHAR', 'CHARACTER', 'CHARACTER_LENGTH', 'CHAR_LENGTH', 'CHECK',
        'CLOSE', 'COALESCE', 'COLLATE', 'COLLATION', 'COLUMN', 'COMMIT',
        'CONNECT', 'CONNECTION', 'CONSTRAINT', 'CONSTRAINTS',
        'CONTINUE', 'CONVERT', 'CORRESPONDING', 'COUNT', 'CREATE',
        'CROSS', 'CURRENT', 'CURRENT_DATE', 'CURRENT_TIME',
        'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR', 'DATE', 'DAY',
        'DEALLOCATE', 'DEC', 'DECIMAL', 'DECLARE', 'DEFAULT',
        'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DESCRIBE',
        'DESCRIPTOR', 'DIAGNOSTICS', 'DISCONNECT', 'DISTINCT', 'DOMAIN',
        'DOUBLE', 'DROP', 'ELSE', 'END', 'END-EXEC', 'ESCAPE', 'EXCEPT',
        'EXCEPTION', 'EXEC', 'EXECUTE', 'EXISTS', 'EXTERNAL', 'EXTRACT',
        'FALSE', 'FETCH', 'FIRST', 'FLOAT', 'FOR', 'FOREIGN', 'FOUND',
        'FROM', 'FULL', 'GET', 'GLOBAL', 'GO', 'GOTO', 'GRANT', 'GROUP',
        'HAVING', 'HOUR', 'IDENTITY', 'IMMEDIATE', 'IN', 'INDICATOR',
        'INITIALLY', 'INNER', 'INPUT', 'INSENSITIVE', 'INSERT', 'INT',
        'INTEGER', 'INTERSECT', 'INTERVAL', 'INTO', 'IS', 'ISOLATION',
        'JOIN', 'KEY', 'LANGUAGE', 'LAST', 'LEADING', 'LEFT', 'LEVEL',
        'LIKE', 'LOCAL', 'LOWER', 'MATCH', 'MAX', 'MIN', 'MINUTE',
        'MODULE', 'MONTH', 'NAMES', 'NATIONAL', 'NATURAL', 'NCHAR',
        'NEXT', 'NO', 'NOT', 'NULL', 'NULLIF', 'NUMERIC',
        'OCTET_LENGTH', 'OF', 'ON', 'ONLY', 'OPEN', 'OPTION', 'OR',
        'ORDER', 'OUTER', 'OUTPUT', 'OVERLAPS', 'PAD', 'PARTIAL',
        'POSITION', 'PRECISION', 'PREPARE', 'PRESERVE', 'PRIMARY',
        'PRIOR', 'PRIVILEGES', 'PROCEDURE', 'PUBLIC', 'READ', 'REAL',
        'REFERENCES', 'RELATIVE', 'RESTRICT', 'REVOKE', 'RIGHT',
        'ROLLBACK', 'ROWS', 'SCHEMA', 'SCROLL', 'SECOND', 'SECTION',
        'SELECT', 'SESSION', 'SESSION_USER', 'SET', 'SIZE', 'SMALLINT',
        'SOME', 'SPACE', 'SQL', 'SQLCODE', 'SQLERROR', 'SQLSTATE',
        'SUBSTRING', 'SUM', 'SYSTEM_USER', 'TABLE', 'TEMPORARY', 'THEN',
        'TIME', 'TIMESTAMP', 'TIMEZONE_HOUR', 'TIMEZONE_MINUTE', 'TO',
        'TRAILING', 'TRANSACTION', 'TRANSLATE', 'TRANSLATION', 'TRIM',
        'TRUE', 'UNION', 'UNIQUE', 'UNKNOWN', 'UPDATE', 'UPPER',
        'USAGE', 'USER', 'USING', 'VALUE', 'VALUES', 'VARCHAR',
        'VARYING', 'VIEW', 'WHEN', 'WHENEVER', 'WHERE', 'WITH', 'WORK',
        'WRITE', 'YEAR', 'ZONE'
    ))

    # Default SQL92 isolation levels
    isolation_levels = \
    set((
        'READ UNCOMMITTED', 'READ COMMITTED',
        'REPEATABLE READ', 'SERIALIZABLE'
    ))

    # No default encodings
    encodings = set()

    def is_keyword(self, word):
        """Return True if `word' is a reserved key word."""
        return word.upper() in self.keywords

    def is_isolation_level(self, level):
        """Return True if `level' is a supported isolation level."""
        return level.upper() in self.isolation_levels

    def is_encoding(self, encoding):
        """Return True if `encoding' is a valid encoding."""
        return encoding.upper() in self.encodings

    def sql_literal(self, value):
        """Return an SQL literal for `value'."""
        if isinstance(value, int) or isinstance(value, long) \
                    or isinstance(value, float):
            literal = '%s' % value
        elif value is None:
            literal = 'NULL'
        else:
            literal = "'%s'" % value
        return literal

    def translate(self, query):
        """Translate a query.

        The query is given in standard SQL and must be translated
        to database specific SQL.
        """
        return query
