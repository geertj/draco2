# vi: ts=8 sts=4 sw=4 et
#
# handler.py: base class for handlers
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
import os.path

from draco2.util import http
from draco2.util import uri as urilib
from draco2.core.exception import *
from draco2.core.request import Request
from draco2.core.response import Response
from draco2.locale.locale import Locale
from draco2.security.context import SecurityContext
from draco2.util.namespace import DictNamespace


class Handler(DictNamespace):
    """Base class for all handlers."""

    Request = Request
    Response = Response
    Locale = None
    Session = None

    allowed_methods = ()
    require_scheme = ()
    require_role = ()

    @classmethod
    def _create(cls, api):
        """Factory function."""
        uri = api.iface.uri()
        docroot = api.options['documentroot']
        scheme, host, path, args = urilib.parse_uri(uri)
        directory, filename, pathinfo = urilib.resolve_path_uri(path, docroot)
        dirname = directory.replace('/', os.sep)
        relname = os.path.join(dirname, '__handler__.py')
        cls = api.loader.load_class(relname, Handler,
                                    scope='__docroot__', default=cls)
        handler = cls()
        return handler

    def _authorize(self, api):
        """Authorize the request."""
        method = api.request.method()
        if method not in self.allowed_methods:
            status = http.HTTP_METHOD_NOT_ALLOWED
            headers = { 'allow': [','.join(self.allowed_methods)] }
            raise HTTPResponse(status, headers=headers)
        if self.require_role and not api.security.principal():
            api.events.raise_event('authentication_required', api)
            raise HTTPResponse, http.HTTP_FORBIDDEN
        for role in self.require_role:
            if role and not api.security.has_role(role):
                api.events.raise_event('insufficient_access', api)
                raise HTTPResponse, http.HTTP_FORBIDDEN
        for scheme in self.require_scheme:
            if scheme not in api.security.schemes():
                api.events.raise_event('insufficient_authentication', api)
                raise HTTPResponse, http.HTTP_FORBIDDEN

    def _dispatch(self, api):
        """Dispatch an HTTP request."""
        self._authorize(api)
        self._handle(api)
