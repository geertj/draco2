# vi: ts=8 sts=4 sw=4 et
#
# scheme.py: security scheme
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class AuthenticationScheme(object):
    """Base class for authentication schemes."""

    def __init__(self, request, response, transaction):
        """Constructor."""
        self.m_request = request
        self.m_response = response
        self.m_transaction = transaction

    @classmethod
    def _create(cls, api):
        """Factory method."""
        transaction = api.models.model('draco').transaction('shared')
        scheme = cls(api.request, api.response, transaction)
        return scheme
