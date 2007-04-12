# vi: ts=8 sts=4 sw=4 et
#
# x509.py: certificate based scheme
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


class X509Authentication(AuthenticationScheme):
    """X509 based security scheme.

    This scheme uses x509 client certificates exchanged during an
    SSLv3/TLS handshake for authentication.
    """

    name = 'x509'

    def __init__(self, request, response, transaction):
        """Constructor."""
        super(X509Authentication, self).__init__(request, response,
                                                 transaction)
        self.m_principal = None

    def authenticate(self):
        """Authenticate the request."""
        if not self.m_request.isssl():
            return False
        clientdn = self.m_request.ssl_variable('SSL_CLIENT_S_DN')
        if not clientdn:
            return False
        result = self.m_transaction.select(Principal, 'certificate_dn = %s',
                                           (clientdn,))
        if not result:
            return False
        self.m_principal = result[0]
        return True

    def principal(self):
        """Return the principal name if authenticated."""
        if self.m_principal:
            return self.m_principal['name']
