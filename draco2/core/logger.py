# vi: ts=8 sts=4 sw=4 et
#
# logger.py: logging
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
import logging


def init_logger(options):
    """Set up the Draco logger."""
    logfile = os.path.join(options['documentroot'], options['logfile'])
    logger = logging.getLogger('draco2')
    handler = logging.FileHandler(logfile)
    format = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if options.get('debug'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
