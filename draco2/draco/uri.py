# vi: ts=8 sts=4 sw=4 et
#
# uri.py: uri parsing
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

from draco2.util import uri as urimod
from draco2.util.loader import path_from_module
from draco2.session.util import issessionid
from draco2.locale.util import islocale


def uri_from_method(method, extension):
    """Create a relative URI from a method."""
    modname = method.im_class.__module__
    pathname = path_from_module('__docroot__', modname)
    if not pathname or not pathname.endswith('__handler__.py'):
        raise ValueError, 'Expecting Draco handler method.'
    dirname = pathname[:-14].replace(os.sep, '/')
    methodname = method.im_func.func_name
    reluri = '%s%s.%s' % (dirname, methodname, extension)
    return reluri


def parse_draco_uri(uri, docroot):
    """Decompose an URI into Draco specific components.

    The return value is the 8-tuple: (protocol, host, path,
        filename, locale, session, pathinfo, args)
    """
    protocol, host, path, args = urimod.parse_uri(uri)
    directory, filename, pathinfo = urimod.resolve_path_uri(path, docroot) 
    parts = pathinfo.split('/')
    if parts and islocale(parts[0]):
        locale = parts[0]
        parts = parts[1:]
    else:
        locale = ''
    if parts and issessionid(parts[0]):
        session = parts[0]
        parts = parts[1:]
    else:
        session = ''
    pathinfo = '/'.join(parts)
    return (protocol, host, directory, filename, locale, session,
            pathinfo, args)


def create_draco_uri(scheme, host, directory, filename, locale,
                     session, pathinfo, args):
    """Create a Draco URI from its components.

    This function is the inverse of parse_draco_uri()
    """
    parts = []
    if locale:
        parts.append(locale)
    if session:
        parts.append(session)
    if pathinfo:
        parts += [ part for part in pathinfo.split('/') if part ]
    pathinfo = '/'.join(parts)
    path = urimod.create_path_uri(directory, filename, pathinfo)
    uri = urimod.create_uri(scheme, host, path, args)
    return uri


def patch_draco_uri(uri, docroot, scheme=None, host=None, directory=None,
                    filename=None, locale=None, session=None, pathinfo=None,
                    args=None):
    """Patch an URI.

    Components provided as arguments override components from `uri'.
    """
    (curscheme, curhost, curdir, curfile, curloc, curses,
     curinfo, curargs) = parse_draco_uri(uri, docroot)
    if scheme is not None:
        curscheme = scheme
    if host is not None:
        curhost = host
    if directory is not None:
        curdir = directory
    if filename is not None:
        curfile = filename
    if locale is not None:
        curloc = locale
    if session is not None:
        curses = session
    if pathinfo is not None:
        curinfo = pathinfo
    if args is not None:
        curargs = args
    return create_draco_uri(curscheme, curhost, curdir, curfile, curloc,
                            curses, curinfo, curargs)


def paste_draco_uri(uri, docroot, scheme=None, host=None, directory=None,
                    filename=None, locale=None, session=None, pathinfo=None,
                    args=None):
    """Paste into a URI.

    Components provides as arguments augment URI if URI doesn't contain
    that component.
    """
    (curscheme, curhost, curdir, curfile, curloc, curses,
     curinfo, curargs) = parse_draco_uri(uri, docroot)
    if not curscheme:
        curscheme = scheme
    if not curhost:
        curhost = host
    if not curdir:
        curdir = directory
    if not curfile:
        curfile = filename
    if not curloc:
        curloc = locale
    if not curses:
        curses = session
    if not curinfo:
        curinfo = pathinfo
    if not curargs:
        curargs = args
    return create_draco_uri(curscheme, curhost, curdir, curfile, curloc,
                            curses, curinfo, curargs)
