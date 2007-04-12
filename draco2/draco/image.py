# vi: ts=8 sts=4 sw=4 et
#
# image.py: image info cache
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
import stat
import threading
import logging

from draco2.util.cache import LruCache
from draco2.util.image import get_image_info


class ImageInfo(object):
    """Get image info.

    The object's responsibility is to provide information on images in
    certain parts of the file system. The information returns in a
    3-tuple of (format, with, height).

    A LRU cache is used for efficiency. The cache is validated on every
    access by means of file modification time.

    This class is thread safe.
    """

    def __init__(self):
        """Constructor."""
        self.m_path = []
        self.m_cache = LruCache(1000)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        images = cls()
        docroot = api.request.docroot()
        images.add_path(docroot)
        config = api.config.ns('draco2.draco.image')
        if config.has_key('cachesize'):
            images._set_cache_size(config['cachesize'])
        if hasattr(api, 'changes'):
            images._set_change_manager(api.changes)
        return images

    def _set_change_manager(self, changes):
        """Set the change manager to `changes'."""
        ctx = changes.get_context('draco2.core.config')
        ctx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Reload config."""
        config = api.config.ns('draco2.draco.image')
        if config.has_key('cachesize'):
            self._set_cache_size(config['cachesize'])
        logger = logging.getLogger('draco2.draco.image')
        logger.debug('Reloaded due to config change.')

    def _set_cache_size(self, size):
        """Set the cache size."""
        self.m_cache.set_size(size)

    def add_path(self, path):
        """Add `path' to the image search path. """
        self.m_path.append(path)

    def get_info(self, fname):
        """Get image size for `fname'.

        The file `fname' is looked up in the path.
        """
        for path in self.m_path:
            # do not use os.path.join() as fname() may start with '/'
            fname = path + os.sep + fname
            try:
                st = os.stat(fname)
            except OSError:
                st = None
            if st and stat.S_ISREG(st.st_mode):
                break
        else:
            return
        mtime = st.st_mtime
        entry = self.m_cache.get(fname)
        if entry and entry[0] == mtime:
            return entry[1]
        info = get_image_info(fname)
        if not info:
            return
        entry = [mtime, info]
        self.m_cache.add(fname, entry)
        return info
