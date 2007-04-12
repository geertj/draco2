#!/usr/bin/env python2.4
# vi: ts=8 sts=4 sw=4 et
#
# draco2.py: Draco2 command line utility.
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import sys

# HACK: prevent script from importing from itself
del sys.path[0]

from draco2 import DracoError
from draco2.core.loader import Loader
from draco2.command import (Command, SchemaCommand, PrincipalCommand,
                            RoleCommand, LanguageCommand, MessageCommand,
                            TranslationCommand, TranslateCommand,
                            ServeCommand)
from draco2.session.command import SessionCommand


class MainCommand(Command):
    """Top-level command.

    This command provides an interface to the standard commands provided
    by Draco, plus any dynamic commands from the document root.
    """

    name = 'main'
    usage = '%prog [options] [subcmd [suboptions]]...'

    def __init__(self):
        """Constructor."""
        super(MainCommand, self).__init__()
        self.add_subcommand(SchemaCommand())
        self.add_subcommand(PrincipalCommand())
        self.add_subcommand(RoleCommand())
        self.add_subcommand(LanguageCommand())
        self.add_subcommand(MessageCommand())
        self.add_subcommand(TranslationCommand())
        self.add_subcommand(TranslateCommand())
        self.add_subcommand(SessionCommand())
        self.add_subcommand(ServeCommand())

    def load_dynamic(self, opts, args):
        """Dynamically load commands from the document root."""
        loader = Loader()
        loader.add_scope('__docroot__', opts.docroot)
        clslist = loader.load_classes('__command__.py', Command,
                                      scope='__docroot__')
        for cls in clslist:
            self.add_subcommand(cls())

    def execute(self, args):
        """Execute the command."""
        subcmd, opts, subargs = self.parse_args(args)
        subcmd.resolve_docroot(opts, subargs)
        self.load_dynamic(opts, subargs)
        subcmd, opts, subargs = self.parse_args(args)  # again for new subcmds
        subcmd.check_args(opts, subargs)
        api = subcmd._create_api(opts, subargs)
        subcmd.run(opts, subargs, api)


def main():
    """Main function."""
    command = MainCommand()
    try:
        command.execute(sys.argv[1:])
    except DracoError, err:
        sys.stderr.write('Error: %s\n' % str(err))
        if hasattr(err, 'filename'):
            sys.stderr.write('Filename: %s\n' % err.filename)
        if hasattr(err, 'lineno'):
            sys.stderr.write('Lineno: %s\n' % err.lineno)
        if hasattr(err, 'backtrace'):
            sys.stderr.write('%s\n' % err.backtrace)
        sys.exit(1)


if __name__ == '__main__':
    main()
