# vi: ts=8 sts=4 sw=4 et
#
# config.py: configuration file parsing
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
import os.path
from draco2.core.exception import DracoError
from draco2.util.namespace import ReadOnlyNamespace


class ConfigError(DracoError):
    """A error has occurred in a configuration file. """

    def __init__(self, message, filename=None):
        self.message = message
        self.filename = filename

    def __str__(self):
        message = self.message
        if self.filename:
            message += '\nFile: %s' % self.filename
        return message


class ConfigSyntaxError(ConfigError):
    """A syntax error has occurred parsing a configuration file."""

    def __init__(self, filename, lineno):
        self.filename = filename
        self.lineno = lineno

    def __str__(self):
        return 'syntax error at %s:%d' % (self.filename, self.lineno)


class ConfigNamespace(ReadOnlyNamespace):
    """The configuration namespace.

    Each configuration namespace corresponds to a section from the
    Draco configuration file.
    """


class Config(object):
    """The Config object.

    This objects parses Draco's configuration files and provides
    access to the configuration namespaces.
    """

    re_ignore = re.compile('^\s*(#.*)?$')
    re_section = re.compile('^\s*\[\s*([\w.-]+)\s*\]\s*$')
    re_assign = re.compile('^\s*(\w+)\s*(?:\[([-\w_@.]+)\])?\s*=\s*(.*?)\s*$')

    def __init__(self, defaults=None):
        """Constructor."""
        self.m_sections = {}
        if defaults is None:
            defaults = {}
        self.m_defaults = defaults
        self.m_sections['draco2'] = self.m_defaults.copy()
        self.m_files = []
        self.m_changectx = None
        self.m_language = None

    @classmethod
    def _create(cls, api):
        """Factory function."""
        config = cls(api.options)
        if hasattr(api, 'changes'):
            config._set_change_manager(api.changes)
        docroot = api.options['documentroot']
        cfgname = api.options['configfile']
        fullname = os.path.join(docroot, cfgname)
        config.add_file(fullname)
        return config

    def _set_change_manager(self, changemgr):
        """Enable a change context. Must be called before _add_file()."""
        self.m_changectx = changemgr.get_context('draco2.core.config')
        self.m_changectx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Change callback function."""
        self.m_sections = {}
        self.m_sections['draco2'] = self.m_defaults.copy()
        for fname in self.m_files:
            self._parse_file(fname)

    def _set_language(self, language):
        """Set the language (for language dependent entries)."""
        self.m_language = language

    def add_file(self, fname):
        """Parse a configuration file `fname'."""
        try:
            self._parse_file(fname)
        except IOError:
            pass
        if self.m_changectx:
            self.m_changectx.add_file(fname)
        self.m_files.append(fname)

    def _parse_file(self, fname):
        """Parse the configuration file `fname'."""
        fin = file(fname)
        try:
            section = 'draco2'
            lineno = 0
            for line in fin:
                lineno += 1
                if self.re_ignore.match(line):
                    continue
                match = self.re_section.match(line)
                if match:
                    section = match.group(1)
                    continue
                match = self.re_assign.match(line)
                if not match:
                    raise ConfigSyntaxError(filename=fname, lineno=lineno)
                name = match.group(1).lower()
                language = match.group(2)
                try:
                    value = eval(match.group(3))
                except:
                    raise ConfigSyntaxError(filename=fname, lineno=lineno)
                if language:
                    key = (section, language)
                else:
                    key = section
                if key not in self.m_sections:
                    self.m_sections[key] = {}
                self.m_sections[key][name] = value
        finally:
            fin.close()

    def namespace(self, scope='draco2'):
        """Return the configuration namespace `scope'."""
        try:
            data = self.m_sections[scope].copy()
        except KeyError:
            data = {}
        try:
            data.update(self.m_sections[(scope, self.m_language)])
        except KeyError:
            pass
        ns = ConfigNamespace(data)
        return ns

    ns = namespace

    def sections(self):
        """Return a list of sections."""
        return self.m_sections.keys()
