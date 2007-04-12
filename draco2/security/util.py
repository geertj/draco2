# vi: ts=8 sts=4 sw=4 et
#
# util.py: utilities for draco2.security
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import re
import random


# Authentication token: 128 bit random number.
# Serialized format: %032x, Python format: idem.

re_authtoken = re.compile('^([0-9a-f]{32})$')

def generate_authtoken():
    """Create a new authentication token.

    The authentication token has 128 bits of entropy.
    """
    gen = random.SystemRandom()
    p0 = '%032x' % gen.getrandbits(128)
    return p0

def dump_authtoken(authtok):
    """Create an authentication token from its components."""
    return authtok

def parse_authtoken(s):
    """Parse an authentication token."""
    if not isauthtoken(s):
        raise valueError, 'Illegal authentication token.'
    return s

def isauthtoken(s):
    """Return True is 's' is a (syntactically) valid auth token."""
    if not isinstance(s, basestring):
        m = 'Expecting string instance (got %s).'
        raise TypeError, m % type(s)
    mobj = re_authtoken.match(s)
    return mobj != None
