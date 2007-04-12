# vi: ts=8 sts=4 sw=4 et
#
# exception.py: draco.form exceptions
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.core.exception import DracoError


class FormError(DracoError):
    """Base class of all form errors."""

    def __init__(self, message, error_fields=[]):
        self.message = message
        self.error_fields = error_fields

    def dict(self):
        d = { 'message': self.message, 'error_fields': self.error_fields }
        return d

    def __str__(self):
        return self.message


class FormDefinitionError(FormError):
    """Raised when an error in a form is detected."""
