# vi: ts=8 sts=4 sw=4 et
#
# response.py: Draco response object
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

from draco2.core.response import Response
from draco2.util import http
from draco2.util import uri as urimod
from draco2.draco import uri as dracouri
from draco2.session.util import dump_sessionid


class DracoResponse(Response):
    """The Draco response object."""

    def __init__(self, *args):
        """Constructor."""
        super(DracoResponse, self).__init__(*args)
        self.m_template = None
        self._set_rewrite_link_level(0)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        response = super(DracoResponse, cls)._create(api)
        response._set_api(api)
        response._set_request(api.request)
        config = api.config.ns('draco2.draco.response')
        if config.has_key('rewritelinklevel'):
            response._set_rewrite_link_level(config['rewritelinklevel'])
        return response

    def _set_api(self, api):
        """Set the API to `api'."""
        self.m_api = api

    def _set_request(self, request):
        """Set the request to `request'."""
        self.m_request = request

    def _set_rewrite_link_level(self, level):
        """Set the rewrite link level to `level'.

        A value of 0 disables link rewriting, a value of 1 enables it
        for subsessions and any value > 1 enables full rewriting."""
        self.m_rewrite_link_level = level

    def template(self):
        """Return the template that will be parsed after the handler."""
        return self.m_template

    def set_template(self, template):
        """Set the template to be parsed."""
        if template is not None and not isinstance(template, basestring):
            raise TypeError, 'Expecting string instance or None.'
        self.m_template = template

    def resolve_uri(self, method):
        """Return the URI of a handler method."""
        if not callable(method) and not isinstance(method, basestring):
            raise TypeError, 'Expecting method or string.'
        if callable(method):
            extension = self.m_api.options['extension']
            method = dracouri.uri_from_method(method, extension)
        elif not method.startswith('/'):
            parts = method.split('/')
            extension = self.m_api.options['extension']
            if not parts[0].endswith('.' + extension):
                parts[0] += '.%s' % extension
            method = '/%s/%s' % (self.m_request.directory(), '/'.join(parts))
        return method

    def absolute_uri(self, uri, scheme=None, host=None):
        """If `uri' is a relative URI, add scheme and host."""
        if not scheme:
            if self.m_request.isssl():
                scheme = 'https'
            else:
                scheme = 'http'
        if not host:
            host = self.m_request.servername()
        docroot = self.m_request.docroot()
        uri = dracouri.paste_draco_uri(uri, docroot, scheme=scheme, host=host)
        return uri

    def paste_uri(self, uri, scheme=None, host=None, directory=None,
                  filename=None, locale=None, session=None, pathinfo=None,
                  args=None):
        """Paste into an URI.

        The arguments specify values to paste into `uri' in case it does
        not contain that component.
        """
        if callable(uri):
            extension = self.m_api.options['extension']
            uri = dracouri.uri_from_method(uri, extension)
        if isinstance(pathinfo, list):
            pathinfo = '/'.join(pathinfo)
        if isinstance(args, dict):
            args = urimod.create_query(args)
        docroot = self.m_request.docroot()
        return dracouri.paste_draco_uri(uri, docroot, scheme, host, directory,
                                        filename, locale, session, pathinfo,
                                        args)

    def patch_uri(self, uri, scheme=None, host=None, directory=None,
                  filename=None, locale=None, session=None, pathinfo=None,
                  args=None):
        """Patch an URI.

        The arguments specify with components of the URI to patch.
        Components that are not specified are left untouched.
        """
        if callable(uri):
            extension = self.m_api.options['extension']
            uri = dracouri.uri_from_method(uri, extension)
        if isinstance(pathinfo, list):
            pathinfo = '/'.join(pathinfo)
        if isinstance(args, dict):
            args = urimod.create_query(args)
        docroot = self.m_request.docroot()
        return dracouri.patch_draco_uri(uri, docroot, scheme, host, directory,
                                        filename, locale, session, pathinfo,
                                        args)

    def rewrite_uri(self, uri, force_rewrite=False):
        """Pass on extended Draco URI components."""
        if callable(uri):
            extension = self.m_api.options['extension']
            uri = dracouri.uri_from_method(uri, extension)
        scheme, host, path, query = urimod.parse_uri(uri)
        if scheme and scheme != 'http':
            return uri
        docroot = self.m_request.docroot()
        extension = self.m_api.options['extension']
        servername = self.m_request.servername()
        parts = dracouri.parse_draco_uri(uri, docroot)
        if not force_rewrite and (parts[1] and parts[1] != servername) \
                    or not parts[3].endswith('.' + extension):
            return uri
        locale = self.m_request.locale()
        if hasattr(self.m_api, 'session'):
            sessionid = self.m_api.session.sessionid()
        else:
            sessionid = None
        if sessionid:
            sessionid = list(sessionid)
            # subsession if not default
            if self.m_rewrite_link_level == 0:
                sessionid[0] = None
                if sessionid[1] == 0:
                    sessionid[1] = None
            # subsession unconditionally
            elif self.m_rewrite_link_level == 1:
                sessionid[0] = None
            session = dump_sessionid(sessionid)
        else:
            session = None
        uri = self.paste_uri(uri, locale=locale, session=session)
        return uri

    def redirect(self, uri, scheme=None, host=None, directory=None,
                 filename=None, locale=None, session=None, pathinfo=None,
                 args=None, force_rewrite=False, status=None):
        """Redirect to another URI."""
        if status is None:
            status = http.HTTP_FOUND
        uri = self.resolve_uri(uri)
        uri = self.absolute_uri(uri)
        uri = self.rewrite_uri(uri, force_rewrite)
        uri = self.patch_uri(uri, scheme, host, directory, filename,
                             locale, session, pathinfo, args)
        super(DracoResponse, self).redirect(uri, status=status)
