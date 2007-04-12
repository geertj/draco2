#
# command.py: Command base class
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
import sys
import stat
import optparse
import logging

from draco2.core.option import init_options
from draco2.core.codec import init_codecs
from draco2.core.logger import init_logger
from draco2.core.api import API
from draco2.core.config import Config
from draco2.core.loader import Loader
from draco2.core.event import EventManager
from draco2.database.manager import DatabaseManager
from draco2.model.manager import ModelManager


class Command(object):
    """Base class for Draco commands.

    A Draco command is an action that can be executed outside the context
    of a web request.

    The Command class has the following responsibilities:

    - I/O to the console
    - creating the API
    - parsing arguments
    - optionally holding a subcommand hierarchy
    """

    name = None
    description = None
    usage = '%prog [options] %command [suboptions]'
    nargs = None
    require_api = set(('options', 'logger', 'config', 'loader',
                       'database', 'models'))

    def __init__(self):
        """Constructor."""
        self.m_parent = None
        self.m_subcommands = []

    def write(self, message):
        """Write `message' to the console."""
        sys.stdout.write('%s' % message)

    def flush(self):
        """Flush the output."""
        sys.stdout.flush()

    def write_error(self, message):
        """Write `message' to the error output on the console."""
        sys.stderr.write('%s' % message)

    def prompt(self, message):
        """Prompt the user for input, displaying `message'."""
        sys.stdout.write(message)
        sys.stdout.flush()
        line = sys.stdin.readline()
        return line

    def warning(self, message):
        """Show a warning message."""
        self.write_error('warning: %s\n' % message)

    def error(self, message):
        """Show an error message."""
        self.write_error('error: %s\n' % message)

    def exit(self, code=1):
        """Exit."""
        sys.exit(code)

    def verify(self, message):
        """Ask the user for verification before continuing."""
        self.warning(message)
        answer = self.prompt('Are you sure you want to continue (y/n)? ')
        return answer.strip() in ('y', 'yes')

    def add_subcommand(self, cmd):
        """Add a new sub command."""
        if not isinstance(cmd, Command):
            m = 'Expecting "Command" instance (got %s).'
            raise TypeError, m % cmd
        cmd._set_parent(self)
        self.m_subcommands.append(cmd)

    def get_subcommand(self, name):
        """Return a subcommand by name, or None."""
        for cmd in self.m_subcommands:
            if cmd.name == name:
                return cmd

    def subcommands(self):
        """Return the list of sub commands."""
        return self.m_subcommands

    def parent(self):
        """Return the parent command."""
        return self.m_parent

    def _set_parent(self, parent):
        """The the parent command."""
        if not isinstance(parent, Command):
            m = 'Expecting "Command" instance (got %s).'
            raise TypeError, m % parent
        self.m_parent = parent

    def fullname(self):
        """Return the full name of the command.

        The full name is this command's name prefixed with its parent's
        command full name. The name of the root command is not included.
        """
        if self.parent() is None or self.parent().parent() is None:
            return self.name
        fullname = '%s %s' %  (self.parent().fullname(), self.name)
        return fullname

    def show_usage(self):
        """Show a small note about program usage and exit."""
        progname = self.m_parser.get_prog_name()
        fullname = self.fullname()
        usage = self.usage.replace('%prog', progname) \
                          .replace('%command', fullname)
        self.write('usage: %s\n' % usage)

    def show_help(self):
        """Show a help text."""
        self.show_usage()
        self.write('\n')
        if self.subcommands():
            fullname = self.fullname()
            if fullname:
                self.write('%s commands:\n' % fullname)
            else:
                self.write('commands:\n')
            for cmd in self.subcommands():
                self.write('  %-21s %s\n' % (cmd.name, cmd.description))
            self.write('\n')
        self.m_parser.print_help(self)

    def _create_parser(self):
        """Create an OptionParser instance."""
        parser = optparse.OptionParser(usage='', add_help_option=False)
        parser.disable_interspersed_args()
        self.configure_parser(parser)
        return parser

    def configure_parser(self, parser):
        """Configure an OptionParser instance."""
        group = optparse.OptionGroup(parser, 'generic options')
        group.add_option('-h', '--help', action='store_true', dest='showhelp',
                         default=False, help='show help text [about subcmd]')
        group.add_option('-r', '--document-root', dest='docroot',
                         default='.', help='specify the document root')
        group.add_option('-f', '--config-file', dest='cfgfile',
                         default='draco2.ini',
                         help='specify an alternate config file [default: %default]')
        group.add_option('-l', '--log-file', dest='logfile',
                         default='draco2.log',
                         help='specify an alternate log file [default: %default]')
        group.add_option('-D', '--dsn', dest='dsn',
                         help='specify alternate dsn [default: use config]')
        parser.add_option_group(group)
        name = self.fullname()
        group = optparse.OptionGroup(parser, 'options for %s' % name)
        self.add_options(group)
        if group.option_list:
            parser.add_option_group(group)
        self.set_defaults(parser)

    def add_options(self, group):
        """Add options to `group'. To be implemented in subclasses."""

    def set_defaults(self, parser):
        """Set defaults on `parser'. To be implemented in subclasses."""

    def parse_args(self, args):
        """Parse arguments."""
        self.m_parser = self._create_parser()
        cmd = self
        opts, subargs = self.m_parser.parse_args(args)
        if subargs and self.subcommands():
            subcmd = self.get_subcommand(subargs[0])
            if subcmd:
                newargs = args[:]
                newargs.remove(subargs[0])
                cmd, opts, subargs = subcmd.parse_args(newargs)
        return cmd, opts, subargs

    def check_args(self, opts, args):
        """Verify arguments."""
        if opts.showhelp:
            self.show_help()
            self.exit(0)
        if self.subcommands():
            self.show_usage()
            self.exit(1)
        nargs = self.nargs
        if isinstance(nargs, int) and len(args) != nargs:
            self.show_usage()
            self.exit(1)
        elif isinstance(nargs, tuple) and (len(args) < nargs[0] \
                or nargs[1] is not None and len(args) > nargs[1]):
            self.show_usage()
            self.exit(1)

    def resolve_docroot(self, opts, args):
        """Check the document root that has been supplied."""
        docroot = os.path.abspath(opts.docroot)
        try:
            st = os.stat(docroot)
        except OSError:
            st = None
        if st is None or not stat.S_ISDIR(st.st_mode):
            self.error('no such directory: %s' % opts.docroot)
            self.exit(1)
        cfgfile = os.path.join(docroot, opts.cfgfile)
        try:
            st = os.stat(cfgfile)
        except OSError:
            st = None
        if st is None or not stat.S_ISREG(st.st_mode):
            self.error('no such file: %s' % opts.cfgfile)
            self.exit(1)
        opts.docroot = docroot
        opts.cfgfile = cfgfile
        opts.logfile = os.path.join(docroot, opts.logfile)

    def _create_api(self, opts, args):
        """Create an API, as requested by the command."""
        options = {}
        options['documentroot'] = opts.docroot
        options['configfile'] = opts.cfgfile
        options['logfile'] = opts.logfile
        options = init_options(options)
        init_logger(options)
        init_codecs(options)
        api = API()
        if 'options' in self.require_api:
            api.options = options
        if 'logger' in self.require_api:
            api.logger = logging.getLogger('draco2.site')
        if 'config' in self.require_api:
            api.config = Config._create(api)
        if 'loader' in self.require_api:
            api.loader = Loader._create(api)
        if 'events' in self.require_api:
            api.events = EventManager._create(api)
        if 'database' in self.require_api:
            api.database = DatabaseManager._create(api)
            if opts.dsn:
                api.database._set_dsn(dsn)
        if 'models' in self.require_api:
            api.models = ModelManager._create(api)
        return api

    def execute(self, args):
        """Run the command. This parses the arguments and calls .run()."""
        subcmd, opts, args = self.parse_args(args)
        subcmd.resolve_docroot(opts, args)
        subcmd.check_args(opts, args)
        api = subcmd._create_api(opts, args)
        subcmd.run(opts, args, api)

    def run(self, opts, args, api):
        """Execute the command. To be implemented in a subclass."""
        self.show_usage()
