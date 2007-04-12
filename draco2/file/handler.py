# vi: ts=8 sts=4 sw=4 et
#
# handler: Draco2 file handler
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
import os.path

from draco2.core.handler import Handler
from draco2.core.response import HTTPResponse
from draco2.util import http
from draco2.util import uri as urilib


class FileHandler(Handler):
    """A handler that serves plain files."""

    allowed_methods = ('GET', 'HEAD')

    def _handle(self, api):
        """Handle a file request."""
        request = api.request
        response = api.response
        filename = request.filename()
        if filename.startswith('_') or filename.startswith('.'):
            raise HTTPResponse, http.HTTP_FORBIDDEN
        fname = os.path.join(request.docroot(), request.directory(),
                             request.filename())
        try:
            st = os.stat(fname)
            fin = file(fname, 'rb')
        except (OSError, IOError):
            raise HTTPResponse, http.HTTP_NOT_FOUND
        content_type = http.get_mime_type(fin, fname)
        if content_type.startswith('text/'):
            encoding = http.get_encoding(fin)
            content_type = '%s; encoding=%s' % (content_type, encoding)
        response.set_buffering(False)
        response.set_header('content-type', content_type)
        response.set_header('content-length', str(st.st_size))
        modified = http.get_last_modified(st)
        response.set_header('last-modified', modified)
        response.send_header()
        if request.method() == 'GET':
            fin.seek(0)
            count = 0
            while True:
                buf = fin.read(4096)
                if not buf:
                    break
                try:
                    response.write(buf)
                except IOError:
                    break  # Client EOF
        fin.close()
