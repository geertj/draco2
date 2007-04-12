# vi: ts=8 sts=4 sw=4 et
#
# message.py: message commands
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import os.path
import stat
import fnmatch

from draco2.draco.opener import DracoOpener
from draco2.draco.parser import Parser, DracoParser, ParseError
from draco2.draco.rewriter import DracoRewriter, RewriteError
from draco2.draco.taglib import TranslationTagLibrary
from draco2.core.model import (Language, Message, Translation,
                               MessageTranslationRelationship)
from draco2.locale.translator import Translator
from draco2.locale.util import extract_messages, islocale
from draco2.command.command import Command
from draco2.model.exception import ModelError


class AddLanguage(Command):
    """Add a language."""

    name = 'add'
    description = 'add a language'
    usage = '%prog %command <language>'
    nargs = 1

    def run(self, opts, args, api):
        language = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        language = Language(language=language)
        try:
            transaction.insert(language)
            transaction.commit()
        except ModelError, err:
            self.error(err)
            self.exit(1)


class RemoveLanguage(Command):
    """Remove a language."""

    name = 'remove'
    description = 'remove a language'
    usage = '%prog %command <language>'
    nargs = 1

    def run(self, opts, args, api):
        language = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Language, 'language=%s', (language,))
        if result:
            transaction.delete(result[0])
            transaction.commit()
        else:
            self.error('language does not exist: %s' % language)
            self.exit(1)


class ListLanguages(Command):
    """List all languages installed in the catalog."""

    name = 'list'
    description = 'list all languages'

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Language)
        for lang in result:
            self.write('-> %s\n' % lang['language'])


class ClearLanguages(Command):
    """Remove all languages from the catalog."""

    name = 'clear'
    description = 'remove all languages from the catalog'

    def add_options(self, group):
        group.add_option('-f', '--force', action='store_true',
                         dest='force', help='do not ask for confirmation')

    def run(self, opts, args, api):
        warning = 'this will delete all languages in the catalog'
        if not opts.force and not self.verify(warning):
            return
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Language)
        for lang in result:
            transaction.delete(lang)
        transaction.commit()


class LanguageCommand(Command):
    """Language meta command."""

    name = 'language'
    description = 'manage languages'

    def __init__(self):
        super(LanguageCommand, self).__init__()
        self.add_subcommand(AddLanguage())
        self.add_subcommand(RemoveLanguage())
        self.add_subcommand(ListLanguages())
        self.add_subcommand(ClearLanguages())


class AddMessage(Command):
    """Add a message to the catalog."""

    name = 'add'
    description = 'add a message'
    usage = '%prog %command <message>'
    nargs = 1

    def add_options(self, group):
        group.add_option('-x', '--context', dest='context',
                         help='the message context')
        group.add_option('-n', '--name', dest='name',
                         help='the message name')

    def run(self, opts, args, api):
        message = args[0]
        name = opts.name or None
        context = opts.context or None
        model = api.models.model('draco')
        transaction = model.transaction()
        hash = Message.hash(message)
        message = Message(hash=hash, context=context, name=name,
                          message=message)
        try:
            transaction.insert(message)
            transaction.commit()
        except ModelError, err:
            self.error(err)
            self.exit(1)


class RemoveMessage(Command):
    """Remove a message."""

    name = 'remove'
    description = 'remove a message from the catalog'
    usage = '%prog %command <message>'
    nargs = 1

    def add_options(self, group):
        group.add_option('-x', '--context', dest='context',
                         help='the message context')
        group.add_option('-n', '--name', dest='name',
                         help='the message name')

    def run(self, opts, args, api):
        message = args[0]
        context = opts.context or None
        name = opts.name or None
        model = api.models.model('draco')
        transaction = model.transaction()
        hash = Message.hash(message)
        query = 'hash = %s'
        args = [hash]
        if context is not None:
            query += ' AND context = %s'
            args.append(context)
        else:
            query += ' AND context IS NULL'
        if name is not None:
            query += ' AND name = %s'
            args.append(name)
        else:
            query += ' AND name IS NULL'
        result = transaction.select(Message, query, args)
        if result:
            transaction.delete(result[0])
            transaction.commit()
        else:
            self.error('message does not exist')
            self.exit(1)


class ClearMessages(Command):
    """Clear messages table."""

    name = 'clear'
    description = 'remove all messages from the catalog'

    def add_options(self, group):
        group.add_option('-f', '--force', action='store_true',
                         dest='force', help='do not ask for confirmation')

    def run(self, opts, args, api):
        warning = 'this will delete all messages'
        if not opts.force and not self.verify(warning):
            return
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Message)
        for msg in result:
            transaction.delete(msg)
        transaction.commit()


class ListMessages(Command):
    """List all messages in the catalog."""

    name = 'list'
    description = 'list all messages in the catalog'

    def run(self, opts, args, api):
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Message)
        for msg in result:
            self.write('-> ')
            self.write(msg['message'].encode('utf-8'))
            data = []
            if msg['context']:
                data.append('context = %s' % msg['context'])
            if msg['name']:
                data.append('name = %s' % msg['name'])
            if data:
                self.write(' (%s)' % ', '.join(data))
            self.write('\n')


class ExtractMessagesDocroot(Command):
    """Extract messages to be translated."""

    name = 'extract_docroot'
    description = 'extract messages for translation'
    usage = '%prog %command [glob]...'

    def _visit_template(self, fname, api):
        """Visit a template `fname'."""
        # Message type #1: XHTML tags
        relname = fname[len(api.docroot):]
        curdir = os.path.dirname(fname)
        api.opener._set_current_directory(curdir)
        try:
            buffer = api.parser.parse(relname, opener=api.opener,
                                      mode=Parser.COLLECT_TEXT)
        except ParseError, err:
            self.error('%s: %s' % (relname, str(err)))
            return []
        rewriter = DracoRewriter()
        taglib = TranslationTagLibrary(TranslationTagLibrary.COLLECT_MESSAGES)
        rewriter.add_tag_library(taglib)
        try:
            dummy = rewriter.filter(buffer)
        except RewriteError, err:
            self.error('%s: %s' % (relname, str(err)))
            return []
        messages = taglib.messages()
        # Message type #2: tr() function inside code
        try:
            buffer = api.parser.parse(relname, opener=api.opener,
                                      mode=Parser.COLLECT_CODE)
        except ParseError, err:
            self.error('%s: %s' % (relname, str(err)))
            return []
        messages += extract_messages(buffer)
        return messages

    def _visit_python(self, fname, api):
        """Visit a Python source."""
        fin = file(fname)
        buffer = fin.read()
        fin.close()
        messages = extract_messages(buffer)
        return messages

    def _visit(self, fname, api):
        """Visit a file."""
        basename, ext = os.path.splitext(fname)
        extension = '.' + api.options['extension']
        if ext == '.py':
            messages = self._visit_python(fname, api)
        elif ext == extension:
            base2, ext2 = os.path.splitext(basename)
            if islocale(ext2):
                return []
            messages = self._visit_template(fname, api)
        else:
            return []
        relname = fname[len(api.docroot):]
        if api.opts.verbose:
            self.write('%s:\n' % relname)
            self._show_messages(messages)
        return messages

    def _show_messages(self, messages):
        """Show messages (verbose output)."""
        for message,context,name in messages:
            self.write('  -> ')
            self.write(message.encode('utf8'))
            data = []
            if context:
                data.append('context = %s' % context)
            if name:
                data.append('name = %s' % name)
            if data:
                self.write(' (%s)' % ', '.join(data))
            self.write('\n')

    def _walk_tree(self, directory, globs, visit, api):
        """Walk a directory tree, calling `visit' on every file
        encountered.
        """
        try:
            contents = os.listdir(directory)
        except OSError:
            return  # happens on Windows sometimes
        result = []
        for entry in contents:
            if entry in ('.svn',):
                continue
            entry = os.path.join(directory, entry)
            try:
                st = os.stat(entry)
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode):
                if globs is not None:
                    relname = entry[len(api.docroot):]
                    for glob in globs:
                        if fnmatch.fnmatch(relname, glob):
                            break
                    else:
                        continue
                result += visit(entry, api)
            elif stat.S_ISDIR(st.st_mode):
                result += self._walk_tree(entry, globs, visit, api)
        return result

    def _extract_messages(self, globs, api):
        """Extract messages from templates and Python sources."""
        api.docroot = api.options['documentroot']
        api.opener = DracoOpener()
        api.opener._set_document_root(api.docroot)
        api.parser = DracoParser()
        messages = self._walk_tree(api.docroot, globs, self._visit, api)
        if api.opts.verbose:
            self.write('Extracted %d messages.\n' % len(messages))
        return messages

    def _unique_messages(self, messages):
        """Unique messages."""
        unique = set()
        for msg in messages:
            unique.add(msg)
        self.write('Total unique messages: %s\n' % len(unique))
        return list(unique)

    def _update_messages(self, messages, api):
        """Store messages in the catalog."""
        model = api.models.model('draco')
        transaction = model.transaction()
        count = transaction.update_messages(messages)
        transaction.commit()
        self.write('Inserted %d new messages.\n' % count)

    def add_options(self, group):
        group.add_option('-v', '--verbose', action='store_true',
                         dest='verbose', help='verbose output')
        group.add_option('-n', '--no-store', action='store_true',
                         dest='showonly',
                         help='show messages only, don\'t store')

    def set_defaults(self, parser):
        parser.set_default('verbose', False)

    def run(self, opts, args, api):
        """Extract messages."""
        if len(args) > 0:
            globs = args
        else:
            globs = None
        api.opts = opts
        api.args = args
        messages = self._extract_messages(globs, api)
        messages = self._unique_messages(messages)
        if api.opts.showonly:
            self.write('Not storing messages.\n')
        else:
            self._update_messages(messages, api)


class ExtractMessagesModel(Command):
    """Extract messages for translation from a model."""

    name = 'extract_model'
    description = 'extract messages for translation from a model'
    usage = '%prog %command <model>'
    nargs = 1

    def _show_messages(self, messages):
        """Show messages (verbose output)."""
        for message,context,name in messages:
            self.write('  -> ')
            self.write(message.encode('utf-8'))
            data = []
            if context:
                data.append('context = %s' % context)
            if name:
                data.append('name = %s' % name)
            if data:
                self.write(' (%s)' % ', '.join(data))
            self.write('\n')

    def _get_messages_from_object(self, object, attribute, model, api):
        """Create messages from `attribute' of `object' in `model'.

        This function queries the model for all instances of the object and
        returns a list of values of the specified attribute. In this context,
        an object is either an Entity or a Relationship class.
        """
        messages = []
        attname = attribute.name
        transaction = model.transaction()
        where = '%s != \'\' AND NOT %s IS NULL' % (attname, attname)
        result = transaction.select(object, where=where)
        for res in result:
            message = res[attname]
            if attribute.translate_byname:
                name = '%s.%s' % (res._object_id(), attname)
            else:
                name = None
            context = attribute.translation_context
            messages.append((message, context, name))
        if api.opts.verbose:
            self.write('%s:\n' % object.name)
            self._show_messages(messages)
        return messages

    def _extract_messages_from_model(self, model, api):
        """Extract messages from the model `model'.
        
        This function scans all objects (entities and relationship) in the
        database. For each object, the attributes are scanned, and those marked
        for translation are extracted.
        """
        messages = []
        model = api.models.model(model)
        for obj in model.entities + model.relationships:
            for att in obj.attributes:
                if not att.translate:
                    continue
                messages += self._get_messages_from_object(obj, att, model,
                                                           api)
        return messages

    def _remove_duplicates(self, messages):
        """Unique messages."""
        unique = set()
        for msg in messages:
            unique.add(msg)
        self.write('Total unique messages: %s\n' % len(unique))
        return list(unique)

    def _update_messages(self, messages, api):
        """Update messages in the catalog."""
        model = api.models.model('draco')
        transaction = model.transaction()
        count = transaction.update_messages(messages)
        transaction.commit()
        self.write('Inserted %d new messages.\n' % count)

    def add_options(self, group):
        group.add_option('-v', '--verbose', action='store_true',
                         dest='verbose', help='verbose output')
        group.add_option('-n', '--no-store', action='store_true',
                         dest='showonly',
                         help='show messages only, don\'t store')

    def set_defaults(self, parser):
        parser.set_default('verbose', False)

    def run(self, opts, args, api):
        """Extract messages."""
        api.args = args
        api.opts = opts
        model = args[0]
        messages = self._extract_messages_from_model(model, api)
        messages = self._remove_duplicates(messages)
        if api.opts.showonly:
            self.write('Not storing messages.\n')
        else:
            self._update_messages(messages, api)


class MessageCommand(Command):
    """Message meta command."""

    name = 'message'
    description = 'manage messages'

    def __init__(self):
        super(MessageCommand, self).__init__()
        self.add_subcommand(AddMessage())
        self.add_subcommand(RemoveMessage())
        self.add_subcommand(ClearMessages())
        self.add_subcommand(ListMessages())
        self.add_subcommand(ExtractMessagesDocroot())
        self.add_subcommand(ExtractMessagesModel())


class AddTranslation(Command):
    """Add a translation to the catalog."""

    name = 'add'
    description = 'add a translation to the catalog'
    usage = '%prog %command <message> <language> <translation>'
    nargs = 3

    def add_options(self, group):
        group.add_option('-x', '--context', dest='context',
                         help='the message context')
        group.add_option('-n', '--name', dest='name',
                         help='the group name')

    def run(self, opts, args, api):
        message, language, translation = args
        context = opts.context
        name = opts.name
        model = api.models.model('draco')
        transaction = model.transaction()
        result = transaction.select(Language, 'language=%s', (language,))
        if not result:
            self.error('language does not exist: %s' % language)
            self.exit(1)
        hash = Message.hash(message)
        query = 'hash = %s'
        args = [hash]
        if context is not None:
            query += ' AND context = %s'
            args.append(context)
        else:
            query += ' AND context IS NULL'
        if name is not None:
            query += ' AND name = %s'
            args.append(name)
        else:
            query += ' AND name IS NULL'
        result = transaction.select(Message, query, tuple(args))
        if not result:
            self.error('message does not exist')
            self.exit(1)
        else:
            message = result[0]
        trobj = message.translation(language)
        if trobj:
            trobj['translation'] = translation
        else:
            trobj = Translation(translation=translation, orig_hash=hash)
            transaction.insert(trobj)
            relationship = MessageTranslationRelationship()
            relationship.set_role('message', message)
            relationship.set_role('translation', trobj)
            relationship['language'] = language
            transaction.insert(relationship)
        transaction.commit()


class RemoveTranslation(Command):
    """Remove a translation from the catalog."""

    name = 'remove'
    description = 'remove a translation from the catalog'
    usage = '%prog %command <message> <language>'
    nargs = 2

    def add_options(self, group):
        group.add_option('-x', '--context', dest='context',
                         help='the message context')
        group.add_option('-n', '--name', dest='name',
                         help='the message name')

    def run(self, opts, args, api):
        message, language = args
        context = opts.context
        name = opts.name
        hash = Message.hash(message)
        query = 'message.hash = %s'
        args = [hash]
        if context is not None:
            query += ' AND message.context = %s'
            args.append(context)
        else:
            query += ' AND message.context IS NULL'
        if name is not None:
            query += ' AND message.name = %s'
            args.append(name)
        else:
            query += ' AND message.name IS NULL'
        query += ' AND language = %s'
        args.append(language)
        model = api.models.model('draco')
        transaction = model.transaction()
        join = (Translation, 'translation',
                MessageTranslationRelationship, 'INNER')
        result = transaction.select(Translation, query, args, join=join)
        if result:
            transaction.delete(result[0])
            transaction.commit()
        else:
            self.error('translation does not exist')
            self.exit(1)


class ListTranslations(Command):
    """List all message translations."""

    name = 'list'
    description = 'list all translations'
    usage = '%prog %command <language>'
    nargs = 1

    def run(self, opts, args, api):
        language = args[0]
        model = api.models.model('draco')
        transaction = model.transaction()
        join = (Translation, 'translation',
                MessageTranslationRelationship, 'INNER')
        result = transaction.select(Translation, 'language=%s',
                                    (language,), join=join)
        for trans in result:
            self.write('-> ')
            self.write(trans['translation'])
            data = []
            if trans['context']:
                data.append('context = %s' % trans['context'])
            if trans['name']:
                data.append('name = %s' % trans['name'])
            if data:
                self.write(' (%s)' % ', '.join(data))
            self.write('\n')


class ClearTranslations(Command):
    """Remove all message translations."""

    name = 'clear'
    description = 'remove all translations'
    usage = '%prog %command <language>'
    nargs = 1

    def add_options(self, group):
        group.add_option('-f', '--force', action='store_true',
                         dest='force', help='do not ask for confirmation')

    def run(self, opts, args, api):
        language = args[0]
        warning = 'this will delete all translations in the catalog'
        if not values.force and not self.verify(warning):
            return
        model = api.models.model('draco')
        transaction = model.transaction()
        join = (Translation, 'translation',
                MessageTranslationRelationship, 'INNER')
        result = transaction.select(Translation, 'language=%s',
                                    (language,), join=join)
        for trans in result:
            transaction.delete(trans)
        transaction.commit()


class TranslationCommand(Command):
    """Translation meta command."""

    name = 'translation'
    description = 'manage translations'

    def __init__(self):
        super(TranslationCommand, self).__init__()
        self.add_subcommand(AddTranslation())
        self.add_subcommand(RemoveTranslation())
        self.add_subcommand(ListTranslations())
        self.add_subcommand(ClearTranslations())


class TranslateCommand(Command):
    """Translate a message."""

    name = 'translate'
    description = 'translate a message'
    usage = '%prog %command <message> <language>...'
    nargs = (2, None)

    def add_options(self, group):
        group.add_option('-x', '--context', dest='context',
                         help='the message context')
        group.add_option('-n', '--name', dest='name',
                         help='the message name')

    def set_defaults(self, parser):
        parser.set_default('context', '')

    def run(self, opts, args, api):
        message = args[0]
        languages = args[1:]
        context = opts.context
        name = opts.name
        translator = Translator._create(api)
        translated = translator.translate(message, languages,
                                          context=context, name=name)
        self.write('%s\n' % translated)
