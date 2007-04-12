# vi: ts=8 sts=4 sw=4 et
#
# model.py: the Draco model
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import threading

from draco2.database import DatabaseError
from draco2.model.transaction import Transaction
from draco2.model.schema import Schema


class ModelMetaClass(type):
    """Metaclass that can be used to call Model._build() when
    a model is defined.
    """

    def __init__(self, name, bases, dict):
        type.__init__(self, name, bases, dict)
        # Call for strict subclasses of Model only.
        if object not in bases:
            self._build()


class Model(object):
    """The Draco Model.

    Specific models are created by subclassing this class and providing
    the various class members.
    """

    __metaclass__ = ModelMetaClass

    name = None
    version = None
    entities = []
    relationships = []
    views = []
    transaction_factory = Transaction
    init_statements = []

    def __init__(self, database):
        """Create a new Draco model."""
        self.m_database = database
        self.m_tsd = threading.local()
        self.m_lock = threading.Lock()
        self.m_anonid = 0

    @classmethod
    def _create(cls, api):
        """Factory method."""
        model = cls(api.database)
        return model

    def _finalize(self):
        """Close all open transactions."""
        try:
            transactions = self.m_tsd.transactions.values()
        except AttributeError:
            transactions = []
        for tnx in transactions:
            tnx._finalize()
        self.m_tsd.__dict__.clear()

    @classmethod
    def _build(cls):
        """Build the model. A model has to be built once, before it
        can be instantiated."""
        from draco2.model.check import CheckVisitor
        from draco2.model.build import BuildVisitor
        checker = CheckVisitor()
        checker.visit(cls)
        builder = BuildVisitor()
        builder.visit(cls)

    def database(self):
        """Return the model's database manager."""
        return self.m_database

    def _get_name(self):
        """Return a new anonymous name."""
        self.m_lock.acquire()
        try:
            anonid = self.m_anonid
            self.m_anonid += 1
        finally:
            self.m_lock.release()
        name = 'anon/%d' % anonid
        return name

    def transaction(self, name=None):
        """Create a (named) transaction.

        If name is given and a transaction with the same name already exists,
        that transaction is returned. If no transaction with the specified
        name exists, or if no name is given, a new transaction is returned.
        """
        if name is None:
            name = self._get_name()
        self.m_lock.acquire()
        try:
            try:
                tnx = self.m_tsd.transactions[name]
            except AttributeError:
                self.m_tsd.transactions = {}
            except KeyError:
                pass
            else:
                return tnx
            tnx = self.transaction_factory(self)
            self.m_tsd.transactions[name] = tnx
        finally:
            self.m_lock.release()
        return tnx

    def schema(self):
        """Return a schema object for this model."""
        return Schema(self)

    def object(self, name):
        """Return the entity or relationship `name'."""
        for en in self.entities:
            if en.name == name:
                return en
        for re in self.relationships:
            if re.name == name:
                return re
        raise KeyError, 'No such object: %s' % name
