# vi: ts=8 sts=4 sw=4 et
#
# change.py: change management
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import threading
import logging


class ChangeContext(object):
    """A change context.
    
    This is a collection of objects and associated callbacks that need to
    be called when a change to an object is detected.
    """

    def __init__(self, name):
        """Constructor."""
        self.m_name = name
        self.m_lock = threading.Lock()
        self.m_objects = {}
        self.m_mtime = {}
        self.m_callbacks = []

    def _file_mtime(self, fname):
        """Return the modification date of file `fname'."""
        try:
            st = os.stat(fname)
            mtime = st.st_mtime
        except OSError:
            mtime = None
        return mtime

    def add_file(self, fname):
        """Add a file to the context."""
        name = 'file:' + fname
        self.m_objects[name] = (self._file_mtime, (fname,))
        self.m_mtime[name] = self._file_mtime(fname)

    def add_object(self, obname, func, *args):
        """Add a functional condition to the context."""
        name = 'object:' + obname
        self.m_objects[name] = (func, args)
        self.m_mtime[name] = func(*args)

    def add_callback(self, func):
        """Add a callback to the context."""
        self.m_callbacks.append(func)

    def run(self, rwlock, api):
        """Run the change context.
        
        The context is urn under lock `rwlock'. This checks the files
        and calls the callbacks if at least one of them has changed.
        """
        logger = logging.getLogger('draco2.core.change')
        # Do not wait for this lock. If another thread holds it, let
        # that take care of running the context. Waiting for the lock
        # would also result in a dead-lock between the global rwlock
        # and the per-context lock.
        if not self.m_lock.acquire(True):
            return
        try:
            changes = 0
            mtimes = {}
            # Do not use an iterator as m_objects can change while we are
            # looping over it, if other threads call .add_file(). And we
            # cannot take self.m_lock in .add_file() as that could again
            # lead to a deadlock with the global rwlock.
            for key in self.m_objects.keys():
                func,args = self.m_objects[key]
                mtime = func(*args)
                if mtime != self.m_mtime[key]:
                    changes += 1
                    mtimes[key] = mtime
            if changes:
                logger.info('Change detected in context %s.' % self.m_name)
                logger.info('Running %d calllbacks.' % len(self.m_callbacks))
                rwlock.upgrade()
                try:
                    for func in self.m_callbacks:
                        func(api)
                finally:
                    rwlock.downgrade()
                self.m_mtime.update(mtimes)
        finally:
            self.m_lock.release()
        return changes


class ChangeManager(object):
    """The change manager.
    
    This acts as a global repository for change contexts.
    """

    def __init__(self):
        """Constructor."""
        self.m_contexts = {}
        self.m_lock = threading.Lock()

    @classmethod
    def _create(cls, api):
        """Factory function to create a ChangeManager object."""
        changes = cls()
        return changes

    def get_context(self, name):
        """Return the change context `name'."""
        self.m_lock.acquire()
        try:
            if name not in self.m_contexts:
                self.m_contexts[name] = ChangeContext(name)
        finally:
            self.m_lock.release()
        return self.m_contexts[name]

    def run_context(self, name, rwlock, api):
        """Run the change context `name'.

        The context is run under lock `rwlock'. The lock must be a
        read-write lock that is currently held in read mode. If any
        callbacks are run, the lock is temporarily upgraded to write
        mode. The number of files that were changed is returned.
        """
        context = self.m_contexts[name]
        nfiles = context.run(rwlock, api)
        return nfiles

    def run_all_contexts(self, rwlock, api):
        """Run all registered change contexts."""
        nfiles = 0
        for name in self.m_contexts:
            nfiles += self.run_context(name, rwlock, api)
        return nfiles
