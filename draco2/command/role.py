# vi: ts=8 sts=4 sw=4 et
#
# role.py: role commands
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 211 $

import sys

from draco2.command.command import Command
from draco2.core.model import DracoModel, Role


class CreateRole(Command):
    """Create a role."""

    name = 'create'
    description = 'create a role'
    usage = '%prog [options] %command <role>'
    nargs = 1

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        roles = transaction.select(Role, 'name = %s', (name,))
        if roles:
            self.error('role "%s" already exist' % name)
            self.exit(1)
        role = Role()
        role['name'] = name
        transaction.insert(role)
        transaction.commit()
        self.write('role "%s" successfully created\n' % name)


class DropRole(Command):
    """Remove a role."""

    name = 'drop'
    description = 'remove a role'
    usage = '%prog [options] %command <role>'
    nargs = 1

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        roles = transaction.select(Role, 'name = %s', (name,))
        if not roles:
            self.error('role "%s" does not exist' % name)
            self.exit(1)
        role = roles[0]
        transaction.delete(role)
        transaction.commit()
        self.write('role "%s" successfully removed\n' % name)


class ListRoles(Command):
    """List all roles."""

    name = 'list'
    description = 'list roles'

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        roles = transaction.select(Role)
        for role in roles:
            sys.stdout.write('-> %s\n' % role['name'])


class RoleCommand(Command):
    """Role management."""

    name = 'role'
    description = 'manage roles'

    def __init__(self):
        super(RoleCommand, self).__init__()
        self.add_subcommand(CreateRole())
        self.add_subcommand(DropRole())
        self.add_subcommand(ListRoles())
