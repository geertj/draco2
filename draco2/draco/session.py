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

from draco2.session.util import issessionid, parse_sessionid
from draco2.session.session import Session, DummySession


class DracoSession(Session):
    """Draco session object.

    A draco session retrieves its session ID from the HTTP cookie
    c.q. the HTTP request URL.
    """

    def _get_sessionid(self):
        """Return session id and subsession."""
        sessionid = self.m_request.session()
        if sessionid and issessionid(sessionid):
            basesession, subsession = parse_sessionid(sessionid)
        else:
            basesession, subsession = None, None
        if basesession is None:
            cookie = self.m_request.cookie('draco-session')
            if cookie and issessionid(cookie.value):
                basesession, dummy = parse_sessionid(cookie.value)
        if subsession is None:
            subsession = 0
        return (basesession, subsession)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        if api.request.isrobot():
            session = DummySession._create(api)
            return session
        transaction = api.models.model('draco').transaction('shared')
        session = cls(api.request, api.response, transaction,
                      api.security, api.events)
        config = api.config.ns('draco2.draco.session')
        if config.has_key('timeout'):
            session.set_timeout(config['timeout'])
        sessionid = session._get_sessionid()
        if not sessionid[0] or not session.load(sessionid):
            session.new()
        return session
