# vi: ts=8 sts=4 sw=4 et
#
# command.py: webui command parsing.
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


def parse_command(command):
    """Parse an webui command.

    The result is a 3-tuple: type, target, options.
    """
    try:
        type, target, option_string = command.split(':')
    except ValueError:
        raise ValueError, 'Illegal command.'
    options = {}
    if option_string:
        for opt in option_string.split(','):
            try:
                key, value = opt.split('=')
            except ValueError:
                raise ValueError, 'Illegal option in command.'
            options[key] = value
    return (type, target, options)


def create_command(type, target, options):
    """Create an webui command.

    This function is the opposite of parse_command().
    """
    option_string = ','.join(['%s=%s' % item for item in options.items()])
    command = '%s:%s:%s' % (type, target, option_string)
    return command
