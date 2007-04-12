#!/usr/bin/env python
#
#
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
# All rights are reserved.

import sys
import os
import socket
import logging
import optparse
import thread
import threading
import time
import tempfile

from draco2.command.command import Command


class ConnectionHandler(object):
    """Base class for connection handlers."""

    def __init__(self, socket, options):
        """Constructor."""
        self.m_socket = socket
        self.m_options = options

    def handle(self):
        """Handle a single connection."""
        from draco2.util import http
        from draco2.util.misc import get_backtrace
        from draco2.interface.standalone import StandaloneInterface
        from draco2.core.dispatch import handle_request

        logger = logging.getLogger('draco2.serve')
        logger.debug('Thread %s' % thread.get_ident())

        conn = self.m_socket.makefile()
        local_addr = self.m_socket.getsockname()
        remote_addr = self.m_socket.getpeername()
        try:
            proto, method, uri, headers = http.parse_request(conn)
        except http.HTTPError, err:
            http.simple_response(conn, err.status(), err.headers(), err.message())
            logger.debug('Response %s' % err.status())
            self.m_socket.close()
            return
        try:
            start = time.time()
            logger.debug('Request for %s (%s)' % (uri, method))
            iface = StandaloneInterface(proto, method, uri, headers,
                                        conn, local_addr, remote_addr,
                                        self.m_options)
            handle_request(iface)
            content_type = iface.headers_out().get('content-type', [''])[0]
            logger.debug('Response %s (%s)' % (iface.status(), content_type))
            end = time.time()
            logger.debug('Request %s took %.2f seconds.' % (uri, end-start))
        except IOError:
            pass
        except:
            message = get_backtrace()
            logger.debug(message)
        conn.close()
        self.m_socket.close()

    def start(self):
        raise NotImplementedError

    @classmethod
    def cleanup(self):
        pass


class ThreadedConnectionhandler(ConnectionHandler):
    """Connection handler that starts a thread for each request."""

    def __init__(self, *args):
        super(ThreadedConnectionhandler, self).__init__(*args)
        self.m_thread = None

    def start(self):
        self.m_thread = threading.Thread(target=self.handle)
        self.m_thread.start()


class ForkedConnectionHandler(ConnectionHandler):
    """Connection handler that forks for each request.

    This handler works on Unix only.
    """

    def __init__(self, *args):
        super(ForkedConnectionHandler, self).__init__(*args)

    def handle(self):
        super(ForkedConnectionHandler, self).handle()
        os._exit(os.EX_OK)

    def start(self):
        pid = os.fork()
        if pid == 0:
            self.handle()
        else:
            self.m_pid = pid
            self.m_socket.close()

    @classmethod
    def cleanup(self):
        pgrp = os.getpgrp()
        while True:
            try:
                pid, status = os.waitpid(-pgrp, os.WNOHANG)
            except OSError:
                break


class ServeCommand(Command):
    """Serve Draco commands using the builtin web server."""

    name = 'serve'
    description = 'start builtin web server'
    require_api = set(('options',))

    def _server_loop(self, address):
        """Stand-alone server loop."""
        logger = logging.getLogger('draco2.serve')
        sock = socket.socket(socket.AF_INET)
        sock.bind(address)
        sock.listen(1)
        logger.debug('Listening on %s:%d.' % address)
        logger.debug('Entering server loop.')
        while True:
            logger.debug('Waiting for new connection.')
            conn, remote_addr = sock.accept()
            logger.debug('New connection from %s:%s' % remote_addr)
            handler = self.handler_class(conn, self.options)
            handler.start()
            self.handler_class.cleanup()
            if self.opts.singleshot:
                break

    def _setup_logger(self):
        """Set up the `dracoserve' logger."""
        logger = logging.getLogger('draco2')
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _get_listen_address(self, address, defport):
        """Parse the listen address."""
        if address:
            parts = address.split(':')
            if len(parts) == 1:
                hostname = parts[0]
                port = defport 
            elif len(parts) == 2:
                hostname, port = parts
            else:
                return
        else:
            hostname = socket.gethostname()
            port = defport
        addr = socket.gethostbyname(hostname)
        port = int(port)
        return (addr, port)

    def add_options(self, group):
        group.add_option('-a', '--address', action='store',
                         dest='address', help='bind to this address')
        group.add_option('-F', '--forked', action='store_true',
                         dest='forked', help='use forked connection handler')
        group.add_option('-T', '--threaded', action='store_false',
                         dest='forked',
                         help='use threaded connection handler')
        group.add_option('-s', '--single-shot', action='store_true',
                         dest='singleshot', help='serve just one request')
        group.add_option('-d', '--debug', action='store_true',
                         dest='debug', help='enable debugging')
        group.add_option('-p', '--profile', action='store_true',
                         dest='profile', help='enable profiling')

    def set_defaults(self, parser):
        parser.set_default('forked', sys.platform != 'win32')
        parser.set_default('singleshot', False)
        parser.set_default('debug', False)
        parser.set_default('profile', False)

    def run(self, opts, args, api):
        """Main function."""
        self.docroot = api.options['documentroot']
        if opts.debug:
            api.options['debug'] = True
        if opts.profile:
            api.options['profile'] = True
        self.options = api.options
        if opts.forked:
            self.handler_class = ForkedConnectionHandler
        else:
            self.handler_class = ThreadedConnectionhandler
        address = self._get_listen_address(opts.address, defport=80)
        if not address:
            parser.error('illegal address: %s' % address)
        self._setup_logger()
        self.opts = opts
        self._server_loop(address)
