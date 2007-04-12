# vi: ts=8 sts=4 sw=4 et
#
# loader.py: module loader
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
import sys
import imp
import stat
import logging

from draco2.core.exception import *
from draco2.util.misc import get_backtrace
from draco2.util.loader import module_from_path


class FileLoader(object):
    """Python 2.3 style module loader that loads a regular file."""

    def __init__(self, fname, loader=None):
        self.m_fname = fname
        self.m_loader = loader

    def load_module(self, fullname):
        """Load the module `fullname'."""
        fin = file(self.m_fname)
        try:
            code = fin.read()
            mod = imp.new_module(fullname)
            mod.__file__ = self.m_fname
            mod.__loader__ = self
            code = compile(code, self.m_fname, 'exec')
            exec code in mod.__dict__
            sys.modules[fullname] = mod
        finally:
            fin.close()
        if self.m_loader:
            self.m_loader._watch_module(mod)
        return mod


class PackageLoader(object):
    """Python 2.3 style module loader for an empty package directory."""

    def __init__(self, dname, loader=None):
        self.m_dname = dname
        self.m_loader = loader

    def load_module(self, fullname):
        """Return an empty module for `fullname'."""
        mod = imp.new_module(fullname)
        sys.modules[fullname] = mod
        mod.__file__ =  self.m_dname
        mod.__loader__ = self
        mod.__path__ = []
        return mod


class DracoImporter(object):
    """Python 2.3 style module importer.

    This importer is registered to sys.meta_path when Draco starts up.
    It is used to make the document root look like a single Python
    package.
    """

    def __init__(self, package, root, loader=None):
        self.m_package = package
        self.m_root = root
        self.m_loader = loader

    def find_module(self, fullname, path=None):
        """Return an importer object for the module `fullname'."""
        if not fullname.startswith(self.m_package):
            return
        fname = fullname[len(self.m_package)+1:].replace('.', '/')
        fname = os.path.normpath(self.m_root + '/' + fname)
        try:
            st = os.stat(fname)
        except OSError:
            st = None
        if st and stat.S_ISDIR(st.st_mode):
            return PackageLoader(fname, self.m_loader)
        fname += '.py'
        try:
            st = os.stat(fname)
        except OSError:
            st = None
        if st and stat.S_ISREG(st.st_mode):
            return FileLoader(fname, self.m_loader)


class Loader(object):
    """Draco Module loader.
    
    This loader is used by Draco to load files that define customization
    classes.
    """
 
    def __init__(self):
        """Constructor."""
        self.m_scopes = {}
        self.m_modules = set()
        self.m_changectx = None

    @classmethod
    def _create(cls, api):
        """Factory function to create a Loader object."""
        loader = cls()
        if hasattr(api, 'changes'):
            loader._set_change_manager(api.changes)
        docroot = api.options['documentroot']
        loader.add_scope('__docroot__', docroot)
        return loader

    def _set_change_manager(self, changes):
        """Use change manager `changes'."""
        context = changes.get_context('draco2.core.loader')
        context.add_callback(self._change_callback)
        self.m_changectx = context

    def _change_callback(self, api):
        """Callback that is run by the change manager whenever a file
        we loaded changed. This will clear all references to loaded
        modules. 
        """
        logger = logging.getLogger('draco2.core.loader')
        logger.info('Releasing %d modules.' % len(self.m_modules))
        for mod in self.m_modules:
            del sys.modules[mod]
        self.m_modules.clear()

    def _watch_module(self, module):
        """Watch module `module' for changes."""
        self.m_modules.add(module.__name__)
        if self.m_changectx:
            self.m_changectx.add_file(module.__file__)

    def add_scope(self, scope, dirbase):
        """Add a scope to the loader.
        
        A scope is a directory below which Python sources can be loaded.
        """
        self.m_scopes[scope] = dirbase
        importer = DracoImporter(scope, dirbase, self)
        sys.meta_path.insert(0, importer)

    def _import(self, modname):
        """Import a module `modname'."""
        try:
            mod = __import__(modname, globals(), locals())
        except SyntaxError, err:
            error = DracoSiteError('Syntax error in module.')
            error.filename = modname
            error.lineno = err.lineno
            error.backtrace = get_backtrace()
            raise error
        except (ImportError, Exception):
            error = DracoSiteError('Could not import module.')
            error.filename = modname
            error.backtrace = get_backtrace()
            raise error
        parts = modname.split('.')
        for part in parts[1:]:
            mod = getattr(mod, part)
        return mod

    def load_class(self, fname, typ, scope, default=None):
        """Load Python source `fname' in scope `scope' and look for
        subclasses of `typ'. Return a the lowest subclass of `typ' which
        is not `typ' itself.
        """
        clslist = self.load_classes(fname, typ, scope)
        if not clslist:
            return default
        clslist.sort(lambda x,y: len(x.__mro__) - len(y.__mro__))
        return clslist[-1]

    def load_classes(self, fname, typ, scope):
        """Load Python source `fname' in scope `scope' and look for
        subclasses of `typ'. Return a list of all strict subclasses,
        i.e. subclasses which are not the class itself.
        """
        if scope not in self.m_scopes:
            raise DracoSiteError, 'Unknown scope %s' % scope
        path = self.m_scopes[scope] + os.sep + fname
        try:
            st = os.stat(path)
        except OSError:
            # It is not an error to load from a non-existing module
            return []
        modname = module_from_path(scope, fname)
        try:
            mod = sys.modules[modname]
        except KeyError:
            mod = self._import(modname)
        clslist = []
        for symbol in dir(mod):
            try:
                attr = getattr(mod, symbol)
                if isinstance(attr, type) and issubclass(attr, typ) and \
                            attr.__module__ == mod.__name__:
                    clslist.append(attr)
            except (AttributeError, TypeError):
                pass
        return clslist
