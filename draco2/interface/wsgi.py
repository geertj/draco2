# vi: ts=8 sts=4 sw=4 et
#
# wsgi.py: web server gateway interface
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

from draco2.interface.interface import HTTPInterface
from draco2.core.dispatch import handle_request


class WSGIInterface(HTTPInterface):
    """Implements the Draco HTTP interface for WSGI."""

    def __init__(self, environ, start_response):
        """Create a WSGI interface from a WSGI environ object."""
        self.m_environ = environ
        self.m_start_response = start_response

    def read(self, size=None):
        input = self.m_environ['wsgi.input']
        if size is None:
            args = ()
        else:
            args = (size,)
        buffer = input.read(*args)
        return buffer

    def readline(self, size=None):
        # The `size' parameter is not supported for WSGI
        # Do we need to emulate it?
        input = self.m_environ['wsgi.input']
        line = input.readline()
        return line

    def send_header(self):
        status = self.status()
        status = '%d %s' % (status, http.http_reason_strings[status])
        headers = []
        headers_out = self.headers_out()
        for key in headers_out:
            for value in headers_out[key]:
                headers.append((key, value))
        self.m_writer = self.m_start_response(status, headers_out)

    def write(self, buffer):
        pass
        


def handler(environ, start_response):
    iface = WSGIInterface(environ, start_response)
    handle_request(iface)
    return ifaca.exit_status()
