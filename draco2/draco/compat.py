# vi: ts=8 sts=4 sw=4 et
#
# compat.py: non-xhtml user agent compatiblity
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
from draco2.core.filter import Filter
from draco2.core.event import EventHandler


class CompatFilter(Filter):
    """Non-XHTML user agent compatiblity filter.

    This filter removes CDATA sections and replaces them with their
    encoded contents.
    """

    def _iscompat(self):
        request = draco2.api.request
        agent_info = request.agent_info()
        return agent_info and agent_info[0] == 'MSIE' or request.isrobot()

    def filter(self, buffer):
        if not self._iscompat():
            return buffer
        p1 = 0
        result = ''
        while True:
            p2 = buffer.find('<![CDATA[', p1)
            if p2 == -1:
                result += buffer[p1:]
                break
            result += buffer[p1:p2]
            p1 = p2 + 9
            p2 = buffer.find(']]>', p1)
            if p2 == -1:
                raise ValueError
            #result += buffer[p1:p2].encode('html')
            result += buffer[p1:p2]
            p1 = p2 + 3
        return result


class CompatEventHandler(EventHandler):
    """Compatiblity for non-XHTML user agents.

    Change content-type "application/xhtml+xml" to "text/html".
    """

    def _iscompat(self):
        request = draco2.api.request
        agent_info = request.agent_info()
        return agent_info and agent_info[0] == 'MSIE' or request.isrobot()

    def pre_request_flush(self, api):
        if not self._iscompat():
            return
        response = draco2.api.response
        if response.header('content-type') == 'application/xhtml+xml':
            response.set_header('content-type', 'text/html')
