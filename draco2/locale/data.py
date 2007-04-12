# vi: ts=8 sts=4 sw=4 et
#
# data.py: locale data
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os.path
from draco2.core.config import Config


class LocaleData(Config):
    """Local conventions database."""

    @classmethod
    def _create(cls, api):
        """Factory method."""
        locdata = cls()
        datadir = api.config.ns()['datadirectory']
        locdata.add_file(os.path.join(datadir, 'locale.ini'))
        docroot = api.request.docroot()
        locdata.add_file(os.path.join(docroot, 'locale.ini'))
        return locdata
