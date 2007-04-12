# vi: ts=8 sts=4 sw=4 et
#
# rwlock.py: a read-write lock
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import threading


class ContextManager(object):
    """Context manager for ReadWriteLock."""

    def __init__(self, lock):
        """Constructor."""
        self.m_lock = lock

    def __enter__(self):
        """Enter a "with" block."""
        self.m_lock.acquire_read()

    def __exit__(self, type, value, tb):
        """Leave a "with" block."""
        self.m_lock.release_read()


class LockingError(Exception):
    """A lock is not used properly."""


class ReadWriteLock(object):
    """A read-write lock.

    The lock can be taken by multiple threads in read mode but only
    once in write mode. A lock held in read mode can be upgraded to
    write mode, and vice-versa.
    """

    def __init__(self):
        """Constructor. """
        self.m_readers = 0
        self.m_writers = 0
        self.m_condition = threading.Condition()

    def __context__(self):
        """Return a context manager for "with" blocks."""
        return ContextManager(self)

    def acquire_read(self):
        """Acquire the lock in read mode. """
        self.m_condition.acquire()
        try:
            while self.m_writers > 0:
                self.m_condition.wait()
            self.m_readers += 1
        finally:
            self.m_condition.release()

    def release_read(self):
        """Release a read mode lock."""
        self.m_condition.acquire()
        try:
            if self.m_readers == 0:
                raise LockingError, 'release_read(): # of readers is 0'
            self.m_readers -= 1
            if self.m_readers == 0:
                self.m_condition.notifyAll()
        finally:
            self.m_condition.release()

    def acquire_write(self):
        """Acquire the lock in write mode."""
        self.m_condition.acquire()
        try:
            while self.m_writers > 0:
                self.m_condition.wait()
            self.m_writers += 1
            while self.m_readers > 0:
                self.m_condition.wait()
        finally:
            self.m_condition.release()

    def release_write(self):
        """Release a write mode lock."""
        self.m_condition.acquire()
        try:
            if self.m_writers == 0:
                raise LockingError, 'release_write(): # of writers is 0'
            self.m_writers -= 1
            assert self.m_writers == 0
            assert self.m_readers == 0
            self.m_condition.notifyAll()
        finally:
            self.m_condition.release()

    def upgrade(self):
        """Upgrade a read mode lock to a write."""
        self.m_condition.acquire()
        try:
            if self.m_readers == 0:
                raise LockingError, 'upgrade(): # of readers is 0'
            while self.m_writers > 0:
                self.m_condition.wait()
            self.m_writers += 1
            self.m_readers -= 1
            while self.m_readers > 0:
                self.m_condition.wait()
        finally:
            self.m_condition.release()

    def downgrade(self):
        """Downgrade a write mode lock to read."""
        self.m_condition.acquire()
        try:
            if self.m_writers == 0:
                raise LockingError, 'downgrade(): # of writers is 0'
            self.m_writers -= 1
            self.m_readers += 1
            assert self.m_writers == 0
            assert self.m_readers == 1
            self.m_condition.notifyAll()
        finally:
            self.m_condition.release()
