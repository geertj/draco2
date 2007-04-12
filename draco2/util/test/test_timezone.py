# vi: ts=8 sts=4 sw=4 et
#
# test_timezone.py: unit tests for draco2.util.timezone
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import time
import datetime
from draco2.util.timezone import *


class TestTimezone(object):

    def test_timezone(self):
        tzutc = UTC()
        utc = datetime.datetime.utcnow().replace(tzinfo=tzutc)
        local = utc.astimezone(LocalTime())
        assert utc == local.astimezone(tzutc)
        assert utc.astimezone(LocalTime()) == utc
        t1 = time.mktime(utc.timetuple())
        t2 = time.mktime(local.timetuple())
        tzlocal = LocalTime()
        stdoffset = tzlocal.utcoffset(utc) - tzlocal.dst(utc)
        assert t2 - t1 == stdoffset.seconds
