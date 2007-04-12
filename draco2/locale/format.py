# vi: ts=8 sts=4 sw=4 et
#
# format.py: locale formatting routines
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


def group_number(number, grouping, thousands_sep):
    """Insert grouping characters (= thousands separators) into a number."""
    result = []
    group = None
    if not grouping or grouping[-1] not in (0, None):
        raise ValueError, 'Grouping must end with `0\' or `None\'.'
    grouping = list(grouping)  # copy
    grouping.reverse()
    if number.startswith('-'):
        sign = '-'
        number = number[1:]
    else:
        sign = ''
    while number:
        try:
            value = grouping.pop()
        except IndexError:
            value = 0
        if value != 0:
            group = value
        if group is None:
            result.append(number)
            number = ''
        else:
            result.append(number[-group:])
            number = number[:-group]
    result.reverse()
    result = sign + thousands_sep.join(result)
    return result


def format_numeric(value, format, localeconv):
    """Format an numerical value."""
    number = format % value
    try:
        integral, fractional = number.split('.')
    except ValueError:
        integral, fractional = number, None
    integral = group_number(integral, localeconv['grouping'],
                            localeconv['thousands_sep'])
    result = integral
    if fractional is not None:
        result += '%s%s' % (localeconv['decimal_point'], fractional)
    return result


def format_monetary(value, format, localeconv, international=False):
    """Format a monetary value."""
    number = format % value
    try:
        integral, fractional = number.split('.')
    except ValueError:
        integral, fractional = number, ''
    if integral.startswith('-'):
        positive = False
        integral = integral[1:]
    else:
        positive = True
    integral = group_number(integral, localeconv['mon_grouping'],
                            localeconv['mon_thousands_sep'])
    if positive:
        sign = localeconv['positive_sign']
        separate = localeconv['p_sep_by_space']
        precede = localeconv['p_cs_precedes']
        position = localeconv['p_sign_posn']
    else:
        sign = localeconv['negative_sign']
        separate = localeconv['n_sep_by_space']
        precede = localeconv['n_cs_precedes']
        position = localeconv['n_sign_posn']
    if international:
        symbol = localeconv['int_curr_symbol']
        fraclen = localeconv['int_frac_digits']
    else:
        symbol = localeconv['currency_symbol']
        fraclen = localeconv['frac_digits']
    if len(fractional) < fraclen:
        fractional += '0' * (fraclen - len(fractional))
    else:
        fractional = fractional[:fraclen]
    if fraclen > 0:
        fractional = '%s%s' % (localeconv['mon_decimal_point'], fractional)
    number = '%s%s' % (integral, fractional)
    if position == 3:
        symbol = '%s%s' % (sign, symbol)
    elif position == 4:
        number = '%s%s' % (sign, number)
    if not precede:
        symbol, number = number, symbol
    if separate:
        symbol += ' '
    result = '%s%s' % (symbol, number)
    if position == 0:
        result = '(%s)' % result
    elif position == 1:
        result = '%s%s' % (sign, result)
    elif position == 2:
        result = '%s%s' % (result, sign)
    return result


def _extended_strftime_format(format, langinfo, obj):
    """Extended strftime() formatting.

    This function returns a new format string that is localised, recognizes
    user-defined date/time formats and some extended format specifiers."""
    replace = []
    try:
        weekday = (obj.weekday() + 1) % 7 + 1
    except AttributeError:
        weekday = 1
    try:
        month = obj.month
    except AttributeError:
        month = 1
    try:
        am = obj.hour < 12
    except AttributeError:
        am = 1
    replace.append(('%x', langinfo['d_fmt']))
    replace.append(('%X', langinfo['t_fmt']))
    replace.append(('%c', langinfo['d_t_fmt']))
    replace.append(('%a', langinfo['abday_%d' % weekday]))
    replace.append(('%A', langinfo['day_%d' % weekday]))
    replace.append(('%b', langinfo['abmon_%d' % month]))
    replace.append(('%B', langinfo['mon_%d' % month]))
    replace.append(('%p', langinfo[am and 'am_str' or 'pm_str']))
    try:
        quarter = (obj.month - 1) // 3 + 1
    except AttributeError:
        quarter = 1
    replace.append(('%q', str(quarter)))
    for i in range(1, 10):
        if langinfo.has_key('d_t_fmt_%d' % i):
            replace.insert(0, ('%%%d' % i, langinfo['d_t_fmt_%d' % i]))
    for s,repl in replace:
        format = format.replace(s, repl)
    return format


def _unicode_strftime(obj, format):
    """Call strftime() on `obj', with unicode support for `format'.

    At least Python 2.4.1 doesn't support strftime() with unicode formats.
    """
    if isinstance(format, unicode):
        format = format.encode('utf-8')
        result = obj.strftime(format)
        result = result.decode('utf-8')
    else:
        result = obj.strftime(format)
    return result


def format_date(date, format, langinfo):
    """Format a date according to `format', using locale
    information from `langinfo'.
    """
    format = _extended_strftime_format(format, langinfo, date)
    return _unicode_strftime(date, format)


def format_time(time, format, langinfo):
    """Format a time according to `format', using locale
    information from `langinfo'.
    """
    format = _extended_strftime_format(format, langinfo, time)
    return _unicode_strftime(time, format)


def format_datetime(datetime, format, langinfo):
    """Format a datedate according to `format', using locale
    information from `langinfo'.
    """
    format = _extended_strftime_format(format, langinfo, datetime)
    return _unicode_strftime(datetime, format)
