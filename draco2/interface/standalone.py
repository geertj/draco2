# vi: ts=8 sts=4 sw=4 et
#
# standalone.py: standalone webserver interface
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import socket

from draco2.util import http
from draco2.interface.interface import HTTPInterface


class StandaloneInterface(HTTPInterface):
    """An interface that can be used stand-alone."""

    def __init__(self, proto, method, uri, headers, conn,
                 local_addr, remote_addr, options):
        self._set_protocol(proto)
        self._set_method(method)
        self._set_uri(uri)
        self._set_headers_in(headers)
        self._set_headers_out({})
        self._set_local_address(local_addr)
        self._set_remote_address(remote_addr)
        self._set_options(options)
        self._set_header_sent(False)
        self._set_username(None)
        self._set_isssl(False)
        self._set_ssl_variables({})
        self.set_status(http.HTTP_OK)
        self.set_error(None)
        self.m_conn = conn
        self.m_options = options
        self.m_sent_header = False
        super(StandaloneInterface, self).__init__()

    def read(self, size=None):
        if size is None:
            try:
                size = self.header('content-length')
            except (TypeError, ValueError):
                size = 0
        return self.m_conn.read(size)

    def readline(self):
        return self.m_conn.readline()

    def send_header(self):
        if self.header_sent():
            return
        reason = http.http_reason_strings[self.status()]
        self.m_conn.write('%s %s %s\r\n' % (self.protocol(), self.status(), reason))
        for name in self.headers_out():
            for value in self.headers_out()[name]:
                self.m_conn.write('%s: %s\r\n' % (name, value))
        self.m_conn.write('\r\n')
        self._set_header_sent(True)

    def write(self, buffer):
        if not self.m_sent_header:
            self.send_header()
        try:
            self.m_conn.write(buffer)
        except socket.error:
            raise IOError, 'Error writing to socket.'
