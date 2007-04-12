# vi: ts=8 sts=4 sw=4 et
#
# schema.py: schema commands
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
import optparse

from draco2.command.command import Command
from draco2.core.model import DracoModel


class CreateSchema(Command):
    """Create the the schema for a model."""

    name = 'create'
    description = 'create a schema'
    usage = '%prog [options] %command [suboptions] <model>'
    nargs = 1

    def add_options(self, group):
        group.add_option('-t', '--database', action='store_true',
                         dest='database',
                         help='create schema in database [default]')
        group.add_option('-s', '--sql', action='store_false',
                         dest='database',
                         help='output SQL definition of schema')
        group.add_option('-n', '--no-init', action='store_false',
                         dest='init',
                         help='do not initialize schema with default data')

    def set_defaults(self, parser):
        parser.set_default('database', True)
        parser.set_default('init', True)

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        schema = model.schema()
        execute = opts.database
        init = opts.init
        statements = schema.create(execute, init=init)
        if not execute:
            result = ';\n'.join(statements) + ';\n'
            self.write(result)


class DropSchema(Command):
    """Drop the Draco2 schema."""

    name = 'drop'
    description = 'drop the a schema'
    usage = '%prog [options] %command [suboptions] <model>'
    nargs = 1

    def add_options(self, group):
        group.add_option('-t', '--database', action='store_true',
                         dest='database',
                         help='create schema in database [default]')
        group.add_option('-s', '--sql', action='store_false',
                         dest='database',
                         help='output SQL definition of schema')

    def set_defaults(self, parser):
        parser.set_default('database', True)

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        schema = model.schema()
        execute = opts.database
        statements = schema.drop(execute)
        if not execute:
            result = ';\n'.join(statements) + ';\n'
            self.write(result)


class CheckSchema(Command):
    """Check that the Draco2 schema is up to date."""

    name = 'verify'
    description = 'verify that a schema is up to date'
    usage = '%prog [options] %command [suboptions] <model>'
    nargs = 1

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        schema = model.schema()
        version = model.version
        schema_version = schema.version()
        self.write('Model version: %d\n' % version)
        self.write('Schema version: %s\n' % (schema_version or 'none present'))
        if version == schema_version:
            self.write('=> Schema is up to date\n')
        else:
            self.write('=> Schema is NOT up to date\n')


class GrantAccess(Command):
    """Grant access to the draco2 schema."""

    name = 'grant'
    description = 'grant access to a user or group'
    usage = '%prog [options] %command [suboptions] <model> <principal>'
    nargs = 2

    def add_options(self, group):
        group.add_option('-u', '--user', action='store_false', dest='group',
                         help='the specified principal is a user [default]')
        group.add_option('-g', '--group', action='store_true', dest='group',
                         help='the specified principal is a group')
        group.add_option('-t', '--database', action='store_true',
                         dest='database',
                         help='create schema in database [default]')
        group.add_option('-s', '--sql', action='store_false',
                         dest='database',
                         help='output SQL definition of schema')

    def set_defaults(self, parser):
        parser.set_default('group', False)
        parser.set_default('database', True)

    def run(self, opts, args, api):
        name, principal = args
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        schema = model.schema()
        group = opts.group
        execute = opts.database
        statements = schema.grant(principal, group=group, execute=execute)
        if not execute:
            result = ';\n'.join(statements) + ';\n'
            self.write(result)


class RevokeAccess(Command):
    """Revoke access to the draco2 schema."""

    name = 'revoke'
    description = 'revoke access from a user or group'
    usage = '%prog [options] %command [suboptions] <principal>'
    nargs = 2

    def add_options(self, group):
        group.add_option('-u', '--user', action='store_false', dest='group',
                         help='the specified principal is a user [default]')
        group.add_option('-g', '--group', action='store_true', dest='group',
                         help='the specified principal is a group')
        group.add_option('-t', '--database', action='store_true',
                         dest='database',
                         help='create schema in database [default]')
        group.add_option('-s', '--sql', action='store_false',
                         dest='database',
                         help='output SQL definition of schema')

    def set_defaults(self, parser):
        parser.set_default('group', False)
        parser.set_default('database', True)

    def run(self, opts, args, api):
        name, principal = args
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        model = DracoModel(api.database)
        schema = model.schema()
        group = opts.group
        execute = opts.database
        statements = schema.revoke(principal, group=group, execute=execute)
        if not execute:
            result = ';\n'.join(statements) + ';\n'
            self.write(result)


class DumpData(Command):
    """Dump the schema."""

    name = 'dump'
    description = 'create a dump of the schema'
    nargs = 1

    def add_options(self, group):
        group.add_option('-o', '--output', dest='output',
                         help='specify the dump file')
        group.add_option('-n', '--no-exec', action='store_true',
                         dest='noexec', help='do not execute command')

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model(name)
        if not model:
            self.error('no such model: %s' % name)
            self.exit(1)
        output = opts.output
        command = api.database.dumpcommand(model.name, output=output)
        if opts.noexec:
            self.write('%s\n' % command)
        else:
            self.write('executing: %s\n' % command)
            os.system(command)


class SchemaCommand(Command):
    """Schema management."""

    name = 'schema'
    description = 'manage schemas'

    def __init__(self):
        super(SchemaCommand, self).__init__()
        self.add_subcommand(CreateSchema())
        self.add_subcommand(DropSchema())
        self.add_subcommand(CheckSchema())
        self.add_subcommand(GrantAccess())
        self.add_subcommand(RevokeAccess())
        self.add_subcommand(DumpData())
