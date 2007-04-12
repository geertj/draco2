# vi: ts=8 sts=4 sw=4 et
#
# test_html.py: tests for draco2.util.html
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.util import html
from draco2.util.test.support import EncoderTest


class TestQuoteSgml(EncoderTest):

    quotechars = '&'
    unsafe = '<>&'

    encode_vectors = (
        ('Test<>123', 'Test&lt;&gt;123'),
        ('Test&lt;123', 'Test&amp;lt;123'),
        ('Test&123', 'Test&amp;123')
    )

    decode_vectors = (
        ('Test&lt;&gt;123', 'Test<>123'),
        ('Test&amp', 'Test&amp'),
        ('Test&unknown;123', 'Test&unknown;123'),
        ('Test&amp&amp;;', 'Test&amp&;')
    )

    def quote(self, s):
        return html.quote_html(s)

    def unquote(self, s):
        return html.unquote_html(s)
