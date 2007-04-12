# vi: ts=8 sts=4 sw=4 et
#
# interface.py: web server integration interface
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os.path
import socket

from draco2.util import http


class HTTPInterface(object):
    """The HTTP server interface.

    This object defines the interface that must be provided to plug
    Draco into a web server.
    """

    ACCEPT = 0
    DECLINE = 1

    def _set_protocol(self, protocol):
        self.m_protocol = protocol

    def protocol(self):
        """Return the protocol version.
        
        The protocol version must used as an upper case string in
        the format described by the RFC, e.g. 'HTTP/1.1'
        """
        return self.m_protocol

    def _set_method(self, method):
        self.m_method = method

    def method(self):
        """Return the HTTP method.
        
        The method must be returned as an upper case string, e.g.
        'GET', 'HEAD' or 'POST'.
        """
        return self.m_method

    def _set_uri(self, uri):
        self.m_uri = uri

    def uri(self):
        """Return the request URI."""
        return self.m_uri

    def _set_headers_in(self, headers_in):
        self.m_headers_in = headers_in

    def headers_in(self):
        """Return all HTTP request headers.

        The headers are returned as a dictionary of lists of strings.
        The dictionary is indexed by lower-case header names.
        """
        return self.m_headers_in

    def read(self, size=None):
        """Read from the HTTP request body.

        Up to `size' bytes are read.
        """
        raise NotImplementedError

    def readline(self):
        """Read a single line of input."""
        raise NotImplementedError

    def set_status(self, status):
        """Set the HTTP response code.

        The `status' argument must be a numeric and valid HTTP
        response code.
        """
        self.m_status = status

    def status(self):
        return self.m_status

    def _set_headers_out(self, headers_out):
        self.m_headers_out = headers_out

    def headers_out(self):
        """Return a dictionary with all response headers.

        The dictionary consists of lists of strings indexed by lower
        case string keys.
        """
        return self.m_headers_out

    def send_header(self):
        """Send the HTTP response header."""
        raise NotImplementedError

    def _set_header_sent(self, header_sent):
        """Set the 'header sent' flag."""
        self.m_header_sent = header_sent

    def header_sent(self):
        """Return True if the HTTP header was already sent."""
        return self.m_header_sent

    def write(self, buf):
        """Write to the HTTP response."""
        raise NotImplementedError

    def _set_options(self, options):
        self.m_options = options

    def options(self):
        """Return options.

        Return options from the web server configuration file that
        provide enough information for Draco to bootstrap its own
        configuration file. The return value is a dictionary with
        string keys and string values, containing at least the
        following keys:

        - documentroot

        The following values are optional:

        - extension
        - configfile
        - logfile
        """
        return self.m_options
    
    def _set_local_address(self, local_address):
        self.m_local_address = local_address
        self.m_local_name = None

    def local_address(self):
        """Return the local address.

        The value returned must be a 2-tuple, constisting of a
        string hostname and a numeric port.
        """
        return self.m_local_address

    def local_hostname(self):
        """Return the local host name.

        This function allows Draco to take advance of DNS lookups that
        are potentially already performed by the web server.
        """
        if self.m_local_name is None:
            self.m_local_name = socket.gethostbyaddr(self.m_local_address[0])[0]
        return self.m_local_name

    def _set_remote_address(self, remote_address):
        self.m_remote_address = remote_address
        self.m_remote_name = None

    def remote_address(self):
        """Return the remote address.

        The value returned must be a 2-tuple, constisting of a
        string hostname and a numeric port.
        """
        return self.m_remote_address

    def remote_hostname(self):
        """Return the remote host name.

        This function allows Draco to take advance of DNS lookups that
        are potentially already performed by the web server.
        """
        if self.m_remote_name is None:
            self.m_remote_name = socket.gethostbyaddr(self.m_remote_address[0])[0]
        return self.m_remote_name

    def servername(self):
        """Returns the web server name.

        This can be different from the local_hostname() in case of
        virtual hosting.
        """
        name = self.headers_in().get('host', [None])[0]
        if not name:
            name = self.local_hostname()
        return name

    def _set_username(self, username):
        """Set the HTTP username."""
        self.m_username = username

    def username(self):
        """Return the HTTP authenticated username, or None."""
        return self.m_username

    def _set_isssl(self, ssl):
        self.m_isssl = ssl

    def isssl(self):
        """Returns whether this request is an SSL/TLS request."""
        return self.m_isssl

    def _set_ssl_variables(self, vars):
        self.m_ssl_variables = vars

    def ssl_variables(self):
        """Return SSL variables (mod_ssl de-facto standard)."""
        return self.m_ssl_variables

    def simple_response(self, status, headers=None, message=None):
        """Provide a simple response."""
        self.set_status(status)
        if headers is None:
            headers = {}
        if message is None:
            message = http.http_reason_strings[status]
        headers['content-type'] = ['text/plain']
        headers['content-length'] = [str(len(message))]
        for name in headers:
            for value in headers[name]:
                try:
                    self.headers_out()[name].append(value)
                except KeyError:
                    self.headers_out()[name] = [value]
        try:
            self.send_header()
            self.write(message)
        except IOError:
            pass

    def internal_redirect(self, uri):
        """Perform an internal redirect.

        The actual redirect is not performed but the interface will look as
        if `uri' was called instead of the original URI."""
        self._set_uri(uri)
        self._set_method('GET')

    def set_error(self, error):
        """Set the error exception to `error'. Error handlers retrieve
        the error from here.
        """
        self.m_error = error

    def error(self):
        """Return the exception that occurred."""
        return self.m_error

    def exit_status(self):
        """Return the exit status to the web server."""
        raise NotImplementedError
