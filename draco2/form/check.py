# vi: ts=8 sts=4 sw=4 et
#
# check.py: form checking
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

from draco2.form.exception import *
from draco2.form.control import Control, ScalarControl
from draco2.form.visit import FormVisitor


class CheckVisitor(FormVisitor):
    """Form checker.

    This visitor checks all nodes in a form.
    """

    def visit_control(self, control):
        if not issubclass(control, Control):
            m = 'Not a Control instance: %s' % control
            raise FormDefinitionError, m
        if control.name is None:
            m = 'Property "name" not set for control %s' % control
            raise FormDefinitionError, m
        if not isinstance(control.name, basestring):
            m = 'Property "name" not string in control %s.' % control
            raise FormDefinitionError, m
        if control.label is not None and not \
                    isinstance(control.label, basestring):
            m = 'Property "label" not a string in control %s' % control
            raise FormDefinitionError, m
        if isinstance(control, ScalarControl) and control.type is not None \
                    and not isinstance(control.type, type):
            m = 'Property "type" not a type in control %s.' % control
            raise FormDefinitionError, m
        if isinstance(control, ScalarControl) and control.default is not None \
                    and not isinstance(control.default, basestring):
            m = 'Property "default" not a string in control %s.' % control
            raise FormDefinitionError, m

    def visit_form(self, form):
        names = set()
        for co in form.inputs:
            if co.name in names:
                m = 'Duplicate input control name %s in form %s.' % (co.name, form)
                raise FormDefinitionError, m
            names.add(co.name)
        names = set()
        for co in form.outputs:
            if co.name in names:
                m = 'Duplicate output control name %s in form %s.' % (co.name, form)
                raise FormDefinitionError, m
            names.add(co.name)
