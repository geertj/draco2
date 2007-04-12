# vi: ts=8 sts=4 sw=4 et
#
# test_http.py: tests for util.http
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
import time
import tempfile
import datetime
import locale

from draco2.util import http


class TestPaserUserAgent(object):
    """Test user agent parsing."""

    user_agents = [
        ('', ('', '', [])),
        ('agent', ('agent', '', [])),
        ('agent/1.0', ('agent', '1.0', [])),
        ('user agent/1.0', ('user agent', '1.0', [])),
        ('user agent/v1.0', ('user agent', 'v1.0', [])),
        ('agent 1.0', ('agent', '1.0', [])),
        ('agent/1.0 (data1)', ('agent', '1.0', ['data1'])),
        ('agent/1.0 (data1, data2)', ('agent', '1.0', ['data1', 'data2'])),
        ('agent/1.0 (data1; data2)', ('agent', '1.0', ['data1', 'data2'])),
        ('agent/1.0 (compatible; agent2/2.0)', ('agent2', '2.0', [])),
        ('agent/1.0 (compatible; agent2/2.0; data)', ('agent2', '2.0', ['data'])),
        ('agent/1.0 (compatible; agent 2.0; data)', ('agent', '2.0', ['data']))
    ]

    def test_parse_agent(self):
        for agent,ref in self.user_agents:
            parsed = http.parse_user_agent(agent)
            assert parsed == ref


class TestHTTP(object):

    def test_last_modified(self):
        now = datetime.datetime.utcnow()
        fobj = tempfile.NamedTemporaryFile()
        st = os.stat(fobj.name)
        modified = http.get_last_modified(st)
        tm = time.strptime(modified, http.rfc1123_datetime)
        moddate = datetime.datetime(*tm[:6])
        assert now - moddate < datetime.timedelta(seconds=5)

    def test_last_modified_locale_agnostic(self):
        current = locale.getlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'nl_NL')
        self.test_last_modified()
        locale.setlocale(locale.LC_ALL, current)
