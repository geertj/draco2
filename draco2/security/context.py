# vi: ts=8 sts=4 sw=4 et
#
# security.py: security contexts
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import logging

from draco2.core.model import Principal, Role, PrincipalRoleRelationship
from draco2.security.scheme import AuthenticationScheme
from draco2.security.draco import DracoAuthentication
from draco2.security.http import HttpAuthentication
from draco2.security.x509 import X509Authentication


class SecurityContext(object):
    """Security context.

    This object defines the security context of a request. It provides
    access to a principal name, schemes that were used to authenticate,
    and current roles.

    The only authentication schema actually implemented here is Draco
    authentication. All other schemes must be implemented by the web server.
    """

    def __init__(self, request, response, transaction):
        """Constructor."""
        self.m_request = request
        self.m_response = response
        self.m_transaction = transaction
        self.m_principal = None
        self.m_schemes = {}
        self.m_authschemes = []
        self.m_roles = []

    @classmethod
    def _create(cls, api):
        """Factory method."""
        transaction = api.models.model('draco').transaction('shared')
        context = cls(api.request, api.response, transaction)
        scheme = DracoAuthentication._create(api)
        context.add_scheme(scheme)
        scheme = HttpAuthentication._create(api)
        context.add_scheme(scheme)
        scheme = X509Authentication._create(api)
        context.add_scheme(scheme)
        clslist = api.loader.load_classes('__authenticate__',
                                          AuthenticationScheme,
                                          scope='__docroot__')
        for cls in clslist:
            obj = cls._create(api)
            context.add_scheme(obj)
        context.authenticate()
        return context

    def add_scheme(self, scheme):
        """Add authentication scheme `scheme'."""
        if not isinstance(scheme, AuthenticationScheme):
            m = 'Expecting AuthenticationScheme instance (got %s).'
            raise TypeError, m % type(scheme)
        self.m_schemes[scheme.name] = scheme

    def scheme(self, name):
        """Return the named security scheme."""
        return self.m_schemes[name]

    def authenticate(self):
        """Authenticate all security schemes."""
        # Authenticate all schemes
        principal = None
        authschemes = []
        logger = logging.getLogger('draco2.security.context')
        for scheme in self.m_schemes.values():
            if not scheme.authenticate():
                continue
            # If two scheme authenticate a different principal name, the
            # last one is used.
            if principal and principal != scheme.principal():
                logger.warning('Two schemes authenticated a different name.')
            principal = scheme.principal()
            authschemes.append(scheme.name)
        # Resolve principal
        result = self.m_transaction.select(Principal, 'name = %s',
                                           (principal,))
        if not result:
            return
        self.m_principal = result[0]
        self.m_authschemes = authschemes
        # Get roles
        join = (Role, 'role', PrincipalRoleRelationship, 'INNER')
        roles = self.m_transaction.select(Role, 'principal.id = %s',
                                          (self.m_principal['id'],), join=join)
        self.m_roles = [ role['name'] for role in roles ]

    def securityid(self):
        """Return the security ID.

        This is a unique number that is never reallocated.
        """
        if not self.m_principal:
            return
        return self.m_principal['id']

    def principal(self):
        """Return the principal name or None."""
        if not self.m_principal:
            return
        return self.m_principal['name']

    def schemes(self):
        """Return the authentication schemes the principal has authenticated
        himself with.

        Possible schemes: "http", "draco" and "x509".
        """
        return self.m_authschemes

    def roles(self):
        """Return the roles this principal has."""
        return self.m_roles

    def has_role(self, role):
        """Return True if the principal has `role', False otherwise."""
        return role.lower() in self.m_roles
