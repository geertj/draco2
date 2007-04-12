# vi: ts=4 sw=4 et
#
# env.py: setup environment variabels.
#
# This small utility outputs a bourne shell fragment that sets up the
# PATH and PYTHONPATH environment variables such that Draco can be used
# from within its source directory. This is required for the test suite,
# and is helpful for developing. Kudos to the py-lib team for the idea.
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.

import os
import os.path
import sys

def prepend_path(name, value):
    if sys.platform == 'win32':
        sep = ';'
    else:
        sep = ':'
    env_path = os.environ.get(name, '')
    parts = [ x for x in env_path.split(sep) if x ]
    while value in parts:
        del parts[parts.index(value)]
    parts.insert(0, value)
    return setenv(name, sep.join(parts))

def setenv(name, value):
    shell = os.environ.get('SHELL', '')
    comspec = os.environ.get('COMSPEC', '')
    if shell.endswith('csh'):
        cmd = 'setenv %s "%s"' % (name, value)
    elif shell.endswith('sh'):
        cmd = '%s="%s"; export %s' % (name, value, name)
    elif comspec.endswith('cmd.exe'):
        cmd = '@set %s=%s' % (name, value)
    else:
        assert False, 'Shell not supported.'
    return cmd


abspath = os.path.abspath(sys.argv[0])
topdir, fname = os.path.split(abspath)

bindir = os.path.join(topdir, 'bin')
print prepend_path('PATH', bindir)
pythondir = topdir
print prepend_path('PYTHONPATH', pythondir)
config = os.path.join(topdir, 'test.ini')
print setenv('TESTCONFIG', config)
bindir = os.path.join(topdir, 'bin')
print setenv('DRACO_BINDIRECTORY', bindir)
datadir = os.path.join(topdir, 'lib')
print setenv('DRACO_DATADIRECTORY', datadir)
