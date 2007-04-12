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

from cStringIO import StringIO

from draco2.core.exception import *
from draco2.core.filter import Filter
from draco2.util import http
from draco2.util.timezone import GMT, LocalTime


class Response(object):
    """The response object."""

    # non-buffer states
    INIT = 0
    HEADER_SENT = 1
    BYTES_WRITTEN = 2
    # buffer states
    BUFFER_INIT = 3
    BYTES_BUFFERED = 4
    BUFFER_COMPLETE = 5
    BUFFER_HEADER_SENT = 6
    BUFFER_BODY_SENT = 7

    def __init__(self, iface):
        """Constructor."""
        self.m_iface = iface
        self.m_buffer = StringIO()
        self.m_state = self.INIT
        self.m_headers = {}
        self.m_cookies = {}
        self.m_modified = None
        self.m_filters = []
        self.set_buffering(False)
        self.set_encoding('utf-8')

    @classmethod
    def _create(cls, api):
        """Factory method."""
        response = cls(api.iface)
        section = api.config.ns('draco2.core.response')
        if section.has_key('buffering'):
            self.set_buffering(section['buffering'])
        if section.has_key('encoding'):
            self.set_encoding(section['encoding'])
        filters = api.loader.load_classes('__filter__.py', Filter, 
                                          scope='__docroot__')
        for filter in filters:
            obj = filter()
            response.add_filter(obj, obj.priority)
        return response

    def buffering(self):
        """Return True if buffering is enabled."""
        return self.m_buffering

    def set_buffering(self, enable):
        """Enable or disable response buffering.

        Features such as encoding require buffering.
        """
        if self.m_state not in (self.INIT, self.BUFFER_INIT):
            m = 'Canot change buffer policy (wrong state).'
            raise DracoInterfaceError, m
        self.m_buffering = enable
        if self.m_buffering:
            self.m_state = self.BUFFER_INIT
        else:
            self.m_state = self.INIT

    def encoding(self):
        """Return the response encoding."""
        return self.m_encoding

    def set_encoding(self, encoding):
        """Set the encoding to use/assume.

        Unicode output is encoded using this encoding. String input is
        assumed to be in the correct encoding already.
        """
        if self.m_state not in (self.INIT, self.BUFFER_INIT):
            m = 'Cannot set encoding (wrong state).'
            raise DracoInterfaceError, m
        self.m_encoding = encoding

    def header(self, name, default=None):
        """Return the value of a header `name'.

        If the header doesn't exist, `default' is returned.
        """
        return self.m_headers.get(name.lower(), [default])[0]

    def headers(self):
        """Return a dictionary of all headers."""
        return self.m_headers

    def set_header(self, name, value):
        """Set a header `name' to `value'.

        All other values for this header are removed.
        """
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Cannot set header (wrong state).'
            raise DracoInterfaceError, m
        if isinstance(value, int):
            value = '%d' % value
        elif isinstance(value, unicode):
            value = value.encode('ascii')
        elif not isinstance(value, str):
            m = 'Expecting str, unicode or int header value (got: %s).'
            raise TypeError, m % type(value)
        self.m_headers[name.lower()] = [value]

    def add_header(self, name, value):
        """Add `value' to header `name'.

        The value is appended to existing values for the header.
        """
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Cannot add header (wrong state).'
            raise DracoInterfaceError, m
        if isinstance(value, int):
            value = '%d' % value
        elif isinstance(value, unicode):
            value = value.encode('ascii')
        elif not isinstance(value, str):
            m = 'Expecting str, unicode or int header value (got: %s).'
            raise TypeError, m % type(value)
        try:
            self.m_headers[name.lower()].append(value)
        except KeyError:
            self.m_headers[name.lower()] = [value]

    def cookie(self, name, default=None):
        """Return the first value of cookie `name', or `default' if
        there is no such cookie."""
        return self.m_cookies.get(name, default)

    def cookies(self):
        """Return a dictionary with all cookies."""
        return self.m_cookies

    def set_cookie(self, cookie):
        """Set a cookie, removing other cookies with the same name."""
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Cannot set cookie (wrong state).'
            raise DracoInterfaceError, m
        self.m_cookies[cookie.name] = cookie

    def status(self):
        """Return the current HTTP response status."""
        return self.m_iface.status()

    def set_status(self, status):
        """Set the HTTP response status."""
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Cannot set status (wrong state).'
            raise DracoInterfaceError, m
        self.m_iface.set_status(status)

    def modified(self):
        """Return the date of last modification, or None if unknown."""
        return self.m_modified

    def set_modified(self, modified):
        """The resource was modified on `modifier'.

        The maximum value of `datetime' is kept and the 'Last-Modified'
        HTTP header is set from this.
        """
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Modification date cannot be changed (wrong state).'
            raise DracoInterfaceError, m
        # Convert to GMT, as required by RFC2616. If no tzinfo was
        # provided, asssume it was in local time.
        if modified.tzinfo is None:
            modified = modified.replace(tzinfo=LocalTime())
        modified = modified.astimezone(GMT())
        if self.m_modified is None:
            self.m_modified = modified
        else:
            self.m_modified = max(self.m_modified, modified)
        value = self.m_modified.strftime(http.rfc1123_datetime)
        self.set_header('last-modified', value)

    def add_filter(self, filter, priority=None):
        """Add an output filter `filter'."""
        if self.m_state not in (self.INIT, self.BUFFER_INIT,
                                self.BYTES_BUFFERED, self.BUFFER_COMPLETE):
            m = 'Filter cannot be added (wrong state).'
            raise DracoInterfaceError, m
        if not isinstance(filter, Filter):
            raise TypeError, 'Expecting Filter instance.'
        if priority is None:
            priority = filter.priority
        self.m_filters.append((priority, filter))
        self.m_filters.sort()

    def filters(self):
        """Return a list of installed filters."""
        filters = [ ft[1] for ft in self.m_filters ]
        return filters

    def send_header(self):
        """Send the HTTP header."""
        if self.m_state not in (self.INIT, self.BUFFER_COMPLETE):
            m = 'Cannot send header (wrong state).'
            raise DracoInterfaceError, m
        for name,cookie in self.m_cookies.items():
            self.add_header('set-cookie', cookie.encode())
        for name,values in self.m_headers.items():
            self.m_iface.headers_out()[name] = values
        self.m_iface.send_header()
        if self.m_state == self.INIT:
            self.m_state = self.HEADER_SENT
        else:
            self.m_state = self.BUFFER_HEADER_SENT

    def write(self, buf):
        """Write the string `buf' to the client.

        If buffering is enabled this call just updated the buffer.
        """
        if self.m_state not in (self.INIT, self.HEADER_SENT,
                                self.BYTES_WRITTEN, self.BUFFER_INIT,
                                self.BYTES_BUFFERED):
            m = 'No output possible (wrong state).'
            raise DracoInterfaceError, m
        if isinstance(buf, unicode):
            buf = buf.encode(self.m_encoding)
        if self.m_buffering:
            assert self.m_state not in (self.HEADER_SENT, self.BYTES_WRITTEN)
            self.m_buffer.write(buf)
            self.m_state = self.BYTES_BUFFERED
        else:
            assert self.m_state not in (self.BUFFER_INIT, self.BYTES_BUFFERED)
            if self.m_state == self.INIT:
                self.send_header()
            self.m_iface.write(buf)
            self.m_state = self.BYTES_WRITTEN

    def flush(self, header_only=False):
        """Flush the response. This function is only useful in combination
        with buffered responses."""
        if self.m_state not in (self.BUFFER_INIT, self.BYTES_BUFFERED):
            m = 'Cannot flush output (wrong state).'
            raise DracoInterfaceError, m
        buffer = self.m_buffer.getvalue()
        for filter in self.filters():
            buffer = filter.filter(buffer)
        self.m_state = self.BUFFER_COMPLETE
        self.set_header('content-length', str(len(buffer)))
        self.send_header()
        if not header_only:
            self.m_iface.write(buffer)
        self.m_state = self.BUFFER_BODY_SENT

    def redirect(self, uri, status=None):
        """Redirect to another URI."""
        if self.m_state not in (self.INIT, self.BUFFER_INIT, self.BYTES_BUFFERED):
            m = 'Cannot redirect (wrong state).'
            raise DracoInterfaceError, m
        if status is None:
            status = http.HTTP_FOUND
        if isinstance(uri, unicode):
            uri = uri.encode('ascii')
        elif not isinstance(uri, str):
            m = 'Expecting str or unicode argument (got: %s).'
            raise TypeError, m % type(uri)
        self.add_header('location', uri)
        for name,cookie in self.m_cookies.items():
            self.add_header('set-cookie', cookie.encode())
        raise HTTPResponse(status, headers=self.m_headers)

    def exit(self, code=http.HTTP_OK):
        """End processing."""
        raise HTTPResponse, code
