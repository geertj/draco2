# vi: ts=8 sts=4 sw=4 et
#
# parser.py: the draco parser
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import re

from draco2.core.exception import DracoError
from draco2.draco.context import DracoContext
from draco2.draco.exception import ParseError
from draco2.util.misc import get_backtrace, dedent


class Parser(object):
    """Base class for all parsers.

    This interface is that of a basic feed parser.
    """

    # Different parsing modes (used when ectracting messages).
    PARSE = 0
    COLLECT_TEXT = 1
    COLLECT_CODE = 2

    @classmethod
    def _create(cls, api):
        """Factory method."""
        return cls()

    def parse(self, input, namespace=None, opener=None, mode=None):
        """Parse a document and return the parsed output.

        The document to be parsed is specified by `input'. It must be either
        a file name, or a file like object. The `namespace' argument
        specifies the namespace to use, `opener is an optional document
        opener, and `mode' specifies the parsing mode.
        """
        raise NotImplementedError

    def start(self, namespace=None, opener=None, mode=None):
        """Start feed parsing with `namespace' and `opener'.

        This method must be called if parsing with .feed().
        """
        raise NotImplementedError

    def feed(self, data, eof=False):
        """Feed data to the parser."""
        raise NotImplementedError

    def close(self):
        """Close parsing and result the result."""
        raise NotImplementedError


class Frame(object):
    """Frame object.

    This object represents one frame in a Draco call stack. The call stack
    is made out of templates that can recursively include each other.
    """

    def __init__(self, filename=None):
        if filename is None:
            filename = '<string>'
        self.filename = filename
        self.lineno = 1
        self.locals = {}
        self.buffer = ''
        self.result = []


class DracoParser(Parser):
    """The draco parser."""

    def parse(self, input, namespace=None, opener=None, mode=None):
        """Parse a document."""
        self._start(namespace, opener, mode)
        result = self.include(input)
        return result

    def _start(self, namespace=None, opener=None, mode=None):
        """INTERNAL: start parsing but do not yet allocate a frame."""
        if namespace is None:
            namespace = {}
        if mode is None:
            mode = self.PARSE
        self.m_globals = namespace.copy()
        self.m_context = DracoContext()
        self.m_opener = opener
        self.m_mode = mode
        self.m_frames = []

    def start(self, namespace=None, opener=None, mode=None):
        """Start parsing."""
        self._start(namespace, opener, mode)
        self.m_frames.append(Frame('<feed>'))

    def close(self):
        """Close parsing."""
        self.feed('', eof=True)
        return self._result()

    def _emit(self, data):
        """INTERNAL: emit output data."""
        self.m_frames[-1].result.append(data)

    def _result(self):
        """INTERNAL: return result."""
        return ''.join(self.m_frames[-1].result)

    def include(self, input, **kwargs):
        """Include a document.

        This function can be called by embedded code while parsing.
        """
        if len(self.m_frames) > 20:
            raise ParseError, 'Maximum recursion depth exceeded.'
        if hasattr(input, 'read'):
            fin = input
            fname = '<file object>'
            close = False
        else:
            try:
                if self.m_opener:
                    fin = self.m_opener.open(input)
                    fname = fin.name
                else:
                    fin = file(input, 'rbU')
                    fname = input
            except IOError:
                raise ParseError, 'Could not open input: %s' % input
            close = True
        self.m_frames.append(Frame(fname))
        self.m_frames[-1].locals.update(kwargs)
        while True:
            buf = fin.read(4096)
            if not buf:
                break
            self.feed(buf)
        self.feed(buf, eof=True)
        if close:
            fin.close()
        result = self._result()
        self.m_frames.pop()
        return result

    def _parse_error(self, message):
        """Raise a parse error."""
        error = ParseError(message)
        error.filename = self.m_frames[-1].filename
        error.lineno = self.m_frames[-1].lineno
        error.backtrace = get_backtrace()
        raise error

    # Any character that is valid for XML is valid for us.
    re_valid = re.compile('^[\t\r\n\x20-\xff]*$')
    re_valid_unicode = re.compile(u'^[\t\r\n\x20-\ud7ff\ue000-\ufffd'
                                   '\U00010000-\U0010FFFF]*$')

    def feed(self, data, eof=False):
        """Feed `data' to the parser."""
        if isinstance(data, str):
            validator = self.re_valid
        elif isinstance(data, unicode):
            validator = self.re_valid_unicode
        else:
            m = 'Expecting string or unicode object (got %s).'
            raise TypeError, m % type(data)
        if not validator.match(data):
            raise ParseError, 'Illegal string/unicode input.'
        buffer = self.m_frames[-1].buffer
        buffer += data
        p0 = 0
        while True:
            p1 = buffer.find('<%', p0)
            if p1 == -1:
                if buffer.endswith('<'):
                    p1 = len(buffer) - 1
                else:
                    p1 = len(buffer)
                if self.m_mode in (self.PARSE, self.COLLECT_TEXT):
                    self._emit(buffer[p0:p1])
                p0 = p1
                break
            if self.m_mode in (self.PARSE, self.COLLECT_TEXT):
                self._emit(buffer[p0:p1])
            self.m_frames[-1].lineno += buffer[p0:p1].count('\n')
            p0 = p1
            p1 = buffer.find('%>', p0+2)
            if p1 < 0:
                if not eof:
                    break
                self._parse_error('Premature EOF (unmatched <% tag)')
            if buffer[p0+2] == '@':
                self._parse_directive(buffer[p0+3:p1])
            elif buffer[p0+2] in '=+':
                if self.m_mode == self.PARSE:
                    res = self._parse_expression(buffer[p0+3:p1])
                    if type(res) not in (str, unicode):
                        res = str(res)
                    if buffer[p0+2] == '+':
                        res = res.encode('html')
                    self._emit(res)
                elif self.m_mode == self.COLLECT_CODE:
                    self._emit(dedent(buffer[p0+3:p1]) + '\n')
            else:
                if self.m_mode == self.PARSE:
                    res = self._parse_code(buffer[p0+2:p1])
                    self._emit(res)
                elif self.m_mode == self.COLLECT_CODE:
                    self._emit(dedent(buffer[p0+2:p1]) + '\n')
            self.m_frames[-1].lineno += buffer[p0:p1+2].count('\n')
            p0 = p1+2
        self.m_frames[-1].buffer = buffer[p0:]

    re_directive = re.compile("""
        \s*(?P<name>[a-z_][a-z_0-9:]+)\s*
        (?P<attributes>([a-z_][a-z_0-9:]*\s*=\s*("[^"&<]*"|'[^'&<]*')\s*)*)
        """, re.VERBOSE | re.IGNORECASE)

    re_attribute = re.compile("""
        \s*(?P<name>[a-z_][a-z_0-9:]*)\s*=\s*
        (?P<value>("[^"&<]*"|'[^'&<]*'))
        """, re.VERBOSE | re.IGNORECASE)

    def _parse_directive(self, buffer):
        """Parse an embedded directive: <%@ name [argn="valuen"]... %>."""
        mobj = self.re_directive.match(buffer)
        if not mobj:
            self._parse_error('Parse error in directive.')
        name = mobj.group('name')
        attributes = mobj.group('attributes')
        attrs = {}
        for mobj in self.re_attribute.finditer(attributes):
            # Convert attribute names to plain strings (no unicode) as
            # these are passed as keyword arguments to .include().
            attrs[str(mobj.group('name'))] = mobj.group('value')[1:-1]
        if name == 'include':
            self._directive_include(attrs)
        else:
            self._parse_error('Unknown directive: %s.' % name)

    def _directive_include(self, attrs):
        """Handle an include directive."""
        if attrs.has_key('file'):
            fname = attrs['file']
            del attrs['file']
        elif attrs.has_key('expr'):
            if self.m_mode == self.PARSE:
                fname = self._parse_expression(attrs['expr'])
            elif self.m_mode == self.COLLECT_CODE:
                self._emit(dedent(attrs['expr']) + '\n')
                fname = None
            else:
                fname = None
            del attrs['expr']
        else:
            self._parse_error('Include directive does not specify source.')
        kwargs = {}
        for key,value in attrs.items():
            if self.m_mode == self.PARSE:
                kwargs[key] = self._parse_expression(value)
            elif self.m_mode == self.COLLECT_CODE:
                self._emit(dedent(value) + '\n')
        if fname is not None:
            result = self.include(fname, **kwargs)
            self._emit(result)

    def _parse_expression(self, buffer):
        """Evaluate an expression: <%= expr %>."""
        try:
            result = self.m_context.eval(buffer, self.m_globals,
                                         self.m_frames[-1].locals,
                                         self.m_frames[-1].filename,
                                         self.m_frames[-1].lineno)
        except ParseError:
            raise  # pass through nested exceptions
        except SyntaxError:
            self._parse_error('Syntax error in expression.')
        except StandardError:
            self._parse_error('Uncaught exception in expression.')
        return result

    def _parse_code(self, buffer):
        """Run a clode block: <% code %>."""
        try:
            stdout, stderr = self.m_context.run(buffer, self.m_globals,
                                                self.m_frames[-1].locals,
                                                self.m_frames[-1].filename,
                                                self.m_frames[-1].lineno)
        except ParseError:
            raise
        except SyntaxError:
            self._parse_error('Syntax error in code block.')
        except StandardError:
            self._parse_error('Uncaught exception in code block.')
        return stdout
