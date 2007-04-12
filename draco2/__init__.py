# vi: ts=8 sts=4 sw=4 et
#
# __init__.py: draco main package
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import sys
assert sys.version_info >= (2, 4, 0), 'Python >= 2.4 is required.'

# Import core exceptions.
from draco2.core.exception import *

# Translation functions
from draco2.locale.locale import tr, tr_attr, tr_mark

# Provide null API
api = None
