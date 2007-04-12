# vi: ts=8 sts=4 sw=4 et
#
# config.py: config commands
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

from draco2.core.model import Config
from draco2.command.command import Command


class SetConfig(Command):
    """Set a configuration key."""

    name = 'set'
    description = 'create a config item'
    usage = '%prog [options] %command <key> <value>'
    nargs = 2

    def run(self, opts, args, api):
        key, value = args
        model = api.models.model('draco')
        transaction = model.transaction()
        configs = transaction.select(Config, 'key = %s', (key,))
        if configs:
            config = configs[0]
            config['value'] = value
        else:
            config = Config(key=key, value=value)
            transaction.insert(config)
        transaction.commit()


class DeleteConfig(Command):
    """Delete a configuration key."""

    name = 'delete'
    description = 'delete a config item'
    usage = '%prog [options] %command <key>'
    nargs = 1

    def run(self, opts, args, api):
        key = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        configs = transaction.select(Config, 'key = %s', (key,))
        if not configs:
            self.error('configuration key "%s" does not exist' % key)
            self.exit(1)
        transaction.delete(configs[0])
        transaction.commit()


class ListConfig(Command):
    """List all configuration keys."""

    name = 'list'
    description = 'list all config items'

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        configs = transaction.select(Config)
        for config in configs:
            self.write('-> %s = %s\n' % (config['key'], config['value']))


class ConfigCommand(Command):
    """Configuration meta command."""

    name = 'config'
    description = 'manage configuration'

    def __init__(self):
        super(ConfigCommand, self).__init__()
        self.add_subcommand(SetConfig())
        self.add_subcommand(DeleteConfig())
        self.add_subcommand(ListConfig())
