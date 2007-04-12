# vi: ts=8 sts=4 sw=4 et
#
# visit.py: form visitor
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class FormVisitor(object):
    """Form Visitor."""

    def visit(self, form):
        """Visit all nodes in a form."""
        for co in form.inputs:
            self.visit_control(co)
        for co in form.outputs:
            self.visit_control(co)
        self.visit_form(form)

    def visit_control(self, control):
        pass

    def visit_form(self, form):
        pass
