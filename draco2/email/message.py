# vi: ts=8 sts=4 sw=4 et
#
# message.py: Message class
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from StringIO import StringIO


class Message(object):
    """An email Message.

    This class is a representation of an RFC2822 email message.
    It has no special support for creating MIME messages, but it
    can be used to hold preformatted MIME messages.
    """

    def __init__(self):
        """Constructor."""
        self.m_headers = {}
        self.m_recipients = []
        self.m_cc_recipients = []
        self.m_bcc_recipients = []
        self.m_buffer = StringIO()

    def header(self, name):
        """Return the first value of a header `name', or None
        if the header does not exist.
        """
        try:
            return self.m_headers[name.lower()][0][1]
        except KeyError:
            pass

    def headers(self):
        """Return a dictionary containing all headers."""
        return self.m_headers

    def add_header(self, name, value):
        """Add the value `value' for header `name'."""
        try:
            self.m_headers[name.lower()].append((name, value))
        except KeyError:
            self.m_headers[name.lower()] = [(name, value)]

    def set_header(self, name, value):
        """Set the value of header `name' to `value', deleting any
        values the header may have.
        """
        self.m_headers[name.lower()] = [(name, value)]

    def del_header(self, name):
        """Delete all headers `name'."""
        try:
            del self.m_headers[name.lower()]
        except KeyError:
            pass

    def recipients(self):
        """Return the list of "To" recipients."""
        return self.m_recipients

    def add_recipient(self, to):
        """Add the recipient `recipient' to the "To" list."""
        self.m_recipients.append(to)

    def cc_recipients(self):
        """Return the list of "Cc" recipients."""
        return self.m_cc_recipients

    def add_cc_recipient(self, cc):
        """Add the recipient `recipient' to the "Cc" list."""
        self.m_cc_recipients.append(cc)

    def bcc_recipients(self):
        """Return the list of "Bcc" recipients."""
        return self.m_bcc_recipients

    def add_bcc_recipient(self, bcc):
        """Add the recipient `recipient' to the "Bcc" list."""
        self.m_bcc_recipients.append(bcc)

    def write(self, buf):
        """Write `buffer' to the message body."""
        self.m_buffer.write(buf)

    def body(self):
        """Return the message body."""
        return self.m_buffer.getvalue()

    def dump(self):
        """Return the message headers and body."""
        if self.m_recipients:
            addrs = ', '.join(self.m_recipients)
            self.set_header('To', addrs)
        if self.m_cc_recipients:
            addrs = ', '.join(self.m_cc_recipients)
            self.set_header('Cc', addrs)
        if self.m_bcc_recipients:
            addrs = ', '.join(self.m_bcc_recipients)
            self.set_header('Bcc', addrs)
        result = u''
        for name in self.m_headers:
            for name, value in self.m_headers[name]:
                result += '%s: %s\r\n' % (name, value)
        result += '\r\n'
        result += self.m_buffer.getvalue()
        return result.encode('utf-8')
