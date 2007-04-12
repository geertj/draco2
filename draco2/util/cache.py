# vi: ts=8 sts=4 sw=4 et
#
# cache.py: a 2-threshold LRU cache
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import threading


class LruCache(object):
    """A 2-threshold LRU cache.

    The cache makes use of a low and a high watermark. If the number of
    entries in the cache reaches the high watermark, an expiration cycle
    is performed, discarding entries until we reach the low watermark.

    The advantage if this 2-threshold cache is that an expiry cycle is
    not needed on every addition.

    This object is thread safe.
    """

    def __init__(self, size):
        """Constructor."""
        self.m_time = 0
        self.m_cache = {}
        self.m_lock = threading.Lock()
        self.m_hits = 0
        self.m_misses = 0
        self.set_size(size)

    def _debug(self, logger):
        """Write debug output."""
        logger.debug('LRU cache statistics:')
        logger.debug('hits: %d' % self.m_hits)
        logger.debug('misses: %d' % self.m_misses)
        hitratio = 100.0 * self.m_hits / max(1, self.m_hits + self.m_misses)
        logger.debug('hit ratio: %.2f%%' % hitratio)
        logger.debug('current size: %d' % len(self.m_cache))
        logger.debug('maximum size: %d/%d' % (self.m_low, self.m_high))
        usage = 100.0 * len(self.m_cache) / max(1, self.m_high)
        logger.debug('current usage: %.2f%%' % usage)

    def set_size(self, size):
        """Set the cache size to `size'. This is the low watermark. The
        high watermark is set to `size' + 10%.
        """
        self.m_low = size
        self.m_high = size + max(1, int(0.1 * size))

    def get(self, key):
        """Return an entry from the cache."""
        try:
            value = self.m_cache[key]
            value[0] = self.m_time
            self.m_time += 1
            self.m_hits += 1
            return value[2]
        except KeyError:
            self.m_misses += 1

    def add(self, key, value):
        """Add an entry to the cache."""
        self.m_cache[key] = [self.m_time, key, value]
        self.m_time += 1
        self.expire()

    def clear(self):
        """Clear all entries from the cache."""
        self.m_cache.clear()

    def expire(self):
        """Expire entries.

        It is not necessary to call this function, it is automatically called
        on every add().
        """
        size = len(self.m_cache)
        if size < self.m_high:
            return
        if not self.m_lock.acquire(False):
            return
        try:
            expire = size - self.m_low
            assert expire > 0
            values = self.m_cache.values()
            values.sort()
            for time,key,value in values[:expire]:
                del self.m_cache[key]
        finally:
            self.m_lock.release()
