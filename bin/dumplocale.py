#!/usr/bin/env python

import sys
import os.path
import locale

variables = \
(
    'decimal_point', 'grouping', 'thousands_sep', 'currency_symbol',
    'int_curr_symbol', 'mon_decimal_point', 'mon_grouping',
    'mon_thousands_sep', 'positive_sign', 'negative_sign',
    'frac_digits', 'int_frac_digits', 'p_sign_posn', 'n_sign_posn',
    'p_cs_precedes', 'n_cs_precedes', 'p_sep_by_space',
    'n_sep_by_space', 'd_t_fmt', 'd_fmt', 't_fmt', 't_fmt_ampm',
    'day_1', 'day_2', 'day_3', 'day_4', 'day_5', 'day_6', 'day_7',
    'abday_1', 'abday_2', 'abday_3', 'abday_4', 'abday_5', 'abday_6',
    'abday_7', 'mon_1', 'mon_2', 'mon_3', 'mon_4', 'mon_5', 'mon_6',
    'mon_7', 'mon_8', 'mon_9', 'mon_10', 'mon_11', 'mon_12', 'abmon_1',
    'abmon_2', 'abmon_3', 'abmon_4', 'abmon_5', 'abmon_6', 'abmon_7',
    'abmon_8', 'abmon_9', 'abmon_10', 'abmon_11', 'abmon_12', 'am_str',
    'pm_str'
)


def unicode_hack(raw):
    return eval('u' + repr(raw))

def usage():
    prog = os.path.basename(sys.argv[0])
    sys.stderr.write('Usage: %s locale\n' % prog)

if len(sys.argv) != 2:
    usage()
    sys.exit(1)
locname = sys.argv[1]

try:
    locale.setlocale(locale.LC_ALL, locname)
except locale.Error:
    sys.stderr.write('Error: unsupported local: %s\n' % locname)
    sys.exit(1)

locname = locname.lower().replace('_', '-')
print '[%s]' % locname

localeconv = locale.localeconv()
for key in variables:
    if localeconv.has_key(key):
        data = localeconv[key]
    elif hasattr(locale, key.upper()):
        data = locale.nl_langinfo(getattr(locale, key.upper()))
    if isinstance(data, str):
        data = unicode_hack(data)
    print '%s = %s' % (key, repr(data))
