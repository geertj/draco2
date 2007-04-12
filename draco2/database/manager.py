# vi: ts=8 sts=4 sw=4 et
#
# manager.py: database manager
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import logging
import threading

from draco2.database.exception import *


class DatabaseManager(object):
    """Base class for all database managers.

    This class must be inherited by database managers that implement an
    interface to a specific RDBMS.

    A database manager instance has two responsabilities:
    - Create and manage database connections.
    - Provide DB specific instances of the DB-API and dialect.
    """

    name = None

    def __init__(self, dsn):
        """Constructor."""
        self.m_config = None
        self.m_events = None
        self.m_anonid = 0
        self.m_dsn = dsn
        self.m_pool = []
        self.m_tsd = threading.local()
        self.m_lock = threading.Lock()
        self._setup_exception()
        self._set_pool_size(2)

    @classmethod
    def _create(cls, api):
        """Try to load a user defined database manager."""
        config = api.config.ns('draco2.database.manager')
        interface = config.get('interface')
        if not interface:
            m = 'Required option "interface" not set in config file ' \
                'section [draco2.database.manager].'
            raise DatabaseInterfaceError, m
        if interface == 'psycopg2':
            from draco2.database.dbpsycopg2 import Psycopg2DatabaseManager
            cls = Psycopg2DatabaseManager
        elif interface == 'mysqldb':
            from draco2.database.dbmysqldb import MySQLdbDatabaseManager
            cls = MySQLdbDatabaseManager
        else:
            m = 'Unknown database interface `%s\' in config file.'
            raise DatabaseInterfaceError, m % interface
        dsn = config.get('dsn')
        if not dsn:
            m = 'Required option "dsn" not set in config file section [%s].'
            raise DatabaseInterfaceError, m % 'draco2.database.manager'
        manager = cls(dsn)
        poolsize = config.get('poolsize')
        if poolsize is not None:
            manager._set_pool_size(poolsize)
        if hasattr(api, 'changes'):
            manager._set_change_manager(api.changes)
        if hasattr(api, 'events'):
            manager._set_event_manager(api.events)
        return manager

    def _finalize(self):
        """Finalize a request. This closes all connections that haven't been
        closed already."""
        try:
            connections = self.m_tsd.connections.values()
        except AttributeError:
            connections = []
        for conn in connections:
            try:
                conn.rollback()
                if len(self.m_pool) < self.m_pool_size:
                    self.m_pool.append(conn)
                else:
                    conn.close()
            except DatabaseDBAPIError:
                pass
        self.m_tsd.__dict__.clear()

    def _set_change_manager(self, changes):
        """Use change manager `changes'."""
        ctx = changes.get_context('draco2.core.config')
        ctx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Change callback."""
        config = api.config.ns('draco2.database.manager')
        poolsize = config.get('poolsize')
        if poolsize is not None:
            self._set_pool_size(poolsize)
        logger = logging.getLogger('draco2.database.manager')
        logger.info('Reloaded configuration (change detected).')

    def _setup_exception(self):
        """Reconfigure dbapi.Error such that it becomes a subclass
        of DatabaseDBAPIError."""
        self.m_lock.acquire()
        try:
            exc = self.dbapi().Error
            if DatabaseDBAPIError not in exc.__bases__:
                exc.__bases__ += (DatabaseDBAPIError,)
        finally:
            self.m_lock.release()

    def _set_event_manager(self, eventmgr):
        """Set the event manager to use."""
        self.m_events = eventmgr

    def _set_pool_size(self, size):
        """Set the size of the connection pool."""
        self.m_pool_size = size

    def dbapi(self):
        """Return the DB-API for this interface."""
        raise NotImplementedError

    def dialect(self):
        """Return the dialect instance."""
        raise NotImplementedError

    def dump_command(self, schema=None, output=None):
        """Return a shell command that will dump the database."""
        raise NotImplementedError

    def set_isolation_level(self, connection, level):
        """Set the transaction isolation level on `connection' to `level'."""
        raise NotImplementedError

    def set_client_encoding(self, connection, encoding):
        """Set the client encoding to `encoding'."""
        raise NotImplementedError

    def is_serialization_error(self, exception):
        """Return True if `exception' is a serialization error."""
        raise NotImplementedError

    def _connect(self, isolation_level=None, encoding=None):
        """Create a new database connection."""
        raise NotImplementedError

    def _get_name(self):
        """Return a new anonymous name."""
        self.m_lock.acquire()
        try:
            anonid = self.m_anonid
            self.m_anonid += 1
        finally:
            self.m_lock.release()
        name = 'anon/%d' % anonid
        return name

    def _ping(self, connection):
        """Ping a conneciton and return True if the connection is alive."""
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT True')
            row = cursor.fetchone()
            return row is not None and row[0] is True
        except DatabaseDBAPIError:
            return False

    def connection(self, name=None):
        """Return a new (named) connection.

        If `name' is not given, a new anonymous connection is created.
        """
        if name is None:
            name = self._get_name()
        logger = logging.getLogger('draco2.database.manager')
        self.m_lock.acquire()
        try:
            try:
                conn = self.m_tsd.connections[name]
            except AttributeError:
                self.m_tsd.connections = {}
            except KeyError:
                pass
            else:
                return conn
            if self.m_pool:
                conn = self.m_pool.pop()
                if not self._ping(conn):
                    logger.error('Persistent connection lost, reconnecting.')
                    conn = self._connect()
                self.m_tsd.connections[name] = conn
            else:
                conn = self._connect()
                self.m_tsd.connections[name] = conn
        finally:
            self.m_lock.release()
        if self.m_events:
            self.m_events.raise_event('configure_database_connection', conn)
        return conn
