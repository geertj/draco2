# vi: ts=8 sts=4 sw=4 et
#
# request.py: request object for Draco handlers
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

from draco2.util import http
from draco2.util import uri as urilib


class Request(object):
    """The request object."""

    def __init__(self, iface):
        """Constructor."""
        self.m_iface = iface
        self.m_headers = iface.headers_in()
        self._parse_uri()
        self._init_cookies()

    @classmethod
    def _create(cls, api):
        """Factory method."""
        request = cls(api.iface)
        return request

    def _parse_uri(self):
        """Parse the request URI."""
        uri = self.m_iface.uri()
        docroot = self.m_iface.options()['documentroot']
        protocol, host, path, args = urilib.parse_uri(uri)
        directory, filename, pathinfo = urilib.resolve_path_uri(path, docroot)
        self.m_docroot = docroot
        self.m_directory = directory
        self.m_filename = filename
        self.m_pathinfo = [ pi for pi in pathinfo.split('/') if pi ]
        self.m_args = {}
        args = urilib.parse_query(args)
        self._add_args(args)
        if self.m_iface.method() == 'POST':
            ctype = self.header('content-type')
            if ctype is not None:
                value, options = http.parse_header_options(ctype)
                if value in ('application/x-www-form-urlencoded',
                             'multipart/form-data'):
                    args = http.parse_post(self.headers(), self)
                    self._add_args(args)
        self.m_basename, self.m_extension = os.path.splitext(self.filename())
        self.m_extension = self.m_extension[1:]

    def protocol(self):
        """Return the protocol version.
        
        The protocol is returned as an upper case string in the format
        described by the RFC, e.g. 'HTTP/1.1'
        """
        return self.m_iface.protocol()

    def method(self):
        """Return the HTTP method.
        
        Method names are case sensitive. All HTTP methods are upper-case,
        e.g. 'GET', 'HEAD' and 'POST'.
        """

        return self.m_iface.method()

    def uri(self):
        """Return the request URI."""
        return self.m_iface.uri()

    def docroot(self):
        """Return the document root."""
        return self.m_docroot

    def directory(self):
        """Return the directory name from the URI.
        
        As this entity is a part of the URI, it contains forward slash
        path separators, independent of ths OS.
        """
        return self.m_directory

    def filename(self):
        """Return the name of the Draco template.

        The template name always ends with the configured
        extension.
        """
        return self.m_filename

    def basename(self):
        """Return the base name of the request file name."""
        return self.m_basename

    def extension(self):
        """Return the extension of the request file name."""
        return self.m_extension

    def pathinfo(self):
        """Return extra path components.

        This function returns the extra path components, that are
        optionally present after the template. The components are
        returned as a list of strings, with empty items removed.
        """
        return self.m_pathinfo

    def _add_args(self, args):
        """Add GET/POST arguments."""
        for name in args:
            for value in args[name]:
                curval = self.m_args.get(name)
                if curval is None:
                    self.m_args[name] = value
                elif isinstance(curval, list):
                    self.m_args[name].append(value)
                else:
                    self.m_args[name] = [self.m_args[name], value]

    def args(self):
        """Return the GET and POST query arguments.

        The result is a dictionary with string, FileUpload or list of 
        string/FileUpload values and string keys.
        """
        return self.m_args

    def header(self, name, default=None):
        """Return the value of HTTP header `name'.

        If multiple values are present, the first one is returned.
        If the header does not exist, `default' is returned.
        """
        return self.m_headers.get(name.lower(), [default])[0]

    def headers(self):
        """Return a dictionary of headers."""
        return self.m_headers

    def _init_cookies(self):
        self.m_cookies = {}
        cookie = self.header('Cookie')
        if not cookie:
            return
        try:
            cookies = http.parse_cookie(cookie)
        except ValueError:
            return
        self.m_cookies = cookies

    def cookie(self, name):
        """Return the value of the named cookie `name'."""
        try:
            return self.m_cookies[name][0]
        except KeyError:
            return None

    def cookies(self):
        """Return the parsed cookies as a dictionary."""
        return self.m_cookies

    def internal_redirect(self, uri):
        """Redirect the request."""
        self.m_iface.internal_redirect(uri)
        self._parse_uri()

    def username(self):
        """Return the HTTP authenticated username, or None."""
        return self.m_iface.username()

    def isssl(self):
        """Return True if the connection was a secure connection."""
        return self.m_iface.isssl()

    def ssl_variable(self, name):
        """Return SSL variable `name', or None."""
        return self.m_iface.ssl_variables().get(name.upper())

    def ssl_variables(self):
        """Return a dictionary with all SSL variables."""
        return self.m_iface.ssl_variables()

    def read(self, size=None):
        """Read up to `size' bytes from the input.

        If size is not specified, the `Content-Length' header is used
        to determine the input size.
        """
        return self.m_iface.read(size)

    def readline(self):
        """Read a single line of input."""
        return self.m_iface.readline()

    def local_address(self):
        """Return the local address of the request connection as
        a (IP, port) tuple."""
        return self.m_iface.local_address()

    def local_hostname(self):
        """Return the local host name of the request connection."""
        return self.m_iface.local_hostname()

    def remote_address(self):
        """Return the remote address of the request connection as
        a (IP, port) tuple."""
        return self.m_iface.remote_address()

    def remote_hostname(self):
        """Return the remote host name of the request connection."""
        return self.m_iface.remote_hostname()

    def servername(self):
        """Return the web server name."""
        return self.m_iface.servername()
