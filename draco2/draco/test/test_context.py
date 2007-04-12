# vi: ts=8 sts=4 sw=4 et
#
# test_context.py: test suite for draco2.draco.context
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
import threading
from Queue import Queue

from draco2.draco.context import DracoContext


class BaseTestContext(object):

    context_class = None

    def setup_method(cls, method):
        cls.context = cls.context_class()

    def teardown_method(cls, method):
        # Required because py.test captures sys.stdout/err as well.
        cls.context._unregister_proxies()

    def test_eval(self):
        code = 'x'
        globals = { 'x': 10 }
        assert self.context.eval(code, globals=globals) == 10

    def test_run(self):
        code = 'print x'
        globals = { 'x': 10 }
        assert self.context.run(code, globals=globals) == ('10\n', '')

    def test_streams(self):
        code = 'import sys\n'
        code += 'print >>sys.stdout, "stdout"\n'
        code += 'print >>sys.stderr, "stderr"\n'
        assert self.context.run(code) == ('stdout\n', 'stderr\n')

    def test_default(self):
        code = 'x'
        assert self.context.eval(code) == ''

    def test_default_sub(self):
        code = '\ndef func():\n  return x\nprint func()\n'
        assert self.context.run(code) == ('\n', '')

    def test_update_locals(self):
        code = 'x = 10'
        globals = {}
        locals = {}
        self.context.run(code, globals=globals, locals=locals)
        assert locals['x'] == 10

    def test_update_globals(self):
        code = 'global x\nx = 10'
        globals = {}
        locals = {}
        self.context.run(code, globals=globals, locals=locals)
        assert globals['x'] == 10

    def test_exception(self):
        code = 'syntax error'
        py.test.raises(SyntaxError, self.context.run, code)
        code = 'raise TypeError'
        py.test.raises(TypeError, self.context.run, code)

    def test_unicode_output(self):
        code = r'print u"\u20ac"'
        assert self.context.run(code) == (u'\u20ac\n', '')

    def _test_thread_safety(self, queue):
        context = self.context_class()
        code = ['import time']
        for i in range(1000):
            code.append('print %d' % i)
            if not i % 100:
                code.append('time.sleep(0.1)')
        code = '\n'.join(code) + '\n'
        stdout, stderr = context.run(code)
        numbers = map(int, stdout.splitlines())
        sorted = numbers[:]
        sorted.sort()
        queue.put(numbers == sorted)

    def test_thread_safety(self):
        threads = []
        nthreads = 10
        queue = Queue(nthreads)
        for i in range(nthreads):
            threads.append(threading.Thread(target=self._test_thread_safety,
                                            args=(queue,)))
        for i in range(nthreads):
            threads[i].start()
        for i in range(nthreads):
            assert queue.get() is True
        for i in range(nthreads):
            threads[i].join()

class TestContext(BaseTestContext):

    context_class = DracoContext
