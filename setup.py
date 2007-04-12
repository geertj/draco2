# vi: ts=8 sts=4 sw=4 et
#
# setup.py: distutils setup script for Draco2
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
import os
import os.path
import re

from distutils import core
from distutils.command.install import install


def svn_revision():
    """Determine the subversion revision."""
    fin = os.popen('svn info')
    for line in fin:
        if not line:
            break
        line = line.rstrip()
        if line.startswith('Revision: '):
            revision = line[10:]
            return revision


class draco_install(install):
    """Extend distutils such as to patch some configuration settings
    into Draco just before installing.
    """

    def patch(self, fname, subs):
        template = "'(%s)'\s*:\s*'[\w/\\\\]*'"
        fin = file(fname)
        buf = fin.read()
        fin.close()
        orig = buf[:]
        for name,value in subs:
            regex = re.compile(template % name)
            buf = regex.sub("'\\1': '%s'" % value, buf, 1)
        if buf != orig:
            os.remove(fname)
            fout = open(fname, 'w')
            fout.write(buf)
            fout.close()

    def run(self):
        fname = os.path.join(self.build_lib, 'draco2', 'core', 'option.py')
        subs = []
        subs.append(('revision', svn_revision()))
        subs.append(('bindirectory', self.install_scripts))
        subs.append(('datadirectory', self.install_data + '/share/draco'))
        self.patch(fname, subs)
        install.run(self)


core.setup(
    cmdclass = { 'install': draco_install },
    name = 'Draco2',
    version = svn_revision(),
    author = 'Digital Fugue',
    author_email = 'geert@digitalfugue.com',
    license = 'Proprietary - All rights reserved',
    packages = ['draco2', 'draco2.command', 'draco2.core', 'draco2.database',
                'draco2.draco', 'draco2.draw', 'draco2.email', 'draco2.file',
                'draco2.form', 'draco2.interface', 'draco2.locale',
                'draco2.model', 'draco2.security', 'draco2.session',
                'draco2.util', 'draco2.webui', 'draco2.xmlrpc'],
    scripts = ['bin/draco2.py'],
    data_files = [('share/draco', ['lib/draco2.ini', 'lib/robots.ini',
                                   'lib/locale.ini'])])
