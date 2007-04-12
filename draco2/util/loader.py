# vi: ts=8 sts=4 sw=4 et
#
# loader.py: utilities for draco2.core.loader
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


def module_from_path(scope, path):
    """Convert a path name to a module name."""
    if path.endswith('.py'):
        path = path[:-3]
    path = path.replace('\\', '/')
    path = path.strip('/').replace('/', '.')
    modname = '%s.%s' % (scope, path)
    return modname

def path_from_module(scope, modname):
    """Convert a module name to a path."""
    if not modname.startswith(scope):
        return
    modname = modname[len(scope):]
    path = modname.replace('.', os.sep) + '.py'
    return path
