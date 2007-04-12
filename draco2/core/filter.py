# vi: ts=8 sts=4 sw=4 et
#
# filer: output filters
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class Filter(object):
    """Base class for all filters.

    A filter is a text transform that is applied to a response just
    before sending it to the client.
    """

    # The default priority for this filter. By convention this
    # should be 0 <= priority <= 100, with 0 the highest priority.
    priority = 50

    def filter(self, buffer):
        """Filter the response in `buffer'."""
        raise NotImplementedError
