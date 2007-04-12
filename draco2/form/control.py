# vi: ts=8 sts=4 sw=4 et
#
# control.py: form controls
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
import time
import decimal
import datetime

from draco2.locale.locale import tr
from draco2.util.http import FileUpload
from draco2.form.exception import *


class Control(object):
    """Base class for all form controls."""

    name = None
    label = None

    def __init__(self, form):
        self.m_form = form

    def parse(self, args):
        """Parse `args' to Python format."""
        raise NotImplementedError

    def unparse(self, object):
        """Parse `object' to string format."""
        raise NotImplementedError


class ScalarControl(Control):
    """A form control that reads one single value from a form and outputs
    that single value.
    """

    type = None
    default = None
    nullok = False
    null_value = ''

    def parse(self, args):
        """Parse `args' to Python format."""
        value = args.get(self.name, '')
        if not isinstance(value, basestring):
            m = tr('Expecting scalar value for field: %s') % tr(self.label)
            fields = [self.name]
            raise FormError(m, fields)
        if self.nullok and value == self.null_value:
            value = None
        elif not value:
            if self.default is None:
                m = tr('A value is required for field: %s') % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
            value = self.default
        if value is not None and self.type is not None:
            try:
                value = self.type(value)
            except ValueError:
                m = tr('Illegal value for field: %s') % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
        result = {}
        result[self.name] = value
        return result

    def unparse(self, object):
        """Parse `object' to string format."""
        value = object[self.name]
        if value is None:
            if self.nullok:
                value = self.null_value
            else:
                # Be lenient when unparsing null values. A null value here
                # means an incomplete db record, which this form is possibly
                # trying to address.
                value = ''
        else:
            value = str(value)
        result = {}
        result[self.name] = value
        return result


class BooleanControl(ScalarControl):
    """Boolean control.

    This control accepts various ways of specifying booleans as its
    input, such as true/false, yes/no and on/off.
    """

    def parse(self, args):
        """Parse `args' to Python format."""
        data = super(BooleanControl, self).parse(args)
        value = data[self.name]
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        elif value is None:
            value = None
        else:
            m = tr('Illegal value for field: %s') % tr(self.label)
            fields = [self.name]
            raise FormError(m, fields)
        data[self.name] = value
        return data

    def unparse(self, object):
        value = object[self.name]
        if value is None:
            if self.nullok:
                value = self.null_value
            else:
                value = ''
        else:
            value = str(value).lower()
        result = {}
        result[self.name] = value
        return result


class NumericControl(ScalarControl):
    """Numeric control.

    This control is the base class for all numeric controls.
    """

    minval = None
    maxval = None

    def parse(self, args):
        """Parse `args' to Python format."""
        result = super(NumericControl, self).parse(args)
        value = result[self.name]
        if value is not None:
            if self.minval is not None and value < self.minval:
                m = tr('Value of field %s is too low (minimum value is %s).') \
                            % (tr(self.label), self.minval)
                fields = [self.name]
                raise FormError(m, fields)
            elif self.maxval is not None and value > self.maxval:
                m = tr('Value of field %s is too high (maximum value is %s).') \
                            % (tr(self.label), self.minval)
                fields = [self.name]
                raise FormError(m, fields)
        return result


class IntegerControl(NumericControl):
    """Integer control.

    This control accepts a regular integer as its input.
    """

    type = int


class DecimalControl(NumericControl):
    """Decimal control.

    This control accepts an arbitrary precision decimal number
    as its input.
    """

    type = decimal.Decimal


class FloatControl(NumericControl):
    """Floatint pont control.

    This control accepts a floating point number as its input.
    """

    type = float


class CharacterControl(ScalarControl):
    """Base class for text controls."""

    minlen = None
    maxlen = None
    strip = None
    regex = None

    def parse(self, args):
        """Parse `args' to Python format."""
        data = super(CharacterControl, self).parse(args)
        value = data[self.name]
        if value is not None:
            if self.strip is not None:
                value = self.strip.sub('', value)
                data[self.name] = value
            if self.minlen is not None and len(value) < self.minlen:
                m = tr('Input for field %s is too short (minimum length is %d).') \
                            % (tr(self.label), self.minlen)
                fields = [self.name]
                raise FormError(m, fields)
            if self.maxlen is not None and len(value) > self.maxlen:
                m = tr('Input for field %s is too long (maximum length is %d).') \
                            % (tr(self.label), self.maxlen)
                fields = [self.name]
                raise FormError(m, fields)
            if self.regex is not None and not self.regex.match(value):
                m = tr('The input for field %s does not match the required ' \
                       'format.') % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
        return data

    def unparse(self, object):
        """Parse `object' to string format."""
        value = object[self.name]
        if value is None:
            if self.nullok:
                value = self.null_value
            else:
                value = ''
        else:
            value = unicode(value)
        result = {}
        result[self.name] = value
        return result


class StringControl(CharacterControl):
    """A control that accepts a single-line of text."""

    re_eol = re.compile('[\r\n]')

    def parse(self, args):
        """Parse `args'."""
        data = super(StringControl, self).parse(args)
        value = data.get(self.name)
        if value is not None:
            value = value.strip()
            if self.re_eol.search(value):
                m = tr('Illegal value for field %s (no end-of-lines allowed).') \
                        % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
            data[self.name] = value
        return data


class TextControl(CharacterControl):
    """A control that accepts an arbitrary amount of text."""


class EnumControl(StringControl):
    """Enumerated control.

    This is a string control that only accepts values form a limited
    set of possibilities.
    """

    values = []

    def parse(self, args):
        """Parse `args' to Python format."""
        data = super(EnumControl, self).parse(args)
        value = data[self.name]
        if value is not None and value not in self.values:
            m = tr('Illegal value for field: %s.') % tr(self.label)
            fields = [self.name]
            raise FormError(m, fields)
        return data


class DateTimeBaseControl(ScalarControl):
    """Date base control.

    This is a base class for all date, time and datetime controls.
    """

    formats = None
    date_type = None
    tm_slice = None

    def parse(self, args):
        """Parse `args' to Python format."""
        data = super(DateTimeBaseControl, self).parse(args)
        value = data[self.name]
        if value is not None:
            for fmt in self.formats:
                try:
                    tm = time.strptime(value, fmt)
                    break
                except ValueError:
                    pass
            else:
                m = tr('Illegal format for field: %s') % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
            value = self.date_type(*tuple(tm)[self.tm_slice])
        data[self.name] = value
        return data

    def unparse(self, object):
        """Parse `object' to string format."""
        result = {}
        value = object[self.name]
        if value is None:
            if self.nullok:
                value = self.null_value
            else:
                value = ''
        else:
            value = value.strftime(self.formats[0])
        result = {}
        result[self.name] = value
        return result


class DateControl(DateTimeBaseControl):
    """Date control.

    This control accepts a date as its input.
    """

    formats = ('%Y-%m-%d', '%y-%m-%d')
    date_type = datetime.date
    tm_slice = slice(0, 3)


class TimeControl(DateTimeBaseControl):
    """Time control.

    This control accepts a time as its input.
    """

    formats = ('%H:%M:%S',)
    date_type = datetime.time
    tm_slice = slice(3, 6)


class DateTimeControl(DateTimeBaseControl):
    """Date/Time control.

    This control accepts a date/time as its input.
    """

    formats = ('%Y-%m-%d %H:%M:%S',)
    date_type = datetime.datetime
    tm_slice = slice(0, 6)


class IntervalControl(IntegerControl):
    """Date/Time interval.

    This control accepts a number of days as its input.
    """

    def parse(self, args):
        """Parse `args' to Python format."""
        data = super(IntegerControl, self).parse(args)
        value = data[self.name]
        if value is not None:
            value = datetime.timedelta(value)
            data[self.name] = value
        return data

    def unparse(self, object):
        """Parse `object' to string format."""
        result = super(IntegerControl, self).unparse(object)
        value = result[self.name]
        if value:
            value = value[:value.find(' ')]
            result[self.name] = value
        return result


class ArrayControl(Control):
    """Array control.

    This control accepts one or multiple values for a single
    variable name. The variables are passed as-is and not parsed
    further.
    """

    def parse(self, args):
        value = args.get(self.name)
        if not value:
            value = []
        elif not isinstance(value, list):
            value = [value]
        result = {}
        result[self.name] = value
        return result

    def unparse(self, object):
        value = object[self.name]
        result = {}
        result[self.name] = value
        return result


class FileUploadControl(Control):
    """File upload control.

    This control accepts a FileUpload object as its input.
    """

    nullok = False

    def parse(self, args):
        value = args.get(self.name)
        if value:
            if not isinstance(value, FileUpload):
                m = tr('Expecting file upload for field: %s') % tr(self.label)
                fields = [self.name]
                raise FormError(m, fields)
        elif self.nullok:
            value = None
        else:
            m = tr('No file selected for field: %s') % tr(self.label)
            fields = [self.name]
            raise FormError(m, fields)
        result = {}
        result[self.name] = value
        return result

    def unparse(self, args):
        # no postback possible for file upload fields
        return {}
