# vi: ts=8 sts=4 sw=4 et
#
# translator.py: translator classes
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

from draco2.util.cache import LruCache
from draco2.core.model import (Message, Translation, Change,
                               MessageTranslationRelationship)
from draco2.model import ModelInterfaceError
from draco2.util.singleton import singleton


class TranslatorInterface(object):
    """Translator interface.

    This class defines the interface to translator objects.
    """

    def __init__(self, models, changes=None):
        """Constructor."""

    @classmethod
    def _create(self, api):
        """Factory method."""
        raise NotImplementedError

    def translate(self, message, languages, context=None, name=None):
        """Tranlate a message `message'.

        The `languages' parameter must be a tuple of languages to which
        the message is to be translated. The first language that has a
        translation is used. The `context' parameter specifies the message
        context and `name' specifies a message name.
        """
        raise NotImplementedError


class Translator(TranslatorInterface):
    """The default translator.

    This translator uses the the DracoModel to translate messages. It also
    employs a LRU cache to cut down on the number of database lookups.
    """

    def __init__(self, models, changes=None):
        """Constructor."""
        self.m_models = models
        if changes:
            self._set_change_manager(changes)
        self.m_cache = LruCache(1000)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        if hasattr(api, 'changes'):
            changes = api.changes
        else:
            changes = None
        translator = cls(api.models, changes)
        config = api.config.namespace('draco2.draco.config')
        if config.has_key('cachesize'):
            translator.set_cache_size(config['cachesize'])
        return translator

    def _set_change_manager(self, changes):
        """Use change manager `changes'."""
        ctx = changes.get_context('draco2.draco.translator')
        ctx.add_object('translation', self._mtime)
        ctx.add_callback(self._change_callback)
        ctx = changes.get_context('draco2.draco.config')  # for cache size
        ctx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Change callback."""
        self.clear_cache()
        config = api.config.namespace('draco2.draco.config')
        if config.has_key('cachesize'):
            self.set_cache_size(config['cachesize'])

    def _mtime(self):
        """Return the time stamp at which the last update to the
        translation table was made."""
        transaction = self.m_models.model('draco').transaction('shared')
        try:
            change = transaction.entity(Change, (Translation.name,))
        except ModelInterfaceError:
            return
        return change['change_date']

    def set_cache_size(self, size):
        """Set the cache size to `size'."""
        self.m_cache.set_size(size)

    def clear_cache(self):
        """Clear the translations cache."""
        self.m_cache.clear()

    def translate(self, message, languages, context=None, name=None):
        """Translate `message'."""
        hash = Message.hash(message)
        cacheid = (hash, context, name) + tuple(languages)
        translation = self.m_cache.get(cacheid)
        if translation:
            return translation
        # All translations are looked up where the corresponding message
        # matches `message' or `name', and that match any of the languages
        # specified in `languages'. If no results are found, `message' itself
        # is returned. If results are found, they are ordered by applying the
        # criteria mentioned below and the first entry is returned:
        # 1. Translations where the message name matched.
        # 2. Translations where the message id matched.
        # 3. Translations that have a language earlier in the `languages' list.
        # 4. Translations where the context matched.
        transaction = self.m_models.model('draco').transaction('shared')
        where = '(message.hash = %s'
        args = [hash]
        if name:
            where += ' OR message.name = %s'
            args.append(name)
        where += ')'
        array = ','.join(['%s'] * len(languages))
        where += ' AND language IN (%s)' % array
        args += languages
        # Ordering on columns that can contain NULL values: testing whether a
        # NULL value is equal to something always returns NULL, and therefore
        # we need to weed those out in the ordering test.
        order = []
        if name is not None:
            order.append('message.name = %s AND NOT name IS NULL DESC')
            args.append(name)
        else:
            order.append('message.name IS NULL DESC')
        order.append('message.hash = %s DESC')
        args.append(hash)
        order += ['language=%s DESC'] * len(languages)
        args += languages
        if context:
            order.append('message.context = %s AND NOT context IS NULL DESC')
            args.append(context)
        order = ','.join(order)
        join = (Translation, 'translation',
                MessageTranslationRelationship, 'INNER')
        result = transaction.select(Translation, where, args,
                                    order=order, join=join)
        if result:
            translation = result[0]['translation']
        else:
            translation = message
        self.m_cache.add(cacheid, translation)
        return translation


class DummyTranslator(TranslatorInterface):
    """Dummy translator (doesn't translate)."""

    @classmethod
    def _create(cls, api):
        return cls()

    def translate(self, message, languages, context=None, name=None):
        return message
