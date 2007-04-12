# vi: ts=8 sts=4 sw=4 et
#
# test_rwlock.py: unit tests for draco2.util.rwlock
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
import time
import threading
from Queue import Queue
import py.test

from draco2.util.rwlock import ReadWriteLock, LockingError


class TestRWLock(object):

    def _reader_thread(self, queue, lock):
        errors = 0
        while not self.m_stop:
            lock.acquire_read()
            sys.stdout.write('R')
            sys.stdout.flush()
            value = self.m_counter 
            time.sleep(0.1)
            if value != self.m_counter:
                errors += 1
            lock.release_read()
        queue.put(errors)

    def _writer_acquire_thread(self, queue, lock):
        lock.acquire_write()
        sys.stdout.write('W')
        sys.stdout.flush()
        value = self.m_counter
        time.sleep(0.1)
        self.m_counter = value + 1
        queue.put(True)
        lock.release_write()

    def _writer_update_thread(self, queue, lock):
        lock.acquire_read()
        lock.upgrade()
        sys.stdout.write('U')
        sys.stdout.flush()
        value = self.m_counter
        time.sleep(0.1)
        self.m_counter = value + 1
        queue.put(True)
        lock.downgrade()
        lock.release_read()

    def test_read_write(self):
        # Start read and write threads. Each write thread will read
        # counter, sleep for a while, increase a it and then exit. Read
        # threads read the counter, sleep for a while, and then assert
        # that the value is still identical. When all write threads are
        # finished, the read threads are stopped.  If all goes well, the
        # read threads have not signaled an error and the counter has
        # counted exactly the number of write thread times.
        threads = []
        nrthreads = 20
        nwthreads = 20
        rqueue = Queue(nrthreads)
        wqueue = Queue(nwthreads)
        self.m_stop = False
        self.m_counter = 0
        lock = ReadWriteLock()
        for i in range(nrthreads):
            threads.append(threading.Thread(target=self._reader_thread,
                                            args=(rqueue, lock)))
        for i in range(nwthreads/2):
            threads.append(threading.Thread(target=self._writer_acquire_thread,
                                            args=(wqueue, lock)))
        for i in range(nwthreads/2):
            threads.append(threading.Thread(target=self._writer_update_thread,
                                            args=(wqueue, lock)))
        for thread in threads:
            thread.start()
        for i in range(nwthreads):
            wqueue.get()
        self.m_stop = True
        for i in range(nrthreads):
            assert rqueue.get() == 0
        assert self.m_counter == nwthreads

    def test_lock_error(self):
        lock = ReadWriteLock()
        py.test.raises(LockingError, lock.release_read)
        py.test.raises(LockingError, lock.release_write)
        py.test.raises(LockingError, lock.upgrade)
        py.test.raises(LockingError, lock.downgrade)
        lock.acquire_read()
        py.test.raises(LockingError, lock.release_write)
        lock.upgrade()
        py.test.raises(LockingError, lock.release_read)
        lock.release_write()
