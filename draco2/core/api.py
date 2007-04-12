# vi: ts=8 sts=4 sw=4 et
#
# api.py: Draco2 API object
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
import draco2


class API(threading.local):
    """The Draco API.

    The API provides an object respository that provides thread-specific
    access to objects. The repository is accessed using the attribute
    API (i.e. api.attribute).
    """

    @classmethod
    def _create(cls):
        """Factory method."""
        api = cls()
        return api

    def _finalize(self):
        """Finalize the API."""
        self.__dict__.clear()

    def _export(self, namespace):
        """Export all items to `namespace'."""
        namespace.update(self.__dict__)

    def _install(self):
        """Install the API in the "draco2" module."""
        draco2.api = self
