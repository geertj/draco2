# vi: ts=8 sts=4 sw=4 et
#
# http.py: HTTP authentication
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.core.model import Principal
from draco2.security.scheme import AuthenticationScheme


class HttpAuthentication(AuthenticationScheme):
    """HTTP authentication scheme.

    This scheme provides authentication based on HTTP authentication.
    """

    name = 'http'

    def __init__(self, request, response, transaction):
        """Constructor."""
        super(HttpAuthentication, self).__init__(request, response,
                                                 transaction)
        self.m_principal = None

    def authenticate(self):
        """Authenticate, and return a principal or None."""
        user = self.m_request.username()
        if not user:
            return False
        result = self.m_transaction.select(Principal, 'name = %s', (user,))
        if not result:
            return False
        self.m_principal = result[0]
        return True

    def principal(self):
        """Return the principal name, if authenticated."""
        if self.m_principal:
            return self.m_principal['name']
