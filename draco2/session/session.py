# vi: ts=8 sts=4 sw=4 et
#
# session.py: session management
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import sys
import datetime
import logging

from draco2.util.http import Cookie
from draco2.util.serialize import loads, dumps
from draco2.util.namespace import DictNamespace
from draco2.core.model import Session as SessionObject
from draco2.session.exception import SessionError
from draco2.session.namespace import SessionNamespace
from draco2.session.util import dump_sessionid, generate_sessionid


class SessionInterface(object):
    """The session management interface."""

    @classmethod
    def _create(cls, api):
        """Factory method."""
        raise NotImplementedError

    def load(self, sessionid):
        """Load an exisiting session."""
        raise NotImplementedError

    def new(self):
        """Create a new session."""
        raise NotImplementedError

    def destroy(self):
        """Destroy the current session."""
        raise NotImplementedError

    def sessionid(self):
        """Return the session ID."""
        raise NotImplementedError

    def set_timeout(self, timeout):
        """Set the default session timeout. """
        raise NotImplementedError

    def create_date(self):
        """Return the creation date of this session."""
        raise NotImplementedError

    def expire_date(self):
        """Return the expiration date of this session."""
        raise NotImplementedError

    def enter_subsession(self):
        """Push a new subsession on the subsession stack."""
        raise NotImplementedError

    def leave_subsession(self):
        """Pop a subsession."""
        raise NotImplementedError

    def clear_subsessions(self):
        """Clear the subsesion stack."""
        raise NotImplementedError

    def namespace(self, scope=None, subsession=True):
        """Return the session namespace with scope `scope'."""
        raise NotImplementedError

    ns = namespace

    def commit(self):
        """Commit the session (flushes namespaces)."""
        raise NotImplementedError


class Session(object):
    """Session management object.

    This class represents a single HTTP session.
    """

    def __init__(self, request, response, transaction,
                 security=None, events=None):
        """Constructor."""
        self.m_session = None
        self.m_sessionid = None
        self.m_request = request
        self.m_response = response
        self.m_transaction = transaction
        self.m_security = security
        self.m_events = events
        self.m_namespaces = {}
        self.set_timeout(7200)  # two hours

    def load(self, sessionid):
        """Load an existing session."""
        if not sessionid[0]:
            return False
        # Lock the session. Every session is updated at each request.
        # Without locking, this would lead to serialization errors (and thus
        # transaction retries) with every concurrent request. Therefore
        # better prevent concurrent request (this is the hypothesis, at
        # least).
        result = self.m_transaction.select(SessionObject, 'id=%s',
                                           (sessionid[0],), lock=True)
        if not result:
            return False
        session = result[0]
        if not self._check(session):
            return False
        self._update(session)
        self.m_session = session
        self.m_sessionid = sessionid
        return True

    def _check(self, session):
        """Check session object `session'."""
        logger = logging.getLogger('draco2.session.session')
        # Once a session has been logged in we don't allow it to be used
        # without credentials anymore. The theory is that these sessions
        # may contain sensitive data and therefore we want as least as
        # much protection as the security context provides us.
        if self.m_security and session['principal'] and \
                session['principal'] != self.m_security.principal():
            logger.info('Session principal mismatch.')
            self.m_transaction.delete(session)
            return False
        now = datetime.datetime.now()
        if session['expire_date'] <= now:
            logger.warning('Client provided expired session id.')
            return False
        return True

    def _update(self, session):
        """Update time stamps in session object `session'."""
        updates = {}  # Batch updates
        updates['principal'] = self.m_security.principal()
        now = datetime.datetime.now()
        updates['last_used'] = now
        expire_date = now + datetime.timedelta(seconds=self.m_timeout)
        updates['expire_date'] = expire_date
        session.update(updates)
        cookie = Cookie('draco-session', session['id'],
                        expires=expire_date, path='/')
        self.m_response.set_cookie(cookie)

    def new(self):
        """Create a new session."""
        session = SessionObject()
        sessionid = generate_sessionid()
        session['id'] = sessionid[0]
        session['last_subsession'] = sessionid[1]
        session['principal'] = self.m_security.principal()
        now = datetime.datetime.now()
        session['create_date'] = now
        session['last_used'] = now
        expire_date = now + datetime.timedelta(seconds=self.m_timeout)
        session['expire_date'] = expire_date
        self.m_transaction.insert(session)
        value = dump_sessionid((sessionid[0], None))
        cookie = Cookie('draco-session', value, expires=expire_date, path='/')
        self.m_response.set_cookie(cookie)
        self.m_session = session
        self.m_sessionid = sessionid

    def destroy(self):
        """Destroy the current session."""
        if not self.m_session:
            return
        self.m_transaction.delete(self.m_session)
        expired = datetime.datetime(1970, 1, 1)
        cookie = Cookie('draco-session', '', expires=expired, path='/')
        self.m_response.set_cookie(cookie)
        self.m_session = None
        self.m_sessionid = None

    def sessionid(self):
        """Return the session ID."""
        return self.m_sessionid

    def set_timeout(self, timeout):
        """Set the default session timeout. """
        self.m_timeout = timeout

    def create_date(self):
        """Return the creation date of this session."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        return self.m_session['create_date']

    def expire_date(self):
        """Return the expiration date of this session."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        return self.m_session['expire_date']

    def _next_subsession(self):
        """Allocate a new subsession."""
        subsession = self.m_session['last_subsession'] + 1
        subsession = subsession % sys.maxint
        self.m_session['last_subsession'] = subsession
        return subsession

    def enter_subsession(self, name=None):
        """Push a new subsession on the subsession stack."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        parent = self.m_sessionid[1]
        child = self._next_subsession()
        self.m_sessionid = (self.m_sessionid[0], child)
        ns = self.namespace('__draco2__')
        ns['parent'] = parent
        ns['name'] = name

    enter = enter_subsession

    def leave_subsession(self):
        """Pop a subsession."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        ns = self.namespace('__draco2__')
        try:
            parent = ns['parent']
        except KeyError:
            return
        self.m_sessionid = (self.m_sessionid[0], parent)

    leave = leave_subsession

    def clear_subsessions(self):
        """Clear the subsesion stack."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        self.m_sessionid = (self.m_sessionid[0], 0)

    clear = clear_subsessions

    def namespace(self, scope=None, subsession=True):
        """Return the session namespace with scope `scope'."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        if callable(scope):
            scope = self.m_response.patch_uri(scope)
        elif scope is None:
            scope = '__default__'
        if subsession:
            scope = '%s/%d' % (scope, self.m_sessionid[1])
        try:
            ns = self.m_namespaces[scope]
        except KeyError:
            ns = SessionNamespace(self.m_session['id'], scope, self.m_transaction)
            self.m_namespaces[scope] = ns
        return ns

    ns = namespace

    def globals(self, scope=None):
        """Return a global namespace with scope `scope'."""
        return self.namespace(scope, False)

    def locals(self, scope=None):
        """Return a local namespace with scope `scope'."""
        return self.namespace(scope, True)

    def commit(self):
        """Commit the session (flushes namespaces)."""
        if not self.m_session:
            raise SessionError, 'Session not initialized.'
        for ns in self.m_namespaces.values():
            ns.flush()
        self.m_namespaces.clear()


class DummySession(SessionInterface):
    """A dummy session.

    This session is allocated to web robots. Using a dummy session
    instead of setting api.session to "None" allows for the same code
    path for web robots and normal clients.
    """

    def __init__(self):
        """Constructor."""
        self.m_namespaces = {}
        self.set_timeout(7200)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        session = cls()
        session.new()
        return session

    def load(self, sessionid):
        """Load an exisiting session."""
        return False

    def new(self):
        """Create a new session."""
        self.m_subsession = 0
        self.m_create_date = datetime.datetime.now()
        self.m_expire_date = self.m_create_date
        self.m_expire_date += datetime.timedelta(self.m_timeout)

    def destroy(self):
        """Destroy the current session."""

    def sessionid(self):
        """Return the session ID."""
        return None

    def set_timeout(self, timeout):
        """Set the default session timeout. """
        self.m_timeout = timeout

    def create_date(self):
        """Return the creation date of this session."""
        return self.m_create_date

    def expire_date(self):
        """Return the expiration date of this session."""
        return self.m_expire_date

    def enter_subsession(self, name=None):
        """Push a new subsession on the subsession stack."""
        self.m_subsession += 1

    enter = enter_subsession

    def leave_subsession(self):
        """Pop a subsession."""
        if self.m_subsession > 0:
            self.m_subsession -= 1

    leave = leave_subsession

    def clear_subsessions(self):
        """Clear the subsesion stack."""
        self.m_subsession = 0

    clear = clear_subsessions

    def namespace(self, scope=None, subsession=True):
        """Return the session namespace with scope `scope'."""
        if callable(scope):
            scope = self.m_response.resolve_uri(scope)
        elif scope is None:
            scope = '__default__'
        if subsession:
            scope = '%s/%d' % (scope, self.m_subsession)
        try:
            ns = self.m_namespaces[scope]
        except KeyError:
            ns = DictNamespace()
            self.m_namespaces[scope] = ns
        return ns

    ns = namespace

    def globals(self, scope=None):
        """Return a global namespace with scope `scope'."""
        return self.namespace(scope, False)

    def locals(self, scope=None):
        """Return a local namespace with scope `scope'."""
        return self.namespace(scope, True)

    def commit(self):
        """Commit the session (flushes namespaces)."""
