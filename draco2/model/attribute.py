# vi: ts=8 sts=4 sw=4 et
#
# attribute.py: Draco model - attributes
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
import datetime
import decimal

from draco2.model.exception import *


class Attribute(object):
    """An attribute of an object.

    Attribute classes are part of the model definition. Attribute
    instances are part of a runtime model, and hold a value.
    """

    name = None
    type = None
    external_type = None
    nullok = False
    default = None
    width = None
    precision = None
    scale = None
    translate = False
    translate_byname = True
    translation_context = None

    _lazy = False

    def __init__(self, obj):
        """Create a new attribute."""
        self.m_object = obj
        self.m_hasvalue = False
        self.m_value = self.default

    def object(self):
        """Return the parent object (entity or relationship)."""
        return self.m_object

    def isnull(self):
        """Return True if the attribute has no value."""
        return self.m_value is None

    def value(self):
        """Return the value for this attribute.

        If no value has been set, the default value is returned.
        """
        return self.m_value

    def set_value(self, value):
        """Set the attribute to `value'."""
        if value is None:
            if not self.nullok:
                m = 'Attribute %s cannot be NULL.'
                raise ModelIntegrityError, m % self.name
        elif not isinstance(value, self.type):
            try:
                value = self.type(value)
            except (TypeError, ValueError):
                m = 'Illegal value for attribute %s'
                raise ModelIntegrityError, m % self.name
        self.m_value = value

    def del_value(self):
        """Delete the current value for the attribute."""
        self.m_value = self.default

    def _validate(self):
        """Validate the current value."""
        self.validate()

    def validate(self):
        """Validate the current value, implementable by the user."""


class BooleanAttribute(Attribute):
    """A boolean attribute."""
    type = bool
    external_type = 'BOOLEAN'


class IntegerAttribute(Attribute):
    """A signed integer attribute that has at least 32 bits of precision."""
    type = int
    external_type = 'INTEGER'


class DecimalAttribute(Attribute):
    """An arbitrary precision attribute that can store at least 1.000
    decimal digits.
    """
    type = decimal.Decimal
    external_type = 'DECIMAL'
    precision = 28
    scale = 2


class FloatAttribute(Attribute):
    """A double-precision IEEE-754 floating point attribute."""
    type = float
    external_type = 'DOUBLE PRECISION'


class StringAttribute(Attribute):
    """A string attribute with a variable length up to 255 characters."""
    type = unicode
    external_type = 'CHARACTER VARYING'
    width = 255


class TextAttribute(Attribute):
    """A string attribute with no length limit."""
    type = unicode
    external_type = 'TEXT'


class BinaryAttribute(Attribute):
    """A binary large object, with no limit on its length."""
    type = buffer
    external_type = 'BINARY LARGE OBJECT'


class DateAttribute(Attribute):
    """A date attribute."""
    type = datetime.date
    external_type = 'DATE'


class TimeAttribute(Attribute):
    """Attribute holding a time of day."""
    type = datetime.time
    external_type = 'TIME'


class DateTimeAttribute(Attribute):
    """Attribute holding a date and a time."""
    type = datetime.datetime
    external_type = 'TIMESTAMP WITHOUT TIME ZONE'


class IntervalAttribute(Attribute):
    """Attribute holding a time interval."""
    type = datetime.timedelta
    external_type = 'INTERVAL'


class PrimaryKey(IntegerAttribute):
    """The default primary key."""
