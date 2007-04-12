# vi: ts=8 sts=4 sw=4 et
#
# dbmysqldb.py: MySQL/MySQLdb database adapter
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
import MySQLdb
from MySQLdb.converters import conversions
from MySQLdb.constants import FIELD_TYPE, FLAG
from MySQLdb import times
from MySQLdb import pytimes
import datetime

from draco2.database import *
from draco2.database.manager import DatabaseManager
from draco2.database.dialect import DatabaseDialect


def create_datetime(value):
    """MySQL timestamp column -> Python datetime.datetime."""
    value += '0' * (14-len(value))
    year, month, day, hour, minute, second = \
            int(value[0:4]), int(value[4:6]), int(value[6:8]), \
            int(value[8:10]), int(value[10:12]), int(value[12:14])
    return datetime.datetime(year=year, month=month, day=day,
                             hour=hour, minute=minute, second=second)

def create_buffer(value):
    """MySQL blob column -> Python buffer."""
    return buffer(value)


def mysql_stringify(value, dummy):
    return "'%s'" % value


class MySQLdbDatabaseManager(DatabaseManager):
    """Draco database access for mysql using MySQLdb."""

    name = 'mysqldb'


    def __init__(self):
        super(MySQLdbDatabaseManager, self).__init__()
        self.m_dialect = MySQLdbDatabaseDialect()
        self._init_conversions()

    def _init_conversions(self):
        """Register our type conversions."""
        self.m_conversions = conversions.copy()
        self.m_conversions[FIELD_TYPE.BLOB] = [(FLAG.BINARY, create_buffer),
                                               (None, None)]
        self.m_conversions[FIELD_TYPE.DATETIME] = pytimes.DateTime_or_None
        self.m_conversions[FIELD_TYPE.DATE] = pytimes.Date_or_None
        self.m_conversions[FIELD_TYPE.TIME] = pytimes.Time_or_None
        self.m_conversions[FIELD_TYPE.TIMESTAMP] = create_datetime
        self.m_conversions[datetime.date] = mysql_stringify
        self.m_conversions[datetime.time] = mysql_stringify
        self.m_conversions[datetime.datetime] = mysql_stringify
        self.m_conversions[datetime.timedelta] = mysql_stringify

    def dbapi(self):
        """Return the Python DB API."""
        return MySQLdb

    def dialect(self):
        """Return a DatabaseDialect instance."""
        return self.m_dialect

    def _connect(self):
        """Return a new connection to the database."""
        if not self.m_dsn:
            raise DatabaseError, 'No DSN configured.'
        args = [ x.split('=') for x in self.m_dsn.split() ]
        args = dict(args)
        args['conv'] = self.m_conversions
        dbapi = self.dbapi()
        try:
            connection = MySQLdb.connect(**args)
        except dbapi.Error, err:
            raise DatabaseDBAPIError, str(err)
        cursor = connection.cursor()
        cursor.execute('SET AUTOCOMMIT = 0')
        if self.m_eventmgr:
            self.m_eventmgr.raise_event('configure_database_connection',
                                        connection)
        return connection


class MySQLdbDatabaseDialect(DatabaseDialect):
    """A database dialect for MySQL/MySQLdb."""

    keywords = set([ 'ADD', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS',
        'ASC', 'ASENSITIVE', 'BEFORE', 'BETWEEN', 'BIGINT', 'BINARY',
        'BLOB', 'BOTH', 'BY', 'CALL', 'CASCADE', 'CASE', 'CHANGE',
        'CHAR', 'CHARACTER', 'CHECK', 'COLLATE', 'COLUMN', 'CONDITION',
        'CONNECTION', 'CONSTRAINT', 'CONTINUE', 'CONVERT', 'CREATE',
        'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
        'CURRENT_USER', 'CURSOR', 'DATABASE', 'DATABASES', 'DAY_HOUR',
        'DAY_MICROSECOND', 'DAY_MINUTE', 'DAY_SECOND', 'DEC', 'DECIMAL',
        'DECLARE', 'DEFAULT', 'DELAYED', 'DELETE', 'DESC', 'DESCRIBE',
        'DETERMINISTIC', 'DISTINCT', 'DISTINCTROW', 'DIV', 'DOUBLE',
        'DROP', 'DUAL', 'EACH', 'ELSE', 'ELSEIF', 'ENCLOSED', 'ESCAPED',
        'EXISTS', 'EXIT', 'EXPLAIN', 'FALSE', 'FETCH', 'FLOAT', 'FOR',
        'FORCE', 'FOREIGN', 'FROM', 'FULLTEXT', 'GOTO', 'GRANT',
        'GROUP', 'HAVING', 'HIGH_PRIORITY', 'HOUR_MICROSECOND',
        'HOUR_MINUTE', 'HOUR_SECOND', 'IF', 'IGNORE', 'IN', 'INDEX',
        'INFILE', 'INNER', 'INOUT', 'INSENSITIVE', 'INSERT', 'INT',
        'INTEGER', 'INTERVAL', 'INTO', 'IS', 'ITERATE', 'JOIN', 'KEY',
        'KEYS', 'KILL', 'LEADING', 'LEAVE', 'LEFT', 'LIKE', 'LIMIT',
        'LINES', 'LOAD', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCK', 'LONG',
        'LONGBLOB', 'LONGTEXT', 'LOOP', 'LOW_PRIORITY', 'MATCH',
        'MEDIUMBLOB', 'MEDIUMINT', 'MEDIUMTEXT', 'MIDDLEINT',
        'MINUTE_MICROSECOND', 'MINUTE_SECOND', 'MOD', 'MODIFIES',
        'NATURAL', 'NOT', 'NO_WRITE_TO_BINLOG', 'NULL', 'NUMERIC', 'ON',
        'OPTIMIZE', 'OPTION', 'OPTIONALLY', 'OR', 'ORDER', 'OUT',
        'OUTER', 'OUTFILE', 'PRECISION', 'PRIMARY', 'PROCEDURE',
        'PURGE', 'READ', 'READS', 'REAL', 'REFERENCES', 'REGEXP',
        'RELEASE', 'RENAME', 'REPEAT', 'REPLACE', 'REQUIRE', 'RESTRICT',
        'RETURN', 'REVOKE', 'RIGHT', 'RLIKE', 'SCHEMA', 'SCHEMAS',
        'SECOND_MICROSECOND', 'SELECT', 'SENSITIVE', 'SEPARATOR', 'SET',
        'SHOW', 'SMALLINT', 'SONAME', 'SPATIAL', 'SPECIFIC', 'SQL',
        'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNING', 'SQL_BIG_RESULT',
        'SQL_CALC_FOUND_ROWS', 'SQL_SMALL_RESULT', 'SSL', 'STARTING',
        'STRAIGHT_JOIN', 'TABLE', 'TERMINATED', 'THEN', 'TINYBLOB',
        'TINYINT', 'TINYTEXT', 'TO', 'TRAILING', 'TRIGGER', 'TRUE',
        'UNDO', 'UNION', 'UNIQUE', 'UNLOCK', 'UNSIGNED', 'UPDATE',
        'USAGE', 'USE', 'USING', 'UTC_DATE', 'UTC_TIME',
        'UTC_TIMESTAMP', 'VALUES', 'VARBINARY', 'VARCHAR',
        'VARCHARACTER', 'VARYING', 'WHEN', 'WHERE', 'WHILE', 'WITH',
        'WRITE', 'XOR', 'YEAR_MONTH', 'ZEROFILL'])

    re_blob = re.compile('\s(BLOB|BINARY LARGE OBJECT)\s', re.I)
    re_text = re.compile('\s(TEXT)\s', re.I)
    re_timestamp = re.compile('\s(TIMESTAMP)\s', re.I)

    def translate(self, query):
        """Translate `query' to MySQL specific dialect."""
        head = query[:30].lstrip().upper()
        if head.startswith('CREATE TABLE'):
            query += ' TYPE = InnoDB'
            query = self.re_blob.sub(' LONGBLOB ', query)
            query = self.re_text.sub(' LONGTEXT ', query)
            query = self.re_timestamp.sub(' DATETIME ', query)
        return query
