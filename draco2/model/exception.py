# vi: ts=8 sts=4 sw=4 et
#
# exception.py: draco2.model exceptoins
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2 import DracoError


class ModelError(DracoError):
    """Base class of all Draco Model related errors. """


class ModelDefinitionError(ModelError):
    """Raised when an error in a model is detected."""


class ModelInterfaceError(ModelError):
    """Raised when the model interface is not used appropriately."""


class ModelIntegrityError(ModelError):
    """Raised when a model validation fails."""


class ModelInternalError(ModelError):
    """Raised when a serious internal error has been detected, such as
    a model/database inconsistency."""
