# vi: ts=8 sts=4 sw=4 et
#
# support.py: unit test support for draco2.draco
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
import os.path
import tempfile

from draco2.core.config import Config
from draco2.core.loader import Loader
from draco2.core.option import init_options


class DracoURITest(object):
    """Base class for draco2.draco URI related tests."""

    def setup_method(cls, method):
        tempdir = tempfile.gettempdir()
        subdir = 'dracotest_%d' % os.getpid()
        docroot = os.path.join(tempdir, subdir)
        os.mkdir(docroot)
        cls.docroot = docroot
        cls.files = []
        cls.directories = [docroot]
        options = { 'documentroot': docroot }
        options = init_options(options)
        config = Config(options)
        config.add_file(os.environ['TESTCONFIG'])
        cls.config = config
        loader = Loader()
        loader.add_scope('__docroot__', docroot)
        cls.loader = loader

    def teardown_method(cls, method):
        for file in cls.files:
            os.remove(file)
        for dir in reversed(cls.directories):
            os.rmdir(dir)
        cls.directories = []

    def create_docroot_directory(self, dname):
        parts = [ x for x in dname.split('/') if x ]
        subdir = self.docroot
        for part in parts:
            subdir = os.path.join(subdir, part)
            try:
                os.mkdir(subdir)
                self.directories.append(subdir)
            except OSError, err:
                if err.errno != errno.EEXIST:
                    raise
        return subdir

    def create_docroot_file(self, fname):
        p1 = fname.rfind('/')
        if p1 != -1:
            dname = fname[:p1]
            fname = fname[p1+1:]
        else:
            dname = ''
        dname = self.create_docroot_directory(dname)
        fname = os.path.join(dname, fname)
        fout = file(fname, 'w')
        fout.close()
        self.files.append(fname)
        return fname
