# vi: ts=8 sts=4 sw=4 et
#
# build.py: form builder
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 141 $

from draco2.form.visit import FormVisitor


class BuildVisitor(FormVisitor):
    """Form builder.

    This visitor plugs default values into the form.
    """

    def visit_control(self, control):
        if control.label is None:
            control.label = control.name
