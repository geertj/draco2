# vi: ts=8 sts=4 sw=4 et
#
# test_urimod.py: tests for util.uri
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
import tempfile
import errno
import string

import py.test

from draco2.util import uri as urimod
from draco2.util.test.support import EncoderTest, inverse


class TestQuoteHex(EncoderTest):

    quotechars = '%'
    unsafe = inverse(string.lowercase + string.uppercase +
                     string.digits + '_.-')

    encode_vectors = (
        ('With spaces.', 'With%20spaces.'),
        ('With/slashes.', 'With%2Fslashes.'),
        ('With percent (%) sign.', 'With%20percent%20%28%25%29%20sign.'),
        ('With % at the end %', 'With%20%25%20at%20the%20end%20%25'),
        ('With escapes %20 %20', 'With%20escapes%20%2520%20%2520')
    )

    decode_vectors = (
        ('%%%%%', '%%%%%'),
        ('Test%20%', 'Test %'),
        ('Test%f', 'Test%f'),
        ('Test%ff', 'Test\xff')
    )

    def quote(self, s):
        return urimod.quote_hex(s)

    def unquote(self, s):
        return urimod.unquote_hex(s)


class TestQuoteUrl(EncoderTest):

    quotechars = '%'
    unsafe = inverse(string.lowercase + string.uppercase +
                     string.digits + '_.-/')

    encode_vectors = (
        ('With spaces.', 'With%20spaces.'),
        ('With/slashes.', 'With/slashes.'),
        ('With percent (%) sign.', 'With%20percent%20%28%25%29%20sign.'),
        ('With % at the end %', 'With%20%25%20at%20the%20end%20%25'),
        ('With escapes %20 %20', 'With%20escapes%20%2520%20%2520'),
        (u'With unicode \u20ac', 'With%20unicode%20%E2%82%AC')
    )

    decode_vectors = (
        ('%%%%%', '%%%%%'),
        ('Test%20%', 'Test %'),
        ('Test%f', 'Test%f'),
        ('Unicode%20%e2%82%ac', u'Unicode \u20ac')
    )

    def quote(self, s):
        return urimod.quote_url(s)

    def unquote(self, s):
        return urimod.unquote_url(s)


class TestQuoteForm(EncoderTest):

    quotechars = '%+'
    unsafe = inverse(string.lowercase + string.uppercase +
                     string.digits + '_.-')

    encode_vectors = (
        ('With spaces.', 'With+spaces.'),
        ('With/slashes.', 'With%2Fslashes.'),
        ('With percent (%) sign.', 'With+percent+%28%25%29+sign.'),
        ('With % at the end %', 'With+%25+at+the+end+%25'),
        ('With escapes %20 %20', 'With+escapes+%2520+%2520'),
        (u'With unicode \u20ac', 'With+unicode+%E2%82%AC')
    )

    decode_vectors = (
        ('%%%%%', '%%%%%'),
        ('Test+%', 'Test %'),
        ('Test%f', 'Test%f'),
        ('Unicode+%e2%82%ac', u'Unicode \u20ac')
    )

    def quote(self, s):
        return urimod.quote_form(s)

    def unquote(self, s):
        return urimod.unquote_form(s)



class TestParseURI(object):

    data = [
        ('', ('', '', '', '')),
        ('http:', ('http', '', '', '')),
        ('//hostname', ('', 'hostname', '', '')),
        ('//host.name', ('', 'host.name', '', '')),
        ('//hostname:80', ('', 'hostname:80', '', '')),
        ('path', ('', '', 'path', '')),
        ('/some/path/', ('', '', 'some/path/', '')),
        ('/some//path/', ('', '', 'some//path/', '')),
        ('?args', ('', '', '', 'args')),
        ('http://hostname', ('http', 'hostname', '', '')),
        ('http://hostname/path', ('http', 'hostname', 'path', '')),
        ('http://hostname/path/', ('http', 'hostname', 'path/', '')),
        ('http://hostname:80/path', ('http', 'hostname:80', 'path', '')),
        ('http://host.name:80/path', ('http', 'host.name:80', 'path', '')),
        ('http://hostname/path?args', ('http', 'hostname', 'path', 'args')),
        ('http://hostname/path/?args', ('http', 'hostname', 'path/', 'args')),
        ('http://hostname/path?args?args', ('http', 'hostname', 'path', 'args?args')),
        ('http:/', ('http', '', '', ''))
    ]

    def test_parse_uri(self):
        for uri,parts in self.data:
            assert urimod.parse_uri(uri) == parts


class TestParsePath(object):

    data = [
        ('', []),
        ('/', []),
        ('///', []),
        ('test', ['test']),
        ('/test', ['test']),
        ('/test/', ['test']),
        ('/test/', ['test']),
        ('dir/subdir', ['dir', 'subdir']),
        ('dir%20/sub%20dir', ['dir ', 'sub dir']),
        ('test%e2%82%ac', [u'test\u20ac'])
    ]

    def test_parse_path(self):
        for path,parts in self.data:
            assert urimod.parse_path(path) == parts


class TestParseQuery(object):

    data = [
        ('', {}),
        ('key', {}),
        ('key&', {}),
        ('key=', {'key': ['']}),
        ('key=value', {'key': ['value']}),
        ('key=value&key', {'key': ['value']}),
        ('key=value&key=value2', {'key': ['value', 'value2']}),
        ('key=value&key2=value2', {'key': ['value'], 'key2': ['value2']}),
        ('key=value%20', {'key': ['value ']}),
        ('key=value%e2%82%ac', {'key': [u'value\u20ac']}),
        ('key%e2%82%ac=value%e2%82%ac', {u'key\u20ac': [u'value\u20ac']})
    ]

    def test_parse_query(self):
        for query,args in self.data:
            assert urimod.parse_query(query) == args


class TestResolvePathURI(object):

    def setup_method(cls, method):
        tempdir = tempfile.gettempdir()
        subdir = 'dracotest_%d' % os.getpid()
        docroot = os.path.join(tempdir, subdir)
        os.mkdir(docroot)
        cls.docroot = docroot
        cls.directories = [docroot]

    def teardown_method(cls, method):
        for dir in reversed(cls.directories):
            os.rmdir(dir)
        cls.directories = []

    def create_reldir(self, dir):
        parts = [ x for x in dir.split('/') if x ]
        subdir = self.docroot
        for part in parts:
            subdir = os.path.join(subdir, part)
            try:
                os.mkdir(subdir)
                self.directories.append(subdir)
            except OSError, err:
                if err.errno != errno.EEXIST:
                    raise

    def test_resolve_path_uri(self):
        uri = '/dir/subdir/template.dsp/path/info'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('', 'dir', 'subdir/template.dsp/path/info')
        self.create_reldir('dir')
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir', 'subdir', 'template.dsp/path/info')
        self.create_reldir('dir/subdir')
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', 'template.dsp', 'path/info')
        uri = '/dir//subdir//template.dsp//path//info/'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', 'template.dsp', 'path/info')
        uri = '/dir/./subdir/template.dsp/path/info'
        py.test.raises(urimod.ResolutionError, urimod.resolve_path_uri,
                       uri, self.docroot)
        uri = '/dir/../subdir/template.dsp/path/info'
        py.test.raises(urimod.ResolutionError, urimod.resolve_path_uri,
                       uri, self.docroot)
        uri = '/dir/subdir/template.dsp/path/./info'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', 'template.dsp', 'path/./info')
        uri = '/dir/subdir/template.dsp/path/../info'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', 'template.dsp', 'path/../info')
        uri = '/dir/subdir/template.dsp/path/info'
        nonex = '%snon_existant_directory_%d' % (os.sep, os.getpid())
        py.test.raises(urimod.ResolutionError, urimod.resolve_path_uri,
                       uri, nonex)
        uri = '/dir/subdir'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', '', '')
        uri = '/dir/subdir/'
        parts = urimod.resolve_path_uri(uri, self.docroot)
        assert parts == ('dir/subdir', '', '')
