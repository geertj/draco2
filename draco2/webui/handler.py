# vi: ts=8 sts=4 sw=4 et
#
# handler.py: webui handler base class.
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.draco.handler import DracoHandler
from draco2.webui.command import parse_command
from draco2.webui.taglib import WebUITagLibrary


class context(object):
    """Decorator for webui methods.

    This decorator sets the "context" function attribute.
    """

    def __init__(self, context):
        self.m_context = context

    def __call__(self, func):
        func.context = self.m_context
        return func


class WebUIHandler(DracoHandler):
    """Web-UI Handler.

    Draco2 handlers should derive from this class if they want to
    use the webui framework.
    """

    def _handle(self, api):
        """Handle an webui request."""
        self.api = api
        super(WebUIHandler, self)._handle(api)

    def _pre_request(self, api):
        """Pre-request hook that takes care of any webui processing."""
        super(WebUIHandler, self)._pre_request(api)
        taglib = WebUITagLibrary()
        api.rewriter.add_tag_library(taglib)
        args = api.request.args()
        try:
            handler = getattr(self, api.request.basename())
        except AttributeError:
            handler = None
        argsupd = {}
        transupd = {}
        for key,value in args.items():
            if key.startswith('transient:'):
                transupd[key[10:]] = value
            else:
                argsupd[key] = value
        nsargs = api.session.namespace('args')
        nstrans = api.session.namespace('transient')
        if api.request.method() in ('GET', 'POST'):
            nsargs.update(argsupd)
            nstrans.update(transupd)
        command = nstrans.get('command')
        if command:
            options = parse_command(command)[2]
        else:
            options = {}
        context = options.get('context', 'keep')
        if context == 'enter' and options.get('context_name'):
            context_name = options['context_name']
            self._enter_context(context_name)
        elif context == 'leave':
            self._leave_context()
        elif context == 'assume':
            context_name = options['context_name']
            self._assume_context(context_name)
        if handler and hasattr(handler, 'context') and \
                    handler.context != self._context():
            self._enter_context(handler.context)
        nsargs = api.session.namespace('args')
        nstrans = api.session.namespace('transient')
        nsctrl = api.session.namespace('control')
        self.update(nsctrl)
        self.update(nstrans)
        self.update(nsargs)
        nstrans.clear()

    def _context(self):
        """Return the current context."""
        ctrl = self.api.session.namespace('control')
        return ctrl.get('context')

    def _assume_context(self, context):
        """Assume an editing context."""
        ctrl = self.api.session.namespace('control')
        ctrl['context'] = context

    def _enter_context(self, context):
        """Enter a new editing context."""
        self.api.session.enter_subsession()
        ctrl = self.api.session.namespace('control')
        ctrl['context'] = context

    def _leave_context(self):
        """Leave the current editing context."""
        self.api.session.leave_subsession()

    def _respond_javascript(self, code):
        """Write out a text/html response with a javascript body
        containing `code'.
        """
        template = '<html><head></head><body>' \
                   '<script type="text/javascript">%s</script>' \
                   '</body></html>'
        response = self.api.response
        response.set_template(None)
        response.set_buffering(False)
        response.set_header('content-type', 'text/html')
        response.write(template % code.encode('html'))

    def _close_dialog(self):
        """Close the current dialog through a javascript response."""
        code = 'window.close()'
        self._respond_javascript(code)

    def _close_and_reload_parent(self):
        """Close the current dialog and reload the window that has opened
        dit through a javascript response."""
        code = 'window.opener.action_reload(); window.close()'
        self._respond_javascript(code)
