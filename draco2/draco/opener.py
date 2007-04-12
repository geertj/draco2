# vi: ts=8 sts=4 sw=4 et
#
# opener.py: resource opener
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
import os.path
import stat
import codecs

from draco2.util import http


class Opener(object):
    """Abstract base class for document openers."""

    @classmethod
    def _create(cls, api):
        cls = api.loader.load_class('__opener__.py', Opener,
                                    scope='__docroot__', default=cls)
        opener = cls()
        return opener
 
    def access(self, resource, mode=os.R_OK):
        """Return True if `mode' access to `resource' is allowed."""
        raise NotImplementedError

    def stat(self, resource):
        """Perform a stat() call on `resource'."""
        raise NotImplementedError

    def open(self, resource):
        """Open a resource.

        This function must return a file-like object on success, or
        raise an IOError on failure.
        """
        raise NotImplementedError


class DracoOpener(Opener):
    """An opener that provides document root/current directory semantics
    and language specific resource.
    """

    def __init__(self):
        self._set_document_root('/')
        self._set_current_directory('')
        self._set_language(None)

    @classmethod
    def _create(cls, api):
        opener = super(DracoOpener, cls)._create(api)
        opener._set_document_root(api.request.docroot())
        opener._set_current_directory(api.request.directory())
        opener._set_language(api.request.locale())
        return opener

    def _set_document_root(self, docroot):
        self.m_document_root = docroot

    def _set_current_directory(self, curdir):
        self.m_current_directory = curdir

    def _set_language(self, language):
        self.m_language = language

    def _resolve(self, fname):
        fname = os.path.normcase(fname)
        if fname.startswith(os.sep):
            path = self.m_document_root + fname
        else:
            path = os.path.join(self.m_document_root,
                                self.m_current_directory, fname)
        basename, ext = os.path.splitext(path)
        if self.m_language:
            fname = basename + '.' + self.m_language + ext
            try:
                st = os.stat(fname)
            except OSError:
                st = None
            if st and stat.S_ISREG(st.st_mode):
                return fname
        fname = basename + ext
        try:
            st = os.stat(fname)
        except OSError:
            st = None
        if st and stat.S_ISREG(st.st_mode):
            return fname

    def access(self, resource, mode=os.R_OK):
        fname = self._resolve(resource)
        if fname:
            return os.access(fname, mode)
        else:
            return False

    def stat(self, resource):
        fname = self._resolve(resource)
        return os.stat(fname)

    def open(self, resource):
        fname = self._resolve(resource)
        if fname is None:
            raise IOError, 'File does not exist: %s.' % resource
        fin = file(fname, 'rb')
        encoding = http.get_encoding(fin)
        fin.close()
        fin = codecs.open(fname, 'rbU', encoding)
        fin.name = fname
        return fin
