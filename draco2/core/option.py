# vi: ts=8 sts=4 sw=4 et
#
# option.py: options
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
from draco2.core.exception import *

# These updated by setup.py:

install_options = \
{
    'revision': '1',
    'bindirectory': '/fugue/web/shs/bin',
    'datadirectory': '/fugue/web/shs/share/draco'
}


def init_options(options):
    """Check options, normalize, and fill in defaults."""
    if not options.has_key('documentroot'):
        raise DracoSiteError, 'Required option `documentroot\' not set.'
    options = options.copy()
    options.update(install_options)
    if os.environ.has_key('DRACO_BINDIRECTORY'):
        options['bindirectory'] = os.environ['DRACO_BINDIRECTORY']
    if os.environ.has_key('DRACO_DATADIRECTORY'):
        options['datadirectory'] = os.environ['DRACO_DATADIRECTORY']
    options['documentroot'] = os.path.normpath(options['documentroot'])
    if not options.has_key('configfile'):
        options['configfile'] = 'draco2.ini'
    if not options.has_key('logfile'):
        options['logfile'] = 'draco2.log'
    if not options.has_key('extension'):
        options['extension'] = 'dsp'
    if not options.has_key('debug'):
        options['debug'] = False
    if not options.has_key('profile'):
        options['profile'] = False
    if not options.has_key('errorhandler'):
        options['errorhandler'] = None
    return options
