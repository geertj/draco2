# vi: ts=8 sts=4 sw=4 et
#
# draco.py: draco authentication scheme
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import logging
import datetime

from draco2.util.http import Cookie
from draco2.core.model import SecurityContext
from draco2.security.util import (isauthtoken, generate_authtoken,
                                  parse_authtoken)
from draco2.security.scheme import AuthenticationScheme


class DracoAuthentication(AuthenticationScheme):
    """Draco security scheme.

    The Draco security scheme is a form/cookie based scheme using
    password authentication.
    """

    name = 'draco'

    def __init__(self, request, response, transaction):
        """Constructor."""
        super(DracoAuthentication, self).__init__(request, response,
                                                  transaction)
        self.m_context = None
        self.set_timeout(3600)
        self.set_secure(False)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        scheme = super(DracoAuthentication, cls)._create(api)
        config = api.config.namespace('draco2.security.draco')
        if config.has_key('timeout'):
            scheme.set_timeout(config['timeout'])
        if config.has_key('secure'):
            scheme.set_secure(config['secure'])
        return scheme

    def set_timeout(self, timeout):
        """Set the timeout value."""
        self.m_timeout = timeout

    def set_secure(self, secure):
        """Set secure flag."""
        self.m_secure = secure

    def authenticate(self):
        """Authenticate, return True if authenticated."""
        cookie = self.m_request.cookie('draco-authtoken')
        if not cookie:
            return False
        logger = logging.getLogger('draco2.security.draco')
        if not isauthtoken(cookie.value):
            logger.info('Client provides illegal authentication token.')
            return False
        authtok = parse_authtoken(cookie.value)
        result = self.m_transaction.select(SecurityContext,
                                           'token = %s', (authtok,))
        if not result:
            logger.info('Client provided unknown authentication token.')
            return False
        context = result[0]
        if self.m_secure and not self.m_request.isssl():
            logger.error('Client provided authentication token w/o ssl.')
            self.m_transaction.delete(context)  # remove exposed context
            return False
        now = datetime.datetime.now()
        if context['expire_date'] <= now:
            logger.info('Client provided expired authentication token.')
            return False
        updates = {}  # batch updates
        updates['last_used'] = now
        expire_date = now + datetime.timedelta(seconds=self.m_timeout)
        updates['expire_date'] = expire_date
        context.update(updates)
        cookie = Cookie('draco-authtoken', context['token'],
                        expires=expire_date, path='/', secure=self.m_secure)
        self.m_response.set_cookie(cookie)
        self.m_context = context
        return True

    def principal(self):
        """Return the principal name that was authenticated."""
        if self.m_context:
            return self.m_context['principal']

    def login(self, principal):
        """Perform a logon for the "draco" scheme."""
        context = SecurityContext()
        context['token'] = generate_authtoken()
        context['principal'] = principal
        now = datetime.datetime.now()
        context['create_date'] = now
        context['last_used'] = now
        expire_date = now + datetime.timedelta(seconds=self.m_timeout)
        context['expire_date'] = expire_date
        self.m_transaction.insert(context)
        cookie = Cookie('draco-authtoken', context['token'],
                        expires=expire_date, path='/', secure=self.m_secure)
        self.m_response.set_cookie(cookie)
        self.m_context = context

    def logout(self):
        """Perform a logout for the "draco" scheme."""
        if not self.m_context:
            return
        expired = datetime.datetime(1970, 1, 1)
        cookie = Cookie('draco-authtoken', '', expires=expired, path='/',
                        secure=self.m_secure)
        self.m_response.set_cookie(cookie)
        self.m_transaction.delete(self.m_context)
        self.m_context = None
