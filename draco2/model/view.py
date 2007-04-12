# vi: ts=8 sts=4 sw=4 et
#
# view.py: views
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.model.exception import *
from draco2.model.attribute import Attribute
from draco2.model.object import Object


class View(Object):
    """Database View.

    A view object is a read-only representation of selected data.
    Each view has an associated VIEW object in the database.
    """

    query = None
    attributes = []
    primary_key = []

    def __init__(self):
        super(View, self).__init__()

    def _select(self, row, description, lock=False):
        if self._state() != self.ASSOCIATED:
            raise ModelInterfaceError, 'No transaction associated.'
        names = [ de[0] for de in description ]
        for name,value in zip(names, row):
            # Create an anonymous attribute using the `type'
            # metaclass.
            dict = {}
            dict['name'] = name
            dict['type'] = type(value)
            dict['nullok'] = True
            cls = type('AnonymousAttribute', (Attribute,), dict)
            attr = cls(self)
            self.m_attributes[name] = attr
        super(View, self)._select(row, description)

    def _insert(self):
        raise ModelInterfaceError, 'Cannot insert into view.'

    def _delete(self):
        raise ModelInterfaceError, 'Cannot delete from view.'

    def __setitem__(self, key, value):
        raise ModelInterfaceError, 'Cannot set attribute on view.'

    def __delitem__(self, key):
        raise ModelInterfaceError, 'Cannot delete attribute on view.'
