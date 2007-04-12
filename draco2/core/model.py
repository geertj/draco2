# vi: ts=8 sts=4 sw=4 et
#
# draco.py: the draco model
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import datetime
import sha
import random

from draco2.util.misc import md5sum
from draco2.model import Model, Entity, Relationship, Index, View
from draco2.model.transaction import Transaction
from draco2.model.attribute import (StringAttribute, IntegerAttribute,
                                    DateTimeAttribute, BinaryAttribute,
                                    TextAttribute)
from draco2.model.exception import ModelIntegrityError


# CHANGE TRACKING ...

class ChangeTrackingEntity(Entity):
    """An entity that tracks changes."""

    def _mark_updated(self):
        if self._state() == self.FREE:
            return
        transaction = self.transaction()
        result = transaction.select(Change, 'name=%s', (self.name,))
        if result:
            assert len(result) == 1
            result[0]['change_date'] = datetime.datetime.now()
        else:
            change = Change()
            change['name'] = self.name
            change['change_date'] = datetime.datetime.now()
            transaction.insert(change)

    def post_insert(self):
        self._mark_updated()

    def post_update(self, attr):
        self._mark_updated()

    def post_delete(self):
        self._mark_updated()


# CONFIG ...

class ConfigKey(StringAttribute):
    name = 'key'
    width = 64

class ConfigValue(StringAttribute):
    name = 'value'
    width = 128

class Config(ChangeTrackingEntity):
    name = 'config'
    attributes = [ConfigKey, ConfigValue]
    primary_key = [ConfigKey]


# LOCALE ...

class LocaleName(StringAttribute):
    name = 'locale'
    width = 64

class Locale(Entity):
    name = 'locale'
    attributes = [LocaleName]
    primary_key = [LocaleName]

class LocaleKey(StringAttribute):
    name = 'key'
    width = 64

class LocaleValue(StringAttribute):
    name = 'value'
    width = 128

class LocaleData(ChangeTrackingEntity):
    name = 'locale_data'
    attributes = [LocaleName, LocaleKey, LocaleValue]
    primary_key = [LocaleName, LocaleKey]


# ROBOTS ...

class RobotSignature(StringAttribute):
    name = 'signature'
    width = 128

class Robot(ChangeTrackingEntity):
    name = 'robot'
    attributes = [RobotSignature]
    primary_key = [RobotSignature]


# PRINCIPAL ...

class PrincipalID(IntegerAttribute):
    name = 'id'

class PrincipalName(StringAttribute):
    name = 'name'
    width = 64

class PrincipalPassword(StringAttribute):
    name = 'password'
    width = 64
    nullok = True

class PrincipalCertificate(StringAttribute):
    name = 'certificate_dn'
    width = 128
    nullok = True

class PrincipalResetToken(StringAttribute):
    name = 'reset_token'
    width = 32
    nullok = True

class PrincipalNameIndex(Index):
    name = 'principal_name_index'
    unique = True
    attributes = [PrincipalName]

class PrincipalCertificateIndex(Index):
    name = 'certificate_dn_index'
    unique = True
    attributes = [PrincipalCertificate]

class Principal(Entity):
    name = 'principal'
    attributes = [PrincipalID, PrincipalName, PrincipalPassword,
                  PrincipalCertificate, PrincipalResetToken]
    primary_key = [PrincipalID]
    indexes = [PrincipalNameIndex, PrincipalCertificateIndex]

    def set_password(self, password):
        """Set the password for this principal."""
        generator = random.SystemRandom()
        salt = '%08x' % generator.getrandbits(32)
        digest = sha.new()
        digest.update(salt)
        digest.update(':')
        digest.update(password.encode('utf-8'))
        verifier = digest.hexdigest()
        password = '%s:%s' % (salt, verifier)
        self['password'] = password

    def verify_password(self, password):
        """Verify a password for a pincipal."""
        ref = self['password']
        if not ref:
            return False
        p0 = ref.find(':')
        if p0 == -1:
            return False
        salt, verifier = ref[:p0], ref[p0+1:]
        digest = sha.new()
        digest.update(salt)
        digest.update(':')
        digest.update(password)
        return digest.hexdigest() == verifier
    
    def enable_password_reset(self):
        """Enable a password reset for this principal. Return a token."""
        generator = random.SystemRandom()
        token = '%032x' % generator.getrandbits(128)
        self['reset_token'] = token
        return token


# ROLE ...

class RoleName(StringAttribute):
    name = 'name'
    width = 64

class Role(Entity):
    name = 'role'
    attributes = [RoleName]
    primary_key = [RoleName]

class PrincipalRoleRelationship(Relationship):
    name = 'principal_role_relationship'
    roles = [('principal', Principal, (0, None)),
             ('role', Role, (0, None))]


# SECURITY CONTEXT ...

class Token(StringAttribute):
    name = 'token'
    width = 32

class SecurityContextPrincipal(PrincipalName):
    name = 'principal'

class CreateDate(DateTimeAttribute):
    name = 'create_date'

class LastUsed(DateTimeAttribute):
    name = 'last_used'

class ExpireDate(DateTimeAttribute):
    name = 'expire_date'

class SecurityContext(Entity):
    name = 'security_context'
    attributes = [Token, SecurityContextPrincipal,
                  CreateDate, LastUsed, ExpireDate]
    primary_key = [Token]


# SESSION ...

class SessionID(StringAttribute):
    name = 'id'
    width = 32

class LastSubsession(IntegerAttribute):
    name = 'last_subsession'
 
class SessionPrincipal(PrincipalName):
    name = 'principal'
    nullok = True

class Session(Entity):
    name = 'session'
    attributes = [SessionID, LastSubsession, SessionPrincipal,
                  CreateDate, LastUsed, ExpireDate]
    primary_key = [SessionID]


# SESSION NAMESPACE ...

class Scope(StringAttribute):
    name = 'scope'
    width = 64

class Data(BinaryAttribute):
    name = 'data'
    nullok = True

class SessionNamespace(Entity):
    name = 'session_namespace'
    attributes = [SessionID, Scope, Data]
    primary_key = [SessionID, Scope]

class SessionNamespaceRelationship(Relationship):
    name = 'session_data_relationship'
    roles = [('session', Session, (1, 1)),
             ('namespace', SessionNamespace, (0, None))]


# LANGUAGE ...

class LanguageID(IntegerAttribute):
    name = 'id'

class LanguageString(StringAttribute):
    name = 'language'
    width = 32

class LanguageNameIndex(Index):
    name = 'language_name_index'
    attributes = [LanguageString]

class Language(Entity):
    name = 'language'
    attributes = [LanguageID, LanguageString]
    primary_key = [LanguageID]
    indexes = [LanguageNameIndex]

    def pre_insert(self):
        """Trigger called prior to insertion in db."""
        # Enforce uniqueness of language.
        transaction = self.transaction()
        result = transaction.select(Language, 'language = %s',
                                    (self['language'],))
        if len(result) > 0:
            m = 'A language with the same name already exists'
            raise ModelIntegrityError, m

    # XXX: a validate_update or post_update is required as well


# MESSAGE ...

class MessageID(IntegerAttribute):
    name = 'id'

# A hash of a (possibly) large message is stored to speed up searching, and to
# see when translations of name-based messages are out of date.

class MessageHash(StringAttribute):
    name = 'hash'
    width = 32

class MessageContext(StringAttribute):
    name = 'context'
    width = 64
    nullok = True

class MessageName(StringAttribute):
    name = 'name'
    width = 64
    nullok = True

class MessageString(TextAttribute):
    name = 'message'

class MessageHashIndex(Index):
    name = 'message_hash_index'
    attributes = [MessageHash]

class MessageNameIndex(Index):
    name = 'message_name_index'
    attributes = [MessageName]

class Message(Entity):
    name = 'message'
    attributes = [MessageID, MessageHash, MessageContext, MessageName,
                  MessageString]
    primary_key = [MessageID]
    indexes = [MessageHashIndex, MessageNameIndex]

    @classmethod
    def hash(self, message):
        """Return a unique message id for `message'."""
        # MD5 works on bytes, not on unicode
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        return md5sum(message)

    def translation(self, language):
        """Return the translation in `language', or None if that does not
        exist."""
        transaction = self.transaction()
        join = (Translation, 'translation', MessageTranslationRelationship,
                'INNER')
        result = transaction.select(Translation,
                                    'message.id = %s AND language = %s',
                                    (self['id'], language), join=join)
        if result:
            return result[0]

    def pre_insert(self):
        """Validate a record before it is inserted."""
        # If a name is given, (name, context) needs to be unique. If no name is
        # given, the tuple (hash, context) needs to be unique with name being
        # NULL. In both cases uniqueness means that NULL values are considered
        # equal to themselves, i.e. NULL = NULL. This is not the normal
        # equality sense in SQL (where NULL means "unknown").
        transaction = self.transaction()
        if self['name'] is not None:
            query = 'name = %s'
            args = [self['name']]
        else:
            query = 'hash = %s and name IS NULL'
            args = [self['hash']]
        if self['context'] is not None:
            query += ' AND context = %s'
            args.append(self['context'])
        else:
            query += ' AND context IS NULL'
        result = transaction.select(Message, query, tuple(args))
        if len(result) > 0:
            m = 'Message already exists in the database.'
            raise ModelIntegrityError, m

    def post_update(self, attr):
        """Trigger that is executed after an attribute update."""
        super(Message, self).post_update(attr)
        # Automatically keep the message hash up to date.
        if attr.name == 'message':
            value = attr.value()
            # MD5 works only on bytes, not on unicode
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            self['hash'] = md5sum(value)

    # XXX: we'd need a validate_update() as well...


# TRANSLATION ...

class TranslationID(IntegerAttribute):
    name = 'id'

# We keep a reference to the checksum of their original message. For named
# messages, this allows us to detect whether a translation is still up to date.

class TranslationOrigHash(StringAttribute):
    name = 'orig_hash'
    width = 32

class TranslationString(TextAttribute):
    name = 'translation'

class Translation(ChangeTrackingEntity):
    name = 'translation'
    attributes = [TranslationID, TranslationOrigHash, TranslationString]
    primary_key = [TranslationID]

    @classmethod
    def hash(self, message):
        """Return a unique message id for `message'."""
        # MD5 works on bytes, not on unicode
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        return md5sum(message)


class MessageTranslationRelationship(Relationship):
    name = 'message_translation_relationship'
    roles = [('message', Message, (1, 1)),
             ('translation', Translation, (0, None))]
    attributes = [LanguageString]

    def verify_insert(self):
        """Verify insertion (commit time)"""
        # Each message can have at most one translation for a given language
        transaction = self.transaction()
        join = (Translation, 'translation', MessageTranslationRelationship,
                'INNER')
        result = transaction.select(Translation,
                                    'message.id = %s AND language = %s',
                                    (self['message_id'], self['language']),
                                    join=join)
        if len(result) > 1:
            m = 'A translation in the same language already exists.'
            raise ModelIntegritError, m

    verify_update = verify_insert


class MessageTranslationView(View):
    """A view that for each message displays its translation in all possible
    languages."""

    name = 'message_translation_view'
    query = """
            SELECT message.id AS id,
                   message.hash AS hash,
                   message.context AS context,
                   message.name AS name,
                   message.message AS message,
                   language.language AS language,
                   translation.translation AS translation,
                   translation.orig_hash AS orig_hash
            FROM draco.message
                CROSS JOIN draco.language
                LEFT OUTER JOIN draco.message_translation_relationship ON
                    draco.message_translation_relationship.message_id =
                        draco.message.id AND
                    draco.language.language =
                        draco.message_translation_relationship.language
                LEFT OUTER JOIN draco.translation ON
                    draco.translation.id =
                        draco.message_translation_relationship.translation_id
            """


# CHANGE ...

class ChangeName(StringAttribute):
    name = 'name'
    width = 32

class ChangeDate(DateTimeAttribute):
    name = 'change_date'

class Change(Entity):
    name = 'change'
    attributes = [ChangeName, ChangeDate]
    primary_key = [ChangeName]


# SCHEMA ...

class SchemaName(StringAttribute):
    name = 'name'
    width = 32

class Version(IntegerAttribute):
    name = 'version'

class Schema(Entity):
    name = 'schema'
    attributes = [SchemaName, Version]
    primary_key = [SchemaName]


# TRANSACTION ...

class DracoTransaction(Transaction):

    def expire_sessions(self):
        """Expire sessions."""
        now = datetime.datetime.now()
        sessions = self.select(Session, 'expire_date < %s', (now,))
        for session in sessions:
            namespaces = self.select(SessionNamespace, 'id = %s',
                                     (session['id'],))
            for ns in namespaces:
                self.delete(ns)
            self.delete(session)
        return len(sessions)

    def update_messages(self, messages):
        """Update the `message' table with new messages that require
        translation.
        
        This function returns the number of new messages that were inserted.
        """
        count = 0
        for message,context,name in messages:
            hash = Message.hash(message)
            if name is None:
                # x = NULL does not work with SQL's tri-valued logic where NULL
                # means "unknown". Therefore don't select on context if it is
                # None.
                if context is None:
                    result = self.select(Message, 'hash=%s', (hash,))
                else:
                    result = self.select(Message, 'hash=%s AND context=%s',
                                         (hash, context))
                if not result:
                    message = Message(context=context, message=message)
                    self.insert(message)
                    count += 1
            else:
                # Update instead of replace named messages. This leaves
                # translations intact.
                result = self.select(Message, 'name = %s', (name,))
                if result:
                    msg = result[0]
                    if msg['message'] != message:
                        msg['message'] = message
                        count += 1
                else:
                    message = Message(name=name, message=message)
                    self.insert(message)
                    count += 1
        return count


# MODEL ...

class DracoModel(Model):
    name = 'draco'
    version = 3
    entities = [Config, Locale, LocaleData, Robot, Principal, Role,
                SecurityContext, Session, SessionNamespace, Language,
                Message, Translation, Change, Schema]
    relationships = [PrincipalRoleRelationship, SessionNamespaceRelationship,
                     MessageTranslationRelationship]
    views = [MessageTranslationView]
    transaction_factory = DracoTransaction
