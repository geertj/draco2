# vi: ts=8 sts=4 sw=4 et
#
# test_uri.py: unit tests for draco2.draco.uri
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
import errno

from draco2.core.handler import Handler
from draco2.draco.uri import *
from draco2.draco.test.support import DracoURITest


class TestDracoURI(DracoURITest):

    def test_uri_from_method(self):
        handler = 'dir/subdir/__handler__.py'
        fname = self.create_docroot_file(handler)
        fout = file(fname, 'w')
        fout.write('from draco2.draco.handler import DracoHandler\n')
        fout.write('class TestHandler(DracoHandler):\n')
        fout.write('    def template(self, path, args):\n')
        fout.write('        pass\n')
        fout.close()
        cls = self.loader.load_class(handler, Handler, scope='__docroot__')
        obj = cls()
        uri = uri_from_method(obj.template, 'dsp')
        assert uri == '/dir/subdir/template.dsp'

    test_uris = (
        ('http://hostname/dir/subdir/template.dsp' \
         '/en-us/995063b888c1b19235063b888c1b1923-0x5160abcd/path/info?query',
            ('http', 'hostname', '', 'dir', '', '',
             'subdir/template.dsp/en-us/995063b888c1b19235063b888c1b1923-0x5160abcd/' \
             'path/info', 'query')),
        ('http://hostname/dir/subdir/template.dsp' \
         '/en-us/995063b888c1b19235063b888c1b1923-0x5160abcd/path/info?query',
            ('http', 'hostname', 'dir/subdir', 'template.dsp', 'en-us',
             '995063b888c1b19235063b888c1b1923-0x5160abcd', 'path/info', 'query')),
        ('http://hostname/dir/subdir/template.dsp' \
         '/EN/995063b888c1b19235063b888c1b1923-0x5160abcd/path/info?query',
            ('http', 'hostname', 'dir/subdir', 'template.dsp',
             '', '', 'EN/995063b888c1b19235063b888c1b1923-0x5160abcd/path/info',
             'query'))
    )

    def test_parse_uri(self):
        parts = parse_draco_uri(self.test_uris[0][0], self.docroot)
        assert parts == self.test_uris[0][1]
        self.create_docroot_directory('dir/subdir')
        for uri,ref in self.test_uris[1:]:
            parts = parse_draco_uri(uri, self.docroot)
            assert parts == ref

    def test_create_uri(self):
        for ref,parts in self.test_uris:
            uri = create_draco_uri(*parts)
            assert uri == ref
