# vi: ts=8 sts=4 sw=4 et
#
# locale.py: i18n/l10n support
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import draco2
from draco2.locale.exception import LocaleError
from draco2.locale.translator import Translator, DummyTranslator
from draco2.locale.data import LocaleData
from draco2.locale import util, format as locfmt


def tr(message, context=None, name=None):
    """Translate a string `message' using the current locale, if available."""
    try:
        return draco2.api.locale.translate(message, context, name)
    except AttributeError:
        return message

def tr_attr(object, attribute):
    """Translate `attribute' of `object' using a named message."""
    message = object[attribute]
    if not message:
        return ''
    objectid = object._object_id()
    if objectid is not None:
        name = '%s.%s' % (objectid, attribute)
    else:
        name = None
    return tr(message, name=name)

def tr_mark(s):
    """Mark a string for translation and return it unchanged."""
    return s


class Locale(object):
    """The Locale object.

    The Locale object implements Draco's L10N/I18n
    (localisation/internationalisation) subsystem.
    """

    default = 'en-us'

    def __init__(self, data, locale=None, translator=None):
        """Constructor."""
        self.m_locale = None
        self._set_locale_data(data)
        if translator is None:
            translator = DummyTranslator()
        self._set_translator(translator)
        self.set_locale(locale)

    def _set_locale_data(self, data):
        """Set the locale data base to `data'."""
        if not isinstance(data, LocaleData):
            raise TypeError, 'Expecting LocaleData instance.'
        self.m_locale_data = data

    def _set_translator(self, translator):
        """Set the translator."""
        if not isinstance(translator, Translator):
            raise TypeError, 'Expecting Translator instance.'
        self.m_translator = translator

    def set_locale(self, locale=None):
        """Set the locale to `locale'."""
        if not locale:
            locale = self.default
        if locale == self.m_locale:
            return
        if locale not in self.m_locale_data.sections():
            raise LocaleError, 'Unknown locale: %s' % locale
        self.m_locale = locale
        language, territory = util.parse_locale(self.m_locale)
        self.m_language = language
        self.m_territory = territory
        self.m_languages = (self.m_locale, self.m_language)
        self.m_conventions = {}
        self.m_conventions.update(self.m_locale_data.namespace(self.m_territory))
        self.m_conventions.update(self.m_locale_data.namespace(self.m_locale))

    def locale(self):
        """Return the current locale."""
        return self.m_locale

    def language(self):
        """Return the current language, as parsed from the locale."""
        return self.m_language

    def territory(self):
        """Return the current country, as parsed from the locale."""
        return self.m_country

    def languages(self):
        """Return the language search path."""
        return self.m_languages

    def localeconv(self):
        """Return a dictionary with locale conventions."""
        return self.m_conventions

    langinfo = localeconv

    def translate(self, message, context=None, name=None):
        """Translate a string `message'."""
        message = self.m_translator.translate(message, self.languages(),
                                              context, name)
        return message

    def format_date(self, date, format='%x', **kwargs):
        if kwargs:
            conv = self.localeconv().copy()
            conv.update(kwargs)
        else:
            conv = self.localeconv()
        result = locfmt.format_date(date, format, conv)
        return result

    def format_time(self, time, format='%X', **kwargs):
        if kwargs:
            conv = self.localeconv().copy()
            conv.update(kwargs)
        else:
            conv = self.localeconv()
        result = locfmt.format_time(time, format, conv)
        return result

    def format_datetime(self, datetime, format='%c', **kwargs):
        """Format datetime 'dt' according to `format'."""
        if kwargs:
            conv = self.localeconv().copy()
            conv.update(kwargs)
        else:
            conv = self.localeconv()
        result = locfmt.format_datetime(datetime, format, conv)
        return result

    def format_numeric(self, value, format='%s', **kwargs):
        """Format a numeric value."""
        if kwargs:
            conv = self.localeconv().copy()
            conv.update(kwargs)
        else:
            conv = self.localeconv()
        result = locfmt.format_numeric(value, format, conv)
        return result

    def format_monetary(self, value, format='%s', **kwargs):
        """Format a monetary value."""
        if kwargs:
            conv = self.localeconv().copy()
            conv.update(kwargs)
        else:
            conv = self.localeconv()
        result = locfmt.format_monetary(value, format, conv)
        return result
