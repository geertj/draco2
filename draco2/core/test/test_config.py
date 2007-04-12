# vi: ts=8 sts=4 sw=4 et
#
# test_config.py: unit tests for config
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
import tempfile
import py.test

from draco2.core.api import API
from draco2.core.config import Config, ConfigSyntaxError
from draco2.util.misc import dedent
from draco2.util.namespace import Namespace, NamespaceError


class ConfigTest(object):

    def setup_class(cls):
        cls.files = []

    def teardown_class(cls):
        for fname in cls.files:
            os.unlink(fname)

    def config_file(self, text, fname=None):
        if fname is None:
            fname = tempfile.mktemp()
        fout = file(fname, 'w')
        fout.write(dedent(text))
        fout.close()
        if fname not in self.files:
            self.files.append(fname)
        return fname

    def create_config(self, text):
        fname = self.config_file(text)
        cfg = Config()
        cfg.add_file(fname)
        return cfg


class TestSyntax(ConfigTest):

    valid = \
        """
        # comment
        key1 = 'value'
        [section]
        key2 = 'value'
        # other comment
        # key3 = 'value
        key4 = 'value' # comment
        """

    invalid1 = \
        """
        key1 = 'value1
        """

    invalid2 = \
        """
        $ illegal comment
        key1 = 'value1'
        """

    invalid3 = \
        """
        key1 'value1'
        """

    invalid4 = \
        """
        [section1]]
        key1 = 'value1'
        """

    def test_syntax(self):
        cfg = self.create_config(self.valid)
        ns = cfg.ns()
        assert ns['key1'] == 'value'
        ns2 = cfg.ns('section')
        assert ns2['key2'] == 'value'
        assert not ns2.has_key('key3')
        assert ns2['key4'] == 'value'
        fname = self.config_file(self.invalid1)
        cfg = Config()
        py.test.raises(ConfigSyntaxError, cfg.add_file, fname)
        fname = self.config_file(self.invalid2)
        cfg = Config()
        py.test.raises(ConfigSyntaxError, cfg.add_file, fname)
        fname = self.config_file(self.invalid3)
        cfg = Config()
        py.test.raises(ConfigSyntaxError, cfg.add_file, fname)
        fname = self.config_file(self.invalid4)
        cfg = Config()
        py.test.raises(ConfigSyntaxError, cfg.add_file, fname)


class TestTypes(ConfigTest):

    cfgtext = \
        """
        key_none = None
        key_string = 'value'
        key_int = 10
        key_long = 10L
        key_float = 10.0
        key_tuple = (1, 2, 3)
        key_list = [1, 2, 3]
        key_dict = {1: None, 2: None, 3: None}
        """

    def test_types(self):
        cfg = self.create_config(self.cfgtext)
        ns = cfg.ns()
        assert ns['key_none'] is None
        assert ns['key_string'] == 'value'
        assert type(ns['key_string']) is str
        assert ns['key_int'] == 10
        assert type(ns['key_int']) is int
        assert ns['key_long'] == 10
        assert type(ns['key_long']) is long
        assert ns['key_float'] == 10.0
        assert type(ns['key_float']) is float
        assert ns['key_tuple'] == (1, 2, 3)
        assert type(ns['key_tuple']) is tuple
        assert ns['key_list'] == [1, 2, 3]
        assert type(ns['key_list']) is list
        assert ns['key_dict'] == {1: None, 2: None, 3: None}
        assert type(ns['key_dict']) is dict


class TestSection(ConfigTest):

    cfgtext = \
        """
        key1 = 'value01'
        key2 = 'value02'
        [section1]
        key1 = 'value11'
        key3 = 'value13'
        [section2]
        key1 = 'value21'
        key4 = 'value24'
        """

    def test_section(self):
        cfg = self.create_config(self.cfgtext)
        ns = cfg.ns()
        assert ns['key1'] == 'value01'
        assert ns['key2'] == 'value02'
        ns = cfg.ns('draco2')
        assert ns['key1'] == 'value01'
        assert ns['key2'] == 'value02'
        ns = cfg.ns('section1')
        assert ns['key1'] == 'value11'
        assert ns['key3'] == 'value13'
        ns = cfg.ns('section2')
        assert ns['key1'] == 'value21'
        assert ns['key4'] == 'value24'
        ns = cfg.ns('section3')
        assert not ns.has_key('key1')
        assert not ns.has_key('key2')
        assert not ns.has_key('key3')
        assert not ns.has_key('key4')
        assert len(cfg.sections()) == 3
        assert 'draco2' in cfg.sections()
        assert 'section1' in cfg.sections()
        assert 'section2' in cfg.sections()


class TestShadow(ConfigTest):

    cfgtext1 = \
        """
        [section1]
        key1 = 'value11'
        [section2]
        key2 = 'value12'
        """

    cfgtext2 = \
        """
        [section1]
        key1 = 'value21'
        [section3]
        key3 = 'value23'
        """

    def test_shadow(self):
        fname = self.config_file(self.cfgtext1)
        cfg = Config()
        cfg.add_file(fname)
        ns = cfg.ns('section1')
        assert ns['key1'] == 'value11'
        ns = cfg.ns('section2')
        assert ns['key2'] == 'value12'
        ns = cfg.ns('section3')
        assert not ns.has_key('key3')
        fname = self.config_file(self.cfgtext2)
        cfg.add_file(fname)
        ns = cfg.ns('section1')
        assert ns['key1'] == 'value21'
        ns = cfg.ns('section2')
        assert ns['key2'] == 'value12'
        ns = cfg.ns('section3')
        assert ns['key3'] == 'value23'


class TestReload(ConfigTest):

    cfgold = """
        [section1]
        key1 = 'value11'
        [section2]
        key2 = 'value12'
        """
    cfgnew = """
        [section1]
        key1 = 'value21'
        [section3]
        key3 = 'value23'
        """

    def test_reload(self):
        fname = self.config_file(self.cfgold)
        cfg = Config()
        cfg.add_file(fname)
        ns = cfg.ns('section1')
        assert ns['key1'] == 'value11'
        ns = cfg.ns('section2')
        assert ns['key2'] == 'value12'
        ns = cfg.ns('section3')
        assert not ns.has_key('key3')
        fname = self.config_file(self.cfgnew, fname=fname)
        api = API()
        cfg._change_callback(api)
        ns = cfg.ns('section1')
        assert ns['key1'] == 'value21'
        ns = cfg.ns('section2')
        assert not ns.has_key('key2')
        ns = cfg.ns('section3')
        assert ns['key3'] == 'value23'


class TestImplementation(ConfigTest):

    cfgtext = \
        """
        [section1]
        key1 = 'value1'
        """

    def test_implementation(self):
        cfg = self.create_config(self.cfgtext)
        ns1 = cfg.ns('section1')
        ns2 = cfg.namespace('section1')
        assert dict(ns1) == dict(ns2)
        ns = cfg.ns()
        assert isinstance(ns, Namespace)
        py.test.raises(NamespaceError, ns.__setitem__, 'key', 'value1')
        py.test.raises(NamespaceError, ns.__delitem__, 'key')


class TestTranslation(ConfigTest):

    cfgtext = \
        """
        [section1]
        key1 = 'value1'
        key1[en] = 'value2'
        key1[en@mod] = 'value3'
        """

    def test_translation(self):
        cfg = self.create_config(self.cfgtext)
        ns1 = cfg.ns('section1')
        assert ns1['key1'] == 'value1'
        cfg._set_language('en')
        ns2 = cfg.ns('section1')
        assert ns2['key1'] == 'value2'
        cfg._set_language('en@mod')
        ns3 = cfg.ns('section1')
        assert ns3['key1'] == 'value3'
