# vi: ts=8 sts=4 sw=4 et
#
# locale.py: draco specific locale
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.locale.locale import Locale
from draco2.locale.data import LocaleData
from draco2.locale.translator import Translator
from draco2.util.singleton import singleton


class DracoLocale(Locale):
    """Draco Locale.

    This is a specific Locale class for the draco handler. It uses
    DracoRequest.locale() to set the current locale.
    """

    @classmethod
    def _create(cls, api):
        data = singleton(LocaleData, api, factory=LocaleData._create)
        translator = singleton(Translator, api, factory=Translator._create)
        locale = api.request.locale()
        if not locale:
            ns_cfg = api.config.ns('draco2.draco.locale')
            locale = ns_cfg.get('default')
        locale = cls(data, locale, translator)
        return locale
