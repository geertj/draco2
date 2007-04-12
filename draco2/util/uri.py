# vi: ts=8 sts=4 sw=4 et
#
# uri.py: various URI related utilties
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
import os.path
import re
import stat


# URL/Form encoding

safe_chars = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              'abcdefghijklmnopqrstuvwxyz'
              '0123456789' '_.-')

def quote_hex(s, safe=''):
    """
    Replace potentially unsafe characters in 's' with their %XX hexadecimal
    counterparts. You can pass additional safe characters in `safe'.
    """
    res = list(s)
    safe += safe_chars
    for i in range(len(s)):
        c = res[i]
        if c not in safe:
            res[i] = '%%%02X' % ord(c)
    return ''.join(res)

def unquote_hex(s):
    """
    Change %XX occurences in `s' with their character value. 
    Does the opposite of quote_url().
    """
    lst = s.split('%')
    res = [lst[0]]
    for s in lst[1:]:
        if len(s) >= 2:
            try:
                c = chr(int(s[:2], 16))
                res.append(c + s[2:])
            except ValueError:
                res.append('%' + s)
        else:
            res.append('%' + s)
    return ''.join(res)

def quote_url(s):
    """URL encode a string."""
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return quote_hex(s, '/')

def unquote_url(s):
    """Decode an URL encoded string."""
    s = unquote_hex(s)
    s = s.decode('utf-8')
    return s

def quote_form(s):
    """Form encode a string."""
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    s = quote_hex(s, ' ')
    s = s.replace(' ', '+')
    return s

def unquote_form(s):
    """Decode a form encoded string."""
    s = s.replace('+', ' ')
    s = unquote_hex(s)
    s = s.decode('utf-8')
    return s


# URI parsing

re_uri = re.compile('(?:([^:/?]*):)?(?://([^?/]*))?(?:/?([^?]*))(?:\?(.*))?')

def parse_uri(uri):
    """Parse an URI into its components.

    The result is a 4-tuple (scheme, host, path, query).

    Note: This function only supports the "hier_part" URL format as
    defined in RFC2396 section 3. The "opaque_part" format is not
    supported.
    """
    mobj = re_uri.match(uri)
    assert mobj
    result = list(mobj.groups())
    for i,value in enumerate(result):
        if result[i] is None:
            result[i] = ''
    return tuple(result)

def create_uri(scheme=None, host=None, path=None, query=None):
    """Create an URI from its components."""
    uri = ''
    if scheme:
        uri += '%s:' % scheme
    if host:
        uri += '//%s' % host
    if path:
        uri += '/%s' % path
    if query:
        uri += '?%s' % query
    return uri

def parse_path(path):
    """Parse the "path" component of an URI.

    The result is a list of path components.
    """
    parts = [ unquote_url(pa) for pa in path.split('/') if pa ]
    return parts

def create_path(parts):
    """Create a "path" component of an URI.

    This function is the reverse of parse_path().
    """
    parts = [ quote_url(pa) for pa in parts ]
    path = '/'.join(parts)
    return path

def parse_query(query):
    """Parse the "query" component of an URI.

    The result is a dictionary that maps a string key to a list with
    one or more string values.
    """
    args = {}
    parts = query.split('&')
    for pa in parts:
        try:
            name, value = pa.split('=')
        except ValueError:
            continue
        name = unquote_form(name)
        value = unquote_form(value)
        try:
            args[name].append(value)
        except KeyError:
            args[name] = [value]
    return args

def create_query(args):
    """Create the "query" component of an URI.

    This function is the reverse of parse_query().
    """
    args = [ '%s=%s' % (quote_form(key), quote_form(value))
                        for key,value in args.items() ]
    query = '&'.join(args)
    return query


# URL path resolution

class ResolutionError(Exception):
    pass

def resolve_path_uri(path, docroot):
    """Resolves the path part of an URI.

    The URI is resolved to the 3-tuple: directory, filename, pathinfo.
    The filename component is either empty or a single path component,
    and may or may not exist as a physical file. The pathinfo component
    consists of zero or more path components.
    """
    try:
        st = os.stat(docroot)
    except OSError:
        st = None
    if st is None or not stat.S_ISDIR(st.st_mode):
        raise ResolutionError, 'Document root does not exist.'
    directory = []
    subdir = docroot
    parts = [ unquote_url(part) for part in path.split('/') if part ]
    for i in range(len(parts)):
        part = parts[i]
        if part in ('.', '..'):
            raise ResolutionError, \
                    'Current or parent directory not allowed in URI.'
        subdir = os.path.join(subdir, part)
        try:
            st = os.stat(subdir)
        except OSError:
            st = None
        if st is None or not stat.S_ISDIR(st.st_mode):
            filename = parts[i]
            pathinfo = '/'.join(parts[i+1:])
            break
        directory.append(part)
    else:
        filename = ''
        pathinfo = ''
    directory = '/'.join(directory)
    return (directory, filename, pathinfo)

def create_path_uri(directory, filename, pathinfo):
    """Create a path URI from a 3-tuple (directory, filename, pathinfo)."""
    parts = []
    if directory:
        parts.append(directory)
    if filename:
        parts.append(filename)
    if pathinfo:
        parts += [ part for part in pathinfo.split('/') if part ]
    parts = [ quote_url(part) for part in parts ]
    path = '/'.join(parts)
    return path
