# vi: ts=8 sts=4 sw=4 et
#
# codecs.py: useful codecs
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import codecs
from draco2.util import uri
from draco2.util import html


class UrlCodec(codecs.Codec):
    """
    URL encoding codec. URL encoding encodes non-safe characters in %xx
    escape sequences.
    """

    def encode(input, errors=None):
        return uri.quote_url(input), len(input)

    encode = staticmethod(encode)

    def decode(input, errors=None):
        return uri.unquote_url(input), len(input)

    decode = staticmethod(decode)

class UrlStreamReader(UrlCodec, codecs.StreamReader):
    pass

class UrlStreamWriter(UrlCodec, codecs.StreamWriter):
    pass


class FormCodec(codecs.Codec):
    """
    Form encoding. This is similar to url encoding but ' ' is encoded
    as '+' and '/' is considered unsafe.
    """

    def encode(input, errors=None):
        return uri.quote_form(input), len(input)

    encode = staticmethod(encode)

    def decode(input, errors=None):
        return uri.unquote_form(input), len(input)

    decode = staticmethod(decode)

class FormStreamReader(FormCodec, codecs.StreamReader):
    pass

class FormStreamWriter(FormCodec, codecs.StreamWriter):
    pass


class HtmlCodec(codecs.Codec):
    """
    Html encoding, replace unsafe characters with their html entity.
    """

    def encode(input, errors=None):
        return html.quote_html(input), len(input)

    encode = staticmethod(encode)

    def decode(input, errors=None):
        return html.unquote_html(input), len(input)

    decode = staticmethod(decode)

class HtmlStreamReader(HtmlCodec, codecs.StreamReader):
    pass

class HtmlStreamWriter(HtmlCodec, codecs.StreamWriter):
    pass


class AttrCodec(codecs.Codec):
    """
    Html attribute encoding, replace " by &quot;.
    """

    def encode(input, errors=None):
        return html.quote_html(input, '"&'), len(input)

    encode = staticmethod(encode)

    def decode(input, errors=None):
        return html.unquote_html(input), len(input)

    decode = staticmethod(decode)

class AttrStreamReader(AttrCodec, codecs.StreamReader):
    pass

class AttrStreamWriter(AttrCodec, codecs.StreamWriter):
    pass


registry = \
{ 
    'url': (UrlCodec.encode, UrlCodec.decode, UrlStreamReader, UrlStreamWriter),
    'form': (FormCodec.encode, FormCodec.decode, FormStreamReader, FormStreamWriter),
    'html': (HtmlCodec.encode, HtmlCodec.decode, HtmlStreamReader, HtmlStreamWriter),
    'attr': (AttrCodec.encode, AttrCodec.decode, AttrStreamReader, AttrStreamWriter)
}

def search_codec(name):
    return registry.get(name)
