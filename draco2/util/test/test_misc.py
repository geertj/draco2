# vi: ts=8 sts=4 sw=4 et
#
# test_misc: test suite for draco2.util.misc
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

from draco2.util.misc import dedent


class TestDedent(object):

    def test_null(self):
        s = ''
        assert dedent(s) == ''

    def test_zero_line(self):
        s = 'test line'
        assert dedent(s) == 'test line'
        s = '  test line'
        assert dedent(s) == 'test line'

    def test_one_line(self):
        s = 'line1\n'
        assert dedent(s) == 'line1'
        s = '  line1\n'
        assert dedent(s) == 'line1'

    def test_multi_line_with_first_line(self):
        s = 'line1\n  line2\n  line3\n'
        assert dedent(s) == 'line1\nline2\nline3'

    def test_multi_line_without_first_line(self):
        s = '\n  line2\n  line3\n'
        assert dedent(s) == 'line2\nline3'

    def test_multi_line_without_final_newline(self):
        s = 'line1\n  line2'
        assert dedent(s) == 'line1\nline2'

    def test_multi_line_with_increasing_indent(self):
        s = 'line1\n line2\n  line3\n   line4\n'
        assert dedent(s) == 'line1\nline2\n line3\n  line4'

    def test_multi_line_with_decreasing_indent(self):
        s = 'line1\n    line2\n   line3\n  line4\n'
        assert dedent(s) == 'line1\n  line2\n line3\nline4'

    def test_multi_line_with_trim(self):
        s = '\n\n\nline1\nline2\n\n\n'
        assert dedent(s) == 'line1\nline2'

    def test_multi_line_with_trim_and_indent(self):
        s = '\n\n\n  line1\n  line2\n\n\n'
        assert dedent(s) == 'line1\nline2'

    def test_multi_line_without_trim(self):
        s = '\n\n\nline1\nline2\n\n\n'
        assert dedent(s, trim=0) == '\n\n\nline1\nline2\n\n'

    def test_empty_line(self):
        s = '\n'
        assert dedent(s) == ''

    def test_empty_lines(self):
        s = '\n\n\n\n'
        assert dedent(s) == ''

    def test_whitespace(self):
        s = '    '
        assert dedent(s) == ''

    def test_whitespace_line(self):
        s = '    \n'
        assert dedent(s) == ''

    def test_whitespace_lines(self):
        s = '    \n    \n'
        assert dedent(s) == ''
