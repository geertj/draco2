# vi: ts=8 sts=4 sw=4 et
#
# support.py: test support for draco2.model
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
from draco2.model.test.shopmodel import ShopModel
from draco2.database.test.support import DatabaseTest


class ModelTest(DatabaseTest):
    """Base class for model tests."""

    def setup_method(cls, method):
        super(ModelTest, cls).setup_method(method)
        cls.model = ShopModel(cls.database)
        cls.schema = cls.model.schema()
        cls.schema.drop()
        cls.schema.create()

    def teardown_method(cls, method):
        cls.model._finalize()
        cls.schema.drop()
        super(ModelTest, cls).teardown_method(method)
