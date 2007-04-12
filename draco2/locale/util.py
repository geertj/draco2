# vi: ts=8 sts=4 sw=4 et
#
# util.py: message extraction
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


re_locale = re.compile('^([a-z][a-z])-([a-z][a-z])$')

def parse_locale(s):
    """Parse a locale string.

    This returns a tuple (language, territory).
    """
    if not isinstance(s, basestring):
        raise TypeError, 'Expecting string instance.'
    mobj = re_locale.match(s)
    if not mobj:
        raise ValueError, 'Illegal locale string.'
    return mobj.groups()

def create_locale(parsed):
    """Create a locale string.

    This is the inverse of parse_locale().
    """
    language, territory = parsed
    return '%s-%s' % (language, territory)

def islocale(locale):
    """Return True if `locale' is a locale."""
    return re_locale.match(locale) is not None


re_message = re.compile("""
    (?<![a-z_])
    tr(_mark)?\s*\(\s*
        (?P<message>([rRuU]*(?P<q1>'|"|'''|\"\"\")(.*?)(?<!\\\\)(?P=q1))+)
        (\s*,\s*(context\s*=\s*)?(?P<q2>'|")(?P<context>(.*?)(?<!\\\\))(?P=q2))?
        (\s*,\s*(name\s*=\s*)?(?P<q3>'|")(?P<name>(.*?)(?<!\\\\))(?P=q3))?
    \s*\)
    """, re.MULTILINE|re.DOTALL|re.VERBOSE)

def extract_messages(s):
    """Extract messages from a string `s'."""
    result = []
    for mobj in re_message.finditer(s):
        message = mobj.group('message')
        try:
            # Use Python to interpret \ sequences in strings.
            message = eval(message)
        except SyntaxError:
            continue
        context = mobj.group('context')  # value or None
        name = mobj.group('name')
        result.append((message, context, name))
    return result
