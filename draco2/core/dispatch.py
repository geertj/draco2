# vi: ts=8 sts=4 sw=4 et
#
# dispatch.py: core dispatcher
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import time
import os.path
import logging
import threading
from StringIO import StringIO

import draco2
from draco2.core.exception import *
from draco2.core.option import init_options
from draco2.core.logger import init_logger
from draco2.core.codec import init_codecs
from draco2.core.api import API
from draco2.core.change import ChangeManager
from draco2.core.config import Config
from draco2.core.loader import Loader
from draco2.core.change import ChangeManager
from draco2.core.event import EventManager
from draco2.core.handler import Handler
from draco2.draco.handler import DracoHandler
from draco2.database.manager import DatabaseManager
from draco2.model.manager import ModelManager
from draco2.security.context import SecurityContext
from draco2.email.sendmail import Sendmail

from draco2.util import http
from draco2.util import uri as urimod
from draco2.util.rwlock import ReadWriteLock
from draco2.util.singleton import singleton
from draco2.util.misc import get_backtrace

initialized = False
rwlock = ReadWriteLock()
initlock = threading.Lock()


def handle_request(iface):
    """Handle a request."""
    # Acquire the read-write lock. This lock is held by all threads in
    # read mode when serving a Draco request. If one of the global Draco
    # objects needs to be reloaded, the lock is upgraded to write mode
    # by the thread that detected the reload condition. All threads will
    # then serialize and the reload can continue.
    rwlock.acquire_read()
    try:
        # Once off initialization. No user code can be run from this, and
        # there's no option of recording errors.
        initlock.acquire()
        try:
            global initialized, options
            if not initialized:
                options = init_options(iface.options())
                init_logger(options)
                init_codecs(options)
                initialized = True
        finally:
            initlock.release()

        # Dispatch the request. Errors are handled from now on.
        debug = options.get('debug')
        profile = options.get('profile')
        logger = logging.getLogger('draco2.core.dispatch')
        try:
            agent = iface.headers_in().get('user-agent', [''])[0]
            logger.debug('Request: %s (%s)' % (iface.uri(), agent))
            t1 = time.time()
            if profile:
                import lsprof
                stats = lsprof.profile(dispatch_request, iface)
                stats.sort('inlinetime')
                io = StringIO()
                stats.pprint(top=20, file=io)
                logger.debug(io.getvalue())
                stats.sort('totaltime')
                io = StringIO()
                stats.pprint(top=20, file=io)
                logger.debug(io.getvalue())
            else:
                dispatch_request(iface)
            t2 = time.time()
            logger.debug('Total time spent: %.2f (%s)' % ((t2 - t1), iface.uri()))
            return

        except HTTPResponse, exc:
            status = exc.status
            headers = exc.headers
            message = http.http_reason_strings[status]
            if not hasattr(exc, 'backtrace') or not exc.backtrace:
                exc.backtrace = get_backtrace()
            errorname = 'error_response_%03d' % status
            exception = exc

        except (StandardError, DracoError), exc:
            status = http.HTTP_INTERNAL_SERVER_ERROR
            headers = {}
            if not hasattr(exc, 'backtrace') or not exc.backtrace:
                exc.backtrace = get_backtrace()
            if debug:
                message = exc.backtrace
            else:
                message = http.http_reason_strings[status]
            errorname = 'uncaught_exception'
            exception = exc
            logger.error('A uncaught exception occurred. Backtrace follows.')
            logger.error(exc.backtrace)

        if iface.header_sent():
            logger.error('Header already sent, cannot continue with error.')
            return

        # For non-error resonse codes always do a simple response.
        stclass = status - (status % 100)
        if stclass in (100, 200, 300):
            iface.simple_response(status, headers, message)
            return

        # Try to dispatch to error handler. This is done by dispatching
        # the request again, using an internal redirect.
        handler = options.get('errorhandler')
        if not handler:
            iface.simple_response(status, headers, message)
            return
        extension = options['extension']
        uri = '/%s/%s.%s' % (handler, errorname, extension)
        iface.internal_redirect(uri)
        iface.set_error(exception)

        try:
            dispatch_request(iface)
            return

        except HTTPResponse, exc:
            if exc.status != http.HTTP_NOT_FOUND:
                logger.error('HTTP response %s in error handler.' % exc.status)

        except (StandardError, DracoError), exc:
            # Log the error but display the original one to the user.
            logger.error('Uncaught exception in error handler. Backtrace follows.')
            if not hasattr(exc, 'backtrace') or not exc.backtrace:
                exc.backtrace = get_backtrace()
            logger.error(exc.backtrace)

        if iface.header_sent():
            logger.error('Header was sent by error handler, cannot continue.')
            return

        # Finally, do a simple error response.
        iface.simple_response(status, headers, message)

    finally:
        rwlock.release_read()


def dispatch_request(iface):
    """Dispatch a request to the proper handler."""
    api = singleton(API, factory=API._create)
    api._install()
    try:
        api.iface = iface
        api.options = options
        api.logger = logging.getLogger('draco2.site')

        # Singleton objects.
        api.changes = singleton(ChangeManager, api,
                                factory=ChangeManager._create)
        api.config = singleton(Config, api, factory=Config._create)
        api.loader = singleton(Loader, api, factory=Loader._create)
        api.events = singleton(EventManager, api,
                               factory=EventManager._create)
        api.database = singleton(DatabaseManager, api,
                                 factory=DatabaseManager._create)
        api.models = singleton(ModelManager, api,
                               factory=ModelManager._create)
        api.sendmail = singleton(Sendmail, api, factory=Sendmail._create)

        # Per request objects.
        api.handler = Handler._create(api)
        api.request = api.handler.Request._create(api)
        api.response = api.handler.Response._create(api)
        api.security = SecurityContext._create(api)

        # Optional objects
        if api.handler.Locale:
            api.locale = api.handler.Locale._create(api)
        if api.handler.Session:
            api.session = api.handler.Session._create(api)

        # Run all change contexts. If a change is detected, this will
        # upgrade 'rwlock' and wait for all threads to serialize outside
        # draco_request(). Then, the change callbacks are run.
        api.changes.run_all_contexts(rwlock, api)

        # Handle the request!
        api.handler._dispatch(api)

    finally:
        if hasattr(api, 'models'):
            api.models._finalize()
        if hasattr(api, 'database'):
            api.database._finalize()
        if hasattr(api, 'events'):
            api.events._finalize()
        api._finalize()
