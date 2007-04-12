# vi: ts=8 sts=4 sw=4 et
#
# test_format.py: unit tests for draco2.util.locale
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import py.test
import datetime

from draco2.locale import format


class TestFormatNumeric(object):

    conv_basic = {
        'grouping': [3, 0],
        'thousands_sep': ',',
        'decimal_point': '.'
    }

    data_basic = (
        (123, '%s', '123'),
        (-123, '%s', '-123'),
        (123456, '%s', '123,456'),
        (-123456, '%s', '-123,456'),
        (1234567, '%s', '1,234,567'),
        (-1234567, '%s', '-1,234,567'),
        (123456789123456789, '%s', '123,456,789,123,456,789'),
        (-123456789123456789, '%s', '-123,456,789,123,456,789'),
        (123.456, '%.3f', '123.456'),
        (-123.456, '%.3f', '-123.456'),
        (1234.567, '%.3f', '1,234.567'),
        (-1234.567, '%.3f', '-1,234.567'),
        (123456789123.456, '%.3f', '123,456,789,123.456'),
        (-123456789123.456, '%.3f', '-123,456,789,123.456'),
    )

    def test_basic(self):
        for number,fmt,string in self.data_basic:
            assert format.format_numeric(number, fmt,
                                         self.conv_basic) == string

    conv_grouping = {
        'grouping': [3, 3, None],
        'thousands_sep': ',',
        'decimal_point': '.'
    }

    data_grouping = (
        (1234567, '%s', '1,234,567'),
        (-1234567, '%s', '-1,234,567'),
        (123456789123456789, '%s', '123456789123,456,789'),
        (-123456789123456789, '%s', '-123456789123,456,789')
    )

    def test_grouping(self):
        for number,fmt,string in self.data_grouping:
            assert format.format_numeric(number, fmt,
                                         self.conv_grouping) == string

    conv_illegal = {
        'grouping': [3, 3],
        'thousands_sep': ',',
        'decimal_point': '.'
    }

    data_illegal = (
        (123, '%s', '123'),
    )

    def test_illegal(self):
        for number,fmt,string in self.data_illegal:
            py.test.raises(ValueError, format.format_numeric,
                           number, fmt, self.conv_illegal)


class TestFormatMonetary(object):

    data = {
        'italy': (
            {
                'mon_grouping': [3, 0],
                'mon_thousands_sep': '.',
                'mon_decimal_point': '',
                'positive_sign': '',
                'negative_sign': '-',
                'p_sep_by_space': 0,
                'p_cs_precedes': 1,
                'p_sign_posn': 1,
                'n_sep_by_space': 0,
                'n_cs_precedes': 1,
                'n_sign_posn': 1,
                'currency_symbol': 'L.',
                'frac_digits': 0,
                'int_curr_symbol': 'ITL.',
                'int_frac_digits': 0
            },
            (1230, 'L.1.230', '-L.1.230', 'ITL.1.230')),
          'netherlands': (
            {
                'mon_grouping': [3, 0],
                'mon_thousands_sep': '.',
                'mon_decimal_point': ',',
                'positive_sign': '',
                'negative_sign': '-',
                'p_sep_by_space': 1,
                'p_cs_precedes': 1,
                'p_sign_posn': 1,
                'n_sep_by_space': 1,
                'n_cs_precedes': 1,
                'n_sign_posn': 4,
                'currency_symbol': 'F',
                'frac_digits': 2,
                'int_curr_symbol': 'NLG',
                'int_frac_digits': 2
            },
            (1234.56, 'F 1.234,56', 'F -1.234,56', 'NLG 1.234,56')),
        'norway': (
            {
                'mon_grouping': [3, 0],
                'mon_thousands_sep': '.',
                'mon_decimal_point': ',',
                'positive_sign': '',
                'negative_sign': '-',
                'p_sep_by_space': 0,
                'p_cs_precedes': 1,
                'p_sign_posn': 1,
                'n_sep_by_space': 0,
                'n_cs_precedes': 1,
                'n_sign_posn': 2,
                'currency_symbol': 'kr',
                'frac_digits': 2,
                'int_curr_symbol': 'NOK ',
                'int_frac_digits': 2
            },
            (1234.56, 'kr1.234,56', 'kr1.234,56-', 'NOK 1.234,56')),
        'switzerland': (
            {
                'mon_grouping': [3, 0],
                'mon_thousands_sep': ',',
                'mon_decimal_point': '.',
                'positive_sign': '',
                'negative_sign': 'C',
                'p_sep_by_space': 0,
                'p_cs_precedes': 1,
                'p_sign_posn': 1,
                'n_sep_by_space': 0,
                'n_cs_precedes': 1,
                'n_sign_posn': 2,
                'currency_symbol': 'SFrs.',
                'frac_digits': 2,
                'int_curr_symbol': 'CHF ',
                'int_frac_digits': 2
            },
            (1234.56, 'SFrs.1,234.56', 'SFrs.1,234.56C', 'CHF 1,234.56'))
    }

    def test_basic(self):
        for country, tuple in self.data.items():
            conv, data = tuple
            number, pos, neg, intl = data
            fmt = '%s'
            assert format.format_monetary(number, fmt, conv) == pos
            assert format.format_monetary(-number, fmt, conv) == neg
            assert format.format_monetary(number, fmt, conv,
                                          international=True) == intl


class TestFormatDate(object):

    # Dutch langinfo
    langinfo = \
    {
        'abday_1': 'zo',
        'abday_2': 'ma',
        'abday_3': 'di',
        'abday_4': 'wo',
        'abday_5': 'do',
        'abday_6': 'vr',
        'abday_7': 'za',
        'day_1': 'zondag',
        'day_2': 'maandag',
        'day_3': 'dinsdag',
        'day_4': 'woensdag',
        'day_5': 'donderdag',
        'day_6': 'vrijdag',
        'day_7': 'zaterdag',
        'abmon_1': 'jan',
        'abmon_2': 'feb',
        'abmon_3': 'mrt',
        'abmon_4': 'apr',
        'abmon_5': 'mei',
        'abmon_6': 'jun',
        'abmon_7': 'jul',
        'abmon_8': 'aug',
        'abmon_9': 'sep',
        'abmon_10': 'okt',
        'abmon_11': 'nov',
        'abmon_12': 'dec',
        'mon_1': 'januari',
        'mon_2': 'februari',
        'mon_3': 'maart',
        'mon_4': 'april',
        'mon_5': 'mei',
        'mon_6': 'juni',
        'mon_7': 'juli',
        'mon_8': 'augustus',
        'mon_9': 'september',
        'mon_10': 'oktober',
        'mon_11': 'november',
        'mon_12': 'december',
        'am_str': 'am',
        'pm_str': 'pm',
        'd_fmt': '%d-%m-%y',
        't_fmt': '%H:%M:%S',
        'd_t_fmt': '%a %d %b %Y %H:%M:%S %Z'
    }

    data = (
        (datetime.date(2005, 10, 8), '%x', '08-10-05'),
        (datetime.time(17, 0, 1), '%X', '17:00:01'),
        (datetime.datetime(2005, 10, 8, 17, 0, 1), '%c', 'za 08 okt 2005 17:00:01 ')
    )

    def test_basic(self):
        for object,fmt,result in self.data:
            if isinstance(object, datetime.date):
                assert format.format_date(object, fmt,
                                          self.langinfo) == result
            elif isinstance(object, datetime.time):
                assert format.format_time(object, fmt,
                                          self.langinfo) == result
            elif isinstance(object, datetime.datetime):
                assert format.format_datetime(object, fmt,
                                              self.langinfo) == result

    def test_extended(self):
        fmt = lambda x: format.format_datetime(x, '%q', self.langinfo)
        dt = datetime.datetime(2005, 1, 1)
        assert fmt(dt) == '1'
        dt = datetime.datetime(2005, 3, 1)
        assert fmt(dt) == '1'
        dt = datetime.datetime(2005, 4, 1)
        assert fmt(dt) == '2'

    def test_custom(self):
        self.langinfo['d_t_fmt_1'] = 'Q%q %Y'
        fmt = lambda x: format.format_datetime(x, '%1', self.langinfo)
        dt = datetime.datetime(2005, 1, 1)
        assert fmt(dt) == 'Q1 2005'
        dt = datetime.datetime(2005, 3, 1)
        assert fmt(dt) == 'Q1 2005'
        dt = datetime.datetime(2005, 4, 1)
        assert fmt(dt) == 'Q2 2005'
