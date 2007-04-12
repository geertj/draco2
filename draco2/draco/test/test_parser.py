# vi: ts=8 sts=4 sw=4 et
#
# test_parser.py: test suite for draco parser
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
from StringIO import StringIO

from draco2.draco.exception import ParseError
from draco2.draco.parser import Parser, DracoParser
from draco2.draco.opener import Opener


class VirtualOpener(Opener):

    def __init__(self):
        self.m_files = {}

    def add_file(self, name, data):
        self.m_files[name] = data

    def open(self, name):
        io = StringIO(self.m_files[name])
        io.name = '<string>'
        return io


class BaseTestParser(object):

    parser_class = None

    def setup_method(cls, method):
        cls.parser = cls.parser_class()

    def teardown_method(cls, method):
        # Required because py.test hooks sys.stdout/err as well
        cls.parser.m_context._unregister_proxies()

    def test_simple(self):
        io = StringIO('test')
        assert self.parser.parse(io) == 'test'
        io = StringIO(u'test\u20ac')
        assert self.parser.parse(io) == u'test\u20ac'

    def test_invalid_char(self):
        io = StringIO('\v\a')
        parser = self.parser
        py.test.raises(ParseError, parser.parse, io)
        io = StringIO(u'\ud800')
        py.test.raises(ParseError, parser.parse, io)

    def test_expression(self):
        io = StringIO('<%= test %>')
        ns = { 'test': 'value' }
        assert self.parser.parse(io, ns) == 'value'

    def test_expression_non_string(self):
        io = StringIO('<%= test %>')
        ns = { 'test': 10 }
        assert self.parser.parse(io, ns) == '10'

    def test_code(self):
        io = StringIO('<% print test %>')
        ns = { 'test': 'value' }
        assert self.parser.parse(io, ns) == 'value\n'

    def test_code_unbalanced(self):
        io = StringIO('<% print test')
        py.test.raises(ParseError, self.parser.parse, io)

    def test_expression_syntax_error(self):
        io = StringIO('<%= syntax error %>')
        py.test.raises(ParseError, self.parser.parse, io)

    def test_expression_exception(self):
        io = StringIO('<%= 1/0 %>')
        py.test.raises(ParseError, self.parser.parse, io)

    def test_code_syntax_error(self):
        io = StringIO('<% syntax error %>')
        py.test.raises(ParseError, self.parser.parse, io)

    def test_code_exception(self):
        io = StringIO('<% 1/0 %>')
        py.test.raises(ParseError, self.parser.parse, io)

    def test_feed(self):
        data = '<% print "test" %>'
        parser = self.parser
        parser.start()
        for char in data:
            parser.feed(char)
        assert parser.close() == 'test\n'

    def test_feed_unbalanced(self):
        parser = self.parser
        parser.start()
        parser.feed('<% print test')
        py.test.raises(ParseError, parser.close)

    def test_opener(self):
        opener = VirtualOpener()
        opener.add_file('file0', 'test')
        assert self.parser.parse('file0', opener=opener) == 'test'

    def test_include(self):
        opener = VirtualOpener()
        opener.add_file('file0', 'test0 <%@ include file="file1" %>')
        opener.add_file('file1', 'test1')
        assert self.parser.parse('file0', opener=opener) == 'test0 test1'

    def test_recursion_loop(self):
        opener = VirtualOpener()
        opener.add_file('file0', 'test0 <%@ include file="file0" %>')
        py.test.raises(ParseError, self.parser.parse, 'file0', None, opener)

    def test_local_namespace_communication(self):
        io = StringIO("""
            <%
                test = 'value'
            %>
            test string
            <%
                print test
            %>""")
        result = self.parser.parse(io)
        words = result.split()
        assert words == ['test', 'string', 'value' ]

    def test_global_namespace_communication(self):
        io = StringIO("""
            <%
                global test
                test = 'value'
            %>
            test string
            <%
                print test
            %>""")
        result = self.parser.parse(io)
        words = result.split()
        assert words == ['test', 'string', 'value']

    def test_global_namespace_include_communication(self):
        io = StringIO("""
            <%
                global test
                test = 'value'
            %>
            test string
            <%@ include file="file1" %>
            """)
        opener = VirtualOpener()
        opener.add_file('file1', '<% print test %>')
        result = self.parser.parse(io, opener=opener)
        words = result.split()
        assert words == ['test', 'string', 'value']

    def test_local_namespace_include_communication(self):
        io = StringIO("""
            <%
                test = 'value'
            %>
            test string
            <%@ include file="file1" %>
            """)
        opener = VirtualOpener()
        opener.add_file('file1', '<% print test %>')
        result = self.parser.parse(io, opener=opener)
        words = result.split()
        assert words == ['test', 'string']

    def test_include_arguments(self):
        io = StringIO("""
            <%
                obj1 = 'test1'
            %>
            test string
            <%@ include file="file1" arg1="obj1" %>
            """)
        opener = VirtualOpener()
        opener.add_file('file1', '<% print arg1 %>')
        result = self.parser.parse(io, opener=opener)
        words = result.split()
        assert words == ['test', 'string', 'test1']

    def test_collect_text_simple(self):
        io = StringIO("""
            <%
                print 'code'
            %>
            test text
            """)
        result = self.parser.parse(io, mode=Parser.COLLECT_TEXT)
        words = result.split()
        assert words == ['test', 'text']

    def test_collect_text_include(self):
        io = StringIO("""
            test text
            <%@ include file="file1" %>
            """)
        opener = VirtualOpener()
        opener.add_file('file1', 'included')
        result = self.parser.parse(io, opener=opener, mode=Parser.COLLECT_TEXT)
        words = result.split()
        assert words == ['test', 'text', 'included']

    def test_collect_code_simple(self):
        io = StringIO("""
            <%= expression %>
            <%
                print code
            %>
            test text
            """)
        result = self.parser.parse(io, mode=Parser.COLLECT_CODE)
        words = result.split()
        assert words == ['expression', 'print', 'code']
        

    def test_collect_code_include(self):
        io = StringIO("""
            <%@ include file="file1" arg1="test1" arg2="test2" %>
            test text
            """)
        opener = VirtualOpener()
        opener.add_file('file1', '<% print code %>')
        result = self.parser.parse(io, opener=opener, mode=Parser.COLLECT_CODE)
        words = result.split()
        assert words == ['test1', 'test2', 'print', 'code']

    def test_parser_include(self):
        io = StringIO("""
            test1
            <%
                print 'test2'
                print parser.include('file1')
                print 'test4'
            %>
            test5
            """)
        opener = VirtualOpener()
        opener.add_file('file1', '<% print "test3" %>')
        namespace = { 'parser': self.parser }
        result = self.parser.parse(io, namespace=namespace, opener=opener)
        words = result.split()
        assert words == ['test1', 'test2', 'test3', 'test4', 'test5']

    def test_successive_parses(self):
        io = StringIO("""
            test1
            <%
                print 'test2'
            %>
            test3
            """)
        result = self.parser.parse(io)
        words = result.split()
        assert words == ['test1', 'test2', 'test3']
        io.seek(0)
        result = self.parser.parse(io)
        words = result.split()
        assert words == ['test1', 'test2', 'test3']


class TestDracoParser(BaseTestParser):

    parser_class = DracoParser
