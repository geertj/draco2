# vi: ts=8 sts=4 sw=4 et
#
# principal.py: principal commands
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 211 $

import os
import sys

from draco2.command.command import Command
from draco2.core.model import (DracoModel, Principal, Role,
                               PrincipalRoleRelationship)


class CreatePrincipal(Command):
    """Create a principal."""

    name = 'create'
    description = 'create a principal'
    usage = '%prog [options] %command <principal>'
    nargs = 1

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if principals:
            self.error('principal "%s" already exists' % name)
            self.exit(1)
        principal = Principal()
        principal['name'] = name
        transaction.insert(principal)
        transaction.commit()
        self.write('principal "%s" created successfully\n' % name)


class DropPrincipal(Command):
    """Remove a principal."""

    name = 'drop'
    description = 'remove a principal'
    usage = '%prog [options] %command <principal>'
    nargs = 1

    def run(self, opts, args, api):
        name = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if not principals:
            self.error('principal "%s" does not exist' % name)
            self.exit(1)
        principal = principals[0]
        transaction.delete(principal)
        transaction.commit()
        self.write('principal "%s" successfully removed\n' % name)


class ListPrincipals(Command):
    """List all principals."""

    name = 'list'
    description = 'list principals'

    def add_options(self, group):
        group.add_option('-p', '--private', action='store_true',
                         dest='private',
                         help='show private information')

    def set_defaults(self, parser):
        parser.set_default('private', False)

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal)
        for principal in principals:
            self.write('-> %s' % principal['name'])
            if opts.private and principal['password']:
                self.write(', password = "%s"' % principal['password'])
            if principal['certificate_dn']:
                self.write(', certificate_dn = "%s"' % principal['certificate'])
            join = (Role, 'role', PrincipalRoleRelationship, 'INNER')
            roles = transaction.select(Role, 'principal.name = %s',
                                       (principal['name'],), join=join)
            roles = ','.join([role['name'] for role in roles])
            if roles:
                self.write(', roles = "%s"' % roles)
            self.write('\n')


class SetPassword(Command):
    """Set a principal's password."""

    name = 'set_password'
    description = 'set a principal\'s password'
    usage = '%prog [options] %command <principal> <password>'
    nargs = 2

    def run(self, opts, args, api):
        name, password = args
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if not principals:
            self.error('principal "%s" does not exist' % name)
            self.exit(1)
        principal = principals[0]
        principal.set_password(password)
        transaction.commit()
        self.write('password for "%s" successfully set\n' % name)


class SetCertificate(Command):
    """Set a principal's certificate."""

    name = 'set_certificate'
    description = 'set a principal\'s certificate'
    usage = '%prog [options] %command <principal> <certificate>'
    nargs = 2

    def run(self, opts, args, api):
        name, certificate = args
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if not principals:
            self.error('principal "%s" does not exist' % name)
            self.exit(1)
        principal = principals[0]
        principal['certificate_dn'] = certificate
        transaction.commit()
        self.write('certificate for "%s" successfully set\n' % name)


class AddRole(Command):
    """Add a role to a principal."""

    name = 'add_role'
    description = 'add a role to a principal'
    usage = '%prog [options] %command <principal> <role>'
    nargs = 2

    def run(self, opts, args, api):
        name, role = args
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if not principals:
            self.error('principal "%s" does not exist' % name)
            self.exit(1)
        principal = principals[0]
        roles = transaction.select(Role, 'name = %s', (role,))
        if not roles:
            self.error('role "%s" does not exist' % role)
            self.exit(1)
        role = roles[0]
        result = transaction.select(PrincipalRoleRelationship,
                                    'principal_id = %s and role_name = %s',
                                    (principal['id'], role['name']))
        if result:
            self.error('principal "%s" already in role "%s"'
                       % (principal['name'], role['name']))
            self.exit(1)
        rel = PrincipalRoleRelationship()
        rel.set_role('principal', principal)
        rel.set_role('role', role)
        transaction.insert(rel)
        transaction.commit()
        self.write('principal "%s" successfully added to role "%s"\n'
                   % (principal['name'], role['name']))


class RemoveRole(Command):
    """Remove a role from a principal."""

    name = 'remove_role'
    description = 'remove a role from a principal'
    usage = '%prog [options] %command <principal> <role>'
    nargs = 2

    def run(self, opts, args, api):
        name, role = args
        model = api.models.model('draco')
        transaction = model.transaction()
        principals = transaction.select(Principal, 'name = %s', (name,))
        if not principals:
            self.error('principal "%s" does not exist' % name)
            self.exit(1)
        principal = principals[0]
        roles = transaction.select(Role, 'name = %s', (role,))
        if not roles:
            self.error('role "%s" does not exist' % role)
            self.exit(1)
        role = roles[0]
        result = transaction.select(PrincipalRoleRelationship,
                                    'principal_id = %s and role_name = %s',
                                    (principal['id'], role['name']))
        if not result:
            self.error('principal "%s" not in role "%s"'
                       % (principal['name'], role['name']))
            self.exit(1)
        rel = result[0]
        transaction.delete(rel)
        transaction.commit()
        self.write('principal "%s" successfully removed from role "%s"\n'
                   % (principal['name'], role['name']))


class PrincipalCommand(Command):
    """Schema management."""

    name = 'principal'
    description = 'manage principals'

    def __init__(self):
        super(PrincipalCommand, self).__init__()
        self.add_subcommand(CreatePrincipal())
        self.add_subcommand(DropPrincipal())
        self.add_subcommand(ListPrincipals())
        self.add_subcommand(SetPassword())
        self.add_subcommand(SetCertificate())
        self.add_subcommand(AddRole())
        self.add_subcommand(RemoveRole())
