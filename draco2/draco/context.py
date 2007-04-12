# vi: ts=8 sts=4 sw=4 et
#
# context.py: draco execution context
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
import threading
from StringIO import StringIO

from draco2.util.misc import dedent


class OutputProxy(object):
    """Output proxy.

    This proxy is used to incercept output on sys.stdout/err on demand,
    in a thread-safe and recursion-safe manner.
    """

    def __init__(self, stream):
        self.m_stream = stream
        self.m_tsd = threading.local()

    def stream(self):
        return self.m_stream

    def start_capture(self):
        try:
            self.m_tsd.buffers.append(StringIO())
        except AttributeError:
            self.m_tsd.buffers = [StringIO()]

    def stop_capture(self):
        try:
            buffer = self.m_tsd.buffers.pop()
        except (AttributeError, IndexError):
            return ''
        return buffer.getvalue()

    def write(self, buffer):
        try:
            self.m_tsd.buffers[-1].write(buffer)
        except (AttributeError, IndexError):
            self.m_stream.write(buffer)


class ExecutionContext(object):
    """Execution context.

    An execution context is responsible for executing Python expressions
    and code fragments.
    """

    def eval(self, expr, globals=None, locals=None, filename=None,
             lineno=None):
        """Evalutate an expression `expr' and return the result.

        The arguments `globals' and `locals' specify local and global
        namespaces, and are updated by the code.
        """
        raise NotImplementedError

    def run(self, code, globals=None, locals=None, filename=None,
           lineno=None):
        """Execute a piece of code and return its standard output.

        The arguments `globals' and `locals' specify local and global
        namespaces, and are updated by the code.
        """
        raise NotImplementedError


class DracoContext(ExecutionContext):
    """Draco execution context.
    
    The Draco execution context has the following characteristics:

    - Free variables will get a default value of ''.
    - Output done with normal print statement is captured and returned
      as the output of .run().
    """

    c_init = False
    c_lock = threading.Lock()

    def __init__(self):
        """Constructor."""
        if not self.c_init:
            self._register_proxies()

    @classmethod
    def _register_proxies(cls):
        """Set IO capture proxies. This is done only once per
        interpreter."""
        cls.c_lock.acquire()
        try:
            if not isinstance(sys.stdout, OutputProxy):
                sys.stdout = OutputProxy(sys.stdout)
            if not isinstance(sys.stderr, OutputProxy):
                sys.stderr = OutputProxy(sys.stderr)
            cls.c_init = True
        finally:
            cls.c_lock.release()

    @classmethod
    def _unregister_proxies(cls):
        """Unregister IO proxies."""
        cls.c_lock.acquire()
        try:
            if isinstance(sys.stdout, OutputProxy):
                sys.stdout = sys.stdout.stream()
            if isinstance(sys.stderr, OutputProxy):
                sys.stderr = sys.stderr.stream()
            cls.c_init = False
        finally:
            cls.c_lock.release()

    def _add_builtins(self, globals):
        """Add reference to __builtins__ to the globals dictionary."""
        # The contents of __builtins__ are accessed through sys.modules
        # because __builtins__ (note the 's') is sometimes a dict and
        # sometimes a module.
        # http://mail.python.org/pipermail/pythonmac-sig/2001-April/003285.html
        if not globals.has_key('__builtins__'):
            globals['__builtins__'] = sys.modules['__builtin__']

    def _add_defaults(self, code, globals, locals):
        """Add default values for free variables."""
        # For each free variable in the block, and free variables in sub
        # blocks, add a default value to the global namespace. The value is
        # added to the global namespace as there is no way to change the
        # local namespaces of sub blocks.  Another way of doing this is to
        # have a customizes dictionary that generated default values on
        # lookup. As of python 2.4.2 however, it is still not possible to
        # have a customized dictionary for the global namespace (it is
        # possible for the local namespace).
        for name in code.co_names:
            if name not in locals and name not in globals \
                        and not hasattr(globals['__builtins__'], name) \
                        and name not in code.co_varnames \
                        and '.' not in name:
                globals[name] = ''
        for obj in code.co_consts:
            if type(obj) is type(code):
                self._add_defaults(obj, globals, locals)

    def _compile(self, code, filename, lineno, type):
        """Compile a piece of code (and make line numbers work)."""
        code = '\n' * (lineno - 1) + code + '\n'
        code = compile(code, filename, type)
        return code

    def eval(self, expr, globals=None, locals=None, filename=None,
             lineno=None):
        """Evaluate the expression `expr'."""
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if filename is None:
            filename = '<string>'
        if lineno is None:
            lineno = 1
        expr = dedent(expr, trim=0)
        code = self._compile(expr, filename, lineno, 'eval')
        self._add_builtins(globals)
        self._add_defaults(code, globals, locals)
        result = eval(code, globals, locals)
        return result

    def run(self, code, globals=None, locals=None, filename=None,
            lineno=None):
        """Execute the code block `code' in the environment."""
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if filename is None:
            filename = '<string>'
        if lineno is None:
            lineno = 1
        sys.stdout.start_capture()
        sys.stderr.start_capture()
        try:
            code = dedent(code, trim=0)
            code = self._compile(code, filename, lineno, 'exec')
            self._add_builtins(globals)
            self._add_defaults(code, globals, locals)
            eval(code, globals, locals)
        finally:
            stdout = sys.stdout.stop_capture()
            stderr = sys.stderr.stop_capture()
        return (stdout, stderr)
