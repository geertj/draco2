# vi: ts=8 sts=4 sw=4 et
#
# timezone.py: time zones
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
from datetime import timedelta, tzinfo


class GMT(tzinfo):
    """GMT timezone. This timezone is used with the RFC1123 dates
    required by the HTTP protocol.

    GMT does not have leap seconds, while UTC does. Therefore, it
    seems to me that utcoffset() should undo the effect of leap
    seconds. However, POSIX mandates leap seconds be unused, so
    many systems do not implement them.

    This class ignores leap seconds as well.
    """

    def tzname(self, dt):
        return 'GMT'

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)


class UTC(tzinfo):
    """UTC timezone."""

    def tzname(self, dt):
        return 'UTC'

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)


class LocalTime(tzinfo):
    """The local system time zone."""

    offset = timedelta(seconds=-time.timezone)
    dstoffset = timedelta(seconds=-time.altzone)
    nulloffset = timedelta(0)
    dstdelta = dstoffset - offset

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.dstoffset
        else:
            return self.offset

    def dst(self, dt):
        if self._isdst(dt):
            return self.dstdelta
        else:
            return self.nulloffset

    def _isdst(self, dt):
        t = time.mktime((dt.year, dt.month, dt.day,
                         dt.hour, dt.minute, dt.second,
                         dt.weekday(), 0, -1))
        tm = time.localtime(t)
        return tm.tm_isdst > 0
