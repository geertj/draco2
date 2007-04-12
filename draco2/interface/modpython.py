# vi: ts=8 sts=4 sw=4 et
#
# modpython.py: mod_python intergration interface
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
from mod_python import apache

from draco2.util import http
from draco2.interface.interface import HTTPInterface
from draco2.core.dispatch import handle_request


class ModPythonInterface(HTTPInterface):
    """Draco2 interface for Apache/mod_python."""

    def __init__(self, mpreq):
        self.m_mpreq = mpreq
        self._set_header_sent(False)
        self._set_protocol(mpreq.protocol)
        self._set_method(mpreq.method)
        self._set_uri(mpreq.unparsed_uri)
        self._init_headers()
        self._set_local_address(mpreq.connection.local_addr)
        self._set_remote_address(mpreq.connection.remote_addr)
        self._init_options()
        self._init_username()
        self._init_ssl()
        self.set_status(http.HTTP_OK)
        self.set_error(None)
        self.m_sent_header = False
        super(ModPythonInterface, self).__init__()

    def _init_options(self):
        options = {}
        for key in self.m_mpreq.get_options():
            value = self.m_mpreq.get_options()[key]
            options[key.lower()] = value
        docroot = os.path.normpath(self.m_mpreq.document_root())
        options['documentroot'] = docroot
        self._set_options(options)

    def _init_headers(self):
        headers_in = {}
        for key in self.m_mpreq.headers_in.keys():
            value = self.m_mpreq.headers_in[key]
            if not isinstance(value, list):
                value = [value]
            headers_in[key.lower()] = value
        self._set_headers_in(headers_in)
        self._set_headers_out({})

    def _init_username(self):
        self.m_mpreq.get_basic_auth_pw()  # see mod_python docs
        self._set_username(self.m_mpreq.user)

    def _init_ssl(self):
        env = self.m_mpreq.subprocess_env
        isssl = env.get('HTTPS')
        self._set_isssl(isssl)
        vars = {}
        for key in env:
            if key.startswith('HTTPS') or key.startswith('SSL'):
                vars[key] = env[key]
        self._set_ssl_variables(vars)

    def read(self, size=None):
        if size is None:
            args = ()
        else:
            args = (size,)
        return self.m_mpreq.read(*args)

    def readline(self, size=None):
        if size is None:
            args = ()
        else:
            args = (size,)
        return self.m_mpreq.readline(*args)

    def send_header(self):
        if self.header_sent():
            return
        self.m_mpreq.status = self.status()
        headers_out = self.headers_out()
        try:
            self.m_mpreq.content_type = headers_out['content-type'][0]
            del headers_out['content-type']
        except KeyError:
            pass
        status_class = self.status() - self.status() % 100
        for key in headers_out:
            for value in headers_out[key]:
                if status_class in (100, 200):
                    self.m_mpreq.headers_out.add(key, value)
                else:
                    self.m_mpreq.err_headers_out.add(key, value)
        self.m_mpreq.send_http_header()
        self._set_header_sent(True)

    def write(self, buffer):
        self.m_mpreq.write(buffer)

    def local_hostname(self):
        return self.m_mpreq.hostname

    def exit_status(self):
        return apache.OK


def handler(mpreq):
    """The mod_python request handler."""
    iface = ModPythonInterface(mpreq)
    handle_request(iface)
    return iface.exit_status()
