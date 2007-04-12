# vi: ts=8 sts=4 sw=4 et
#
# dispatch.py: xmlrpc dispatcher
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import draco2
from draco2.core.handler import MetaHandler


class XmlRpcMetaHandler(MetaHandler):

    def __init__(self):
        """
        Constructor.
        """
        MetaHandler.__init__(self)

    def handleRequest(self, iface):
        """
        Handle the web server request.
        """
        reldir = iface.reldir()
        fname = '%s/__handler__.py' % reldir
        hclass = draco2.loader.loadClass(fname, Handler, scope='__docroot__')
        if hclass is None:
            return draco2.HTTP_NOT_FOUND

        filename = iface.filename()
        if not hasattr(hclass, filename):
            return draco2.HTTP_NOT_FOUND

        handler = hclass()
        method = getattr(handler, filename)

        request = XmlRpcRequest(iface)
        response = XmlRpcResponse(iface)
        client = Client(iface)
        server = Server(iface)

        handler.request = request
        handler.response = response
        handler.client = client
        handler.server = server

        status = method(request.args()) or draco2.HTTP_OK
        response.flush()
        return status
