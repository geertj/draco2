# vi: ts=8 sts=4 sw=4 et
#
# test_util.py: unit tests for draco2.session.util
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import py.test
from draco2.session import util


class TestBaseSession(object):

    def test_invalid(self):
        py.test.raises(TypeError, util.isbasesession, None)
        py.test.raises(TypeError, util.isbasesession, 10)
        assert not util.isbasesession('invalid')

    def test_roundtrip(self):
        for i in range(100):
            sid = util.generate_basesession()
            dump = util.dump_basesession(sid)
            assert util.isbasesession(dump)
            parsed = util.parse_basesession(dump)
            assert sid == parsed

    def test_clash(self):
        sids = set()
        for i in range(100):
            sid = util.generate_basesession()
            assert sid not in sids
            sids.add(sid)


class TestSubSession(object):

    def test_invalid(self):
        py.test.raises(TypeError, util.issubsession, None)
        py.test.raises(TypeError, util.issubsession, 10)
        assert not util.issubsession('invalid')

    def test_roundtrip(self):
        for i in range(100):
            sub = util.generate_subsession()
            dump = util.dump_subsession(sub)
            assert util.issubsession(dump)
            parsed = util.parse_subsession(dump)
            assert sub == parsed

    def test_clash(self):
        subs = set()
        for i in range(100):
            sub = util.generate_subsession()
            assert sub not in subs
            subs.add(sub)


class TestSessionID(object):

    def test_invalid(self):
        py.test.raises(TypeError, util.issessionid, None)
        py.test.raises(TypeError, util.issessionid, 10)
        assert not util.issessionid('invalid')

    def test_roundtrip(self):
        for i in range(100):
            sess = util.generate_sessionid()
            dump = util.dump_sessionid(sess)
            assert util.issessionid(dump)
            parsed = util.parse_sessionid(dump)
            assert sess == parsed
        for i in range(100):
            sess = util.generate_sessionid()
            sess = (sess[0], None)
            dump = util.dump_sessionid(sess)
            assert util.issessionid(dump)
            parsed = util.parse_sessionid(dump)
            assert sess == parsed
        for i in range(100):
            sess = util.generate_sessionid()
            sess = (None, sess[1])
            dump = util.dump_sessionid(sess)
            assert util.issessionid(dump)
            parsed = util.parse_sessionid(dump)
            assert sess == parsed

    def test_clash(self):
        sessions = set()
        for i in range(100):
            sess = util.generate_sessionid()
            assert sess not in sessions
            sessions.add(sess)
