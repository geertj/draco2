# vi: ts=8 sts=4 sw=4 et
#
# command.py: session commands
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

from draco2.util.timezone import GMT, LocalTime
from draco2.util.http import rfc1123_datetime
from draco2.core.model import Session
from draco2.command.command import Command


class ListSessions(Command):
    """List active sessions."""

    name = 'list'
    description = 'list sessions'

    def _format_time(self, dt, gmt=False):
        dt = dt.replace(tzinfo=GMT())
        if not gmt:
            dt = dt.astimezone(LocalTime())
        s = dt.strftime(rfc1123_datetime)
        return s

    def add_options(self, group):
        group.add_option('-g', '--gmt', action='store_true',
                         dest='gmt', help='show date/times in GMT')

    def set_defaults(self, parser):
        parser.set_default('gmt', False)

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        sessions = transaction.select(Session)
        for session in sessions:
            self.write('session: %s, create_date = %s, last_used = %s, ' \
                       'expire_date = %s\n' % (session['id'],
                           self._format_time(session['create_date'], opts.gmt),
                           self._format_time(session['last_used'], opts.gmt),
                           self._format_time(session['expire_date'], opts.gmt)))
        self.write('total sessions: %d\n' % len(sessions))


class ExpireSessions(Command):
    """Expire sessions."""

    name = 'expire'
    description = 'expire sessions'

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        expired = transaction.expire_sessions()
        transaction.commit()
        self.write('sessions expired: %s\n' % expired)


class SessionCommand(Command):

    name = 'session'
    description = 'manage sessions'

    def __init__(self):
        super(SessionCommand, self).__init__()
        self.add_subcommand(ListSessions())
        self.add_subcommand(ExpireSessions())
