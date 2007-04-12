# vi: ts=8 sts=4 sw=4 et
#
# misc.py: various utility functions
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import sys
import traceback
import md5


def md5sum(data):
    """Return the MD5 sum of `data'."""
    md = md5.new()
    md.update(data)
    return md.hexdigest().lower()


def get_backtrace():
    """Return a backtrace from the last exception that occured."""
    type, value, trace = sys.exc_info()
    if type is None:
        return  # no exception being handled
    mesg = traceback.format_exception(type, value, trace)
    trace = None  # See python docs
    return ''.join(mesg)


def dedent(s, trim=1):
    """De-indent a multiline string. The algorithm is the algorithm
    for multi-line docstrings described in PEP257.
    """
    if s.find('\n') == -1:
        return  s.strip()
    lines = s.expandtabs().splitlines()
    level = None
    for li in lines[1:]:
        if li and not li.isspace():
            linelevel = 0
            while li[linelevel].isspace():
                linelevel += 1
            if level is None:
                level = linelevel
            else:
                level = min(level, linelevel)
    if level is None:
        level = 0  # all empty lines
    lines = [ lines[0].strip() ] + \
            [ li[level:].rstrip() for li in lines[1:] ]
    if trim:
        for lo in range(len(lines)):
            if lines[lo] and not lines[lo].isspace():
                break
        for hi in range(len(lines),0,-1):
            if lines[hi-1] and not lines[hi-1].isspace():
                break
        lines = lines[lo:hi]
    return '\n'.join(lines)
