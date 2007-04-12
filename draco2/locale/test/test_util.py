# vi: ts=8 sts=4 sw=4 et
#
# test_util.py: unit tests for draco2.locale.util
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import py.test
from draco2.locale import util


class TestParseLocale(object):

    data = (
        ('en-us', ('en', 'us')),
        ('nl-nl', ('nl', 'nl'))
    )

    def test_parse(self):
        for name,parsed in self.data:
            assert util.parse_locale(name) == parsed

    def test_create(self):
        for name,parsed in self.data:
            assert util.create_locale(parsed) == name

    def test_roundtrip(self):
        for name,parsed in self.data:
            assert util.create_locale(util.parse_locale(name)) == name

    def test_islocale(self):
        for name,parsed in self.data:
            assert util.islocale(name)

    def test_illegal(self):
        py.test.raises(TypeError, util.parse_locale, None)
        py.test.raises(TypeError, util.parse_locale, 10)
        py.test.raises(ValueError, util.parse_locale, 'illegal')
        py.test.raises(ValueError, util.parse_locale, 'il-leg-al')


class TestUtil(object):

    messages = [
        ('tr("test")', [('test', None, None)]),
        ("tr('test')", [('test', None, None)]),
        ('tr("""test""")', [('test', None, None)]),
        ("tr('''test''')", [('test', None, None)]),
        ('tr("test") test tr("test2")', [('test', None, None), ('test2', None, None)]),
        ('tr( "test")', [('test', None, None)]),
        ('tr( "test" )', [('test', None, None)]),
        ('tr("test" )', [('test', None, None)]),
        (' tr("test")', [('test', None, None)]),
        ('+tr("test")', [('test', None, None)]),
        ('atr("test")', []),
        ('tr("test"', []),
        ('tr("test\')', []),
        ('tr("test)', []),
        ('tr_mark("test")', [('test', None, None)]),
        ('tr("test", context="ctx")', [('test', 'ctx', None)]),
        ('tr("test", name="nm")', [('test', None, 'nm')]),
        ('tr("test", context="ctx", name="nm")', [('test', 'ctx', 'nm')]),
        ('tr("test" "test1")', [('testtest1', None, None)]),  # string catenation
        ('tr("test", "test1")', [('test', 'test1', None)]),  # positional arguments
        ('tr("test", "test1", "test2")', [('test', 'test1', 'test2')]),
        ('tr("test\ntest")', []),  # newline not allowed in single quoted string
        (r'tr("test\ntest")', [('test\ntest', None, None)]),  # newline escape
        ('tr("""test\ntest""")', [('test\ntest', None, None)]),
        ('tr("test\ttest")', [('test\ttest', None, None)]),
        ('tr(u"test")', [(u'test', None, None)]),
        (r'tr(u"test\u20ac")', [(u'test\u20ac', None, None)])  # unicode escape
    ]

    def test_extract(self):
        for s,ref in self.messages:
            messages = util.extract_messages(s)
            assert messages == ref
