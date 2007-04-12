# vi: ts=8 sts=4 sw=4 et
#
# handler.py: Draco handler
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.core.handler import Handler
from draco2.core.exception import HTTPResponse
from draco2.locale.locale import tr, tr_attr, tr_mark
from draco2.draco.opener import DracoOpener
from draco2.draco.request import DracoRequest
from draco2.draco.response import DracoResponse
from draco2.draco.locale import DracoLocale
from draco2.draco.session import DracoSession
from draco2.draco.parser import DracoParser
from draco2.draco.rewriter import DracoRewriter
from draco2.draco.compat import CompatFilter, CompatEventHandler
from draco2.file.handler import FileHandler
from draco2.util import http
from draco2.util import uri as urilib


def norobot(method):
    """Decorator disallowing robot access."""
    method.norobot = True
    return method


class DracoHandler(Handler):
    """The Draco handler base class."""

    Request = DracoRequest
    Response = DracoResponse
    Locale = DracoLocale
    Session = DracoSession

    allowed_methods = ('GET', 'HEAD', 'POST')

    def _redirect_index(self, api):
        """Redirect to an index page."""
        request = api.request
        status = http.HTTP_FOUND
        extension = api.config.ns()['extension']
        filename = 'index.%s' % extension
        uri = urilib.create_path_uri(request.directory(), filename, '')
        headers = { 'location': [uri] }
        raise HTTPResponse(status, headers=headers)

    def _pre_request(self, api):
        """Pre request hook."""

    def _post_request(self, api):
        """Post request hook."""

    def _handle(self, api):
        """Handle a Draco request.

        Supported HTTP methods are GET, HEAD and POST. Files having the
        Draco extension are handled as Draco content. Requests for
        directories are redirected to an index page, all other requests
        are treated as plain file requests.
        """
        request = api.request
        response = api.response

        # Redirect to index?
        filename = request.filename()
        if not filename:
            self._redirect_index(api)
            return

        # Serve a normal file?
        extension = api.config.ns()['extension']
        if request.extension() != extension:
            if request.extension() not in ('css', 'js'):
                raise HTTPResponse, http.HTTP_FORBIDDEN
            handler = FileHandler()
            ret = handler._handle(api)
            return ret

        # Set up shared transaction for the draco model.
        model = api.models.model('draco')
        transaction = model.transaction('shared')
        transaction.set_finalization_policy('COMMIT')

        # Per-request objects
        api.opener = DracoOpener._create(api)
        api.parser = DracoParser._create(api)
        api.rewriter = DracoRewriter._create(api)

        try:
            # Session try/finally block.
            api._export(self)
            self['api'] = api
            self['tr'] = tr
            self['tr_attr'] = tr_attr
            self['tr_mark'] = tr_mark

            # Add "compatiblity" events that make our XHTML framework
            # solution work with internet explorer.
            filter = CompatFilter()
            api.response.add_filter(filter)
            event = CompatEventHandler()
            api.events.add_event_handler(event)

            response.set_template(request.filename())

            api.events.raise_event('pre_request', api)
            self._pre_request(api)

            basename = request.basename()
            try:
                method = getattr(self, basename)
            except AttributeError:
                method = None

            template = response.template()
            if template and not api.opener.access(template):
                template = None

            if not method and not template:
                raise HTTPResponse, http.HTTP_NOT_FOUND

            if hasattr(method, 'norobot') and method.norobot and \
                        api.request.isrobot():
                raise HTTPResponse, http.HTTP_FORBIDDEN

            if method:
                method(api)

            if template:
                output = api.parser.parse(template, namespace=self,
                                          opener=api.opener)
                output = api.rewriter.filter(output)
                mime_type = http.get_mime_type(output)
                response.set_buffering(True)
                response.set_header('Content-Type', mime_type)
                response.set_header('Cache-Control', 'no-cache')
                response.set_header('Content-Length', str(len(output)))
                response.write(output)
                api.events.raise_event('pre_request_flush', api)
                header_only = request.method() == 'HEAD'
                response.flush(header_only)

            api.events.raise_event('post_request', api)
            self._post_request(api)

        finally:
            if api.session:
                api.session.commit()

    def _delegate(self, method, api):
        """Delegate execution to another handler."""
        cls = method.im_class
        handler = cls()
        handler.update(self)
        api.handler = handler
        method(handler, api)
        self.update(handler)
        api.handler = self
