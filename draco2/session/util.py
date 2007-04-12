# vi: ts=8 sts=4 sw=4 et
#
# session.py: session management basics
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
import random


# Base session: a 128 bit random number.
# Serialized format: 32 char hex string. Python format: idem

re_basesession = re.compile('^([0-9a-f]{32})$')

def generate_basesession():
    """Create a new session id."""
    gen = random.SystemRandom()
    p0 = '%032x' % gen.getrandbits(128)
    return p0

def dump_basesession(basesession):
    """Dump a session id to a string."""
    return basesession

def parse_basesession(s):
    """Parse a session id from a string."""
    if not isbasesession(s):
        raise valueError, 'Illegal session id.'
    return s

def isbasesession(s):
    """Return True is 's' is a (syntactically valid) base session."""
    if not isinstance(s, basestring):
        m = 'Expecting string instance (got %s).'
        raise TypeError, m % type(s)
    mobj = re_basesession.match(s)
    return mobj is not None


# Subsession: 31 bit random number.
# Serialized format: '0x' + hexadecimal string. Python format: int.

re_subsession = re.compile('^(0x[0-9a-f]{2,8})$')

def generate_subsession():
    """Create a new subsession id."""
    gen = random.SystemRandom()
    p0 = gen.getrandbits(31)
    return p0

def dump_subsession(subsession):
    """Dump a subsession id to a string."""
    return '%#04x' % subsession

def parse_subsession(s):
    """Parse a subsession id (inverse of dump())."""
    if not issubsession(s):
        raise valueError, 'Illegal subsession id.'
    return int(s, 16)

def issubsession(s):
    """Return True is 's' is a (syntactically valid) session id."""
    if not isinstance(s, basestring):
        m = 'Expecting string instance (got %s).'
        raise TypeError, m % type(s)
    mobj = re_subsession.match(s)
    return mobj is not None


# Session ID: a combination of a session id and a subsession id,
# both parts optional.
# Serialized format: '%032x-%08x'. Python format: tuple(str, int).

re_sessionid = re.compile('^(?:([0-9a-f]{32})|([0-9a-f]{32})-(0x[0-9a-f]{2,8})'
                        '|(0x[0-9a-f]{2,8}))$')

def generate_sessionid():
    """Generate a new session id."""
    sid = generate_basesession()
    return (sid, 0)

def dump_sessionid(sessionid):
    """Create a new session id from its components."""
    parts = []
    if sessionid[0] is not None:
        parts.append(dump_basesession(sessionid[0]))
    if sessionid[1] is not None:
        parts.append(dump_subsession(sessionid[1]))
    s = '-'.join(parts)
    return s

def parse_sessionid(s):
    """Parse a session id (inverse of dump())."""
    if not issessionid(s):
        raise ValueErorr, 'Illegal session id.'
    parts = s.split('-')
    if len(parts) == 1:
        if isbasesession(parts[0]):
            sid = parse_basesession(parts[0])
            sub = None
        else:
            sid = None
            sub = parse_subsession(parts[0])
    else:
        sid = parse_basesession(parts[0])
        sub = parse_subsession(parts[1])
    return (sid, sub)

def issessionid(s):
    """Return True if `s' is a valid session id."""
    if not isinstance(s, basestring):
        m = 'Expecting string instance (got %s).'
        raise TypeError, m % type(s)
    mobj = re_sessionid.match(s)
    return mobj is not None
