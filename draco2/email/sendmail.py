# vi: ts=8 sts=4 sw=4 et
#
# sendmail.py: Sendmail class
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
import socket
from smtplib import SMTP, SMTPException
import logging

from draco2.email.exception import SendmailError
from draco2.email.message import Message


class Sendmail(object):
    """Sendmail object.

    This object is responsible for sending out email to an SMTP server.
    """

    smtp_port = 25
    local_sender = 'noreply'

    def __init__(self):
        """Constructor."""
        hostname = socket.getfqdn()
        sender = '%s@%s' % (self.local_sender, hostname)
        self._set_sender(sender)
        self._set_smtp_server('localhost')

    @classmethod
    def _create(cls, api):
        """Factory method."""
        sendmail = cls()
        config = api.config.ns('draco2.email.sendmail')
        if config.has_key('sender'):
            sendmail._set_sender(config['sender'])
        if config.has_key('smtpserver'):
            sendmail._set_smtp_server(config['smtpserver'])
        if hasattr(api, 'changes'):
            sendmail._set_change_manager(api.changes)
        return sendmail

    def _set_change_manager(self, changes):
        """Set the change manager to `changes'."""
        ctx = changes.get_context('draco2.core.config')
        ctx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Reload config."""
        config = api.config.ns('draco2.email.sendmail')
        if config.has_key('sender'):
            self._set_sender(config['sender'])
        if config.has_key('smtpserver'):
            self._set_smtp_server(config['smtpserver'])
        logger = logging.getLogger('draco2.email.sendmail')
        logger.info('Reloaded configuration (change detected).')

    def _set_sender(self, sender):
        """Set the sender address."""
        self.m_sender = sender

    def _set_smtp_server(self, server):
        """Set the SMTP server.

        The server can be specified in host:port form.
        """
        try:
            server, port = server.split(':')
        except ValueError:
            port = self.smtp_port
        self.m_smtp_server = server
        self.m_smtp_port = port

    def send(self, message, recipients=None):
        """Send an email.

        The email is sent to `recipient', which must be a list of
        RFC2822 compliant mailboxes and groups.

        If recipients is not specified, it is extracted from the
        'To', 'Cc' and 'Bcc' headers of the message.

        The return value is a list of failed email addresses. If
        not a single email could be sent, an exception is raised.
        """
        if not isinstance(message, Message):
            raise TypeError, 'Expecting "Message" instance.'
        if recipients is None:
            recipients = message.recipients()
            recipients += message.cc_recipients()
            recipients += message.bcc_recipients()
        message.del_header('Bcc')
        smtp = SMTP()
        try:
            smtp.connect(self.m_smtp_server, self.m_smtp_port)
            ret = smtp.sendmail(self.m_sender, recipients, message.dump())
        except SMTPException, err:
            m = 'Could not send email: %s' % str(err)
            raise SendmailError, m
        refused = ret.keys()
        return refused
