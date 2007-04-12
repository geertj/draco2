# vi: ts=8 sts=4 sw=4 et
#
# exception.py: core exception classes
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class DracoException(Exception):
    """Base class for all Draco exceptions."""


class DracoError(DracoException):
    """Base class for all Draco errors."""


class DracoSiteError(DracoError):
    """An error has occurred for which the Draco site
    owner is responsible."""

    def __init__(self, message, filename=None, lineno=None, backtrace=None):
        self.message = message
        self.filename = filename
        self.lineno = lineno
        self.backtrace = backtrace

    def __str__(self):
        return self.message


class DracoInternalError(DracoError):
    """An internal draco error has occurred."""


class DracoInterfaceError(DracoError):
    """The Draco interface is being used wrongly."""


class HTTPResponse(DracoException):
    """Base class for all exceptions that are used to
    stop request processing.
    """

    def __init__(self, status, headers={}, body=''):
        self.status = status
        self.headers = headers
        self.body = body


class FilterError(DracoSiteError):
    """A filter error has occurred."""
