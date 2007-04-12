# vi: ts=8 sts=4 sw=4 et
#
# form.py: base class for Draco forms
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class FormMetaClass(type):
    """Metaclass for forms.

    This metaclass calls .build() on form when their class is
    defined.
    """

    def __init__(self, name, bases, dict):
        type.__init__(self, name, bases, dict)
        # Do not call for Form itself, only subclasses.
        if object not in bases:
            self.build()


class Form(object):
    """Form Object.

    A form consists of controls. Each control maps a set of values
    between the web domain and the database domain. Values in the web
    domain are strings, values in the database domain are values
    understood by the DBAPI.
    """

    __metaclass__ = FormMetaClass

    inputs = []
    outputs = []

    def __init__(self):
        """Constructor."""
        self.m_inputs = []
        for cls in self.inputs:
            obj = cls(self)
            self.m_inputs.append(obj)
        self.m_outputs = []
        for cls in self.outputs:
            obj = cls(self)
            self.m_outputs.append(obj)

    @classmethod
    def build(cls):
        """Build the form. This performs a few checks on the form
        definition and plugs in some default values."""
        from draco2.form.check import CheckVisitor
        from draco2.form.build import BuildVisitor
        checker = CheckVisitor()
        checker.visit(cls)
        builder = BuildVisitor()
        builder.visit(cls)

    def parse(self, args):
        """Parse form arguments.

        The `args' parameter must be a mapping of strings to lists of
        strings and FileUpload classes.
        """
        result = {}
        for co in self.m_inputs:
            result.update(co.parse(args))
        return result

    def unparse(self, object, keep_empty_values=True):
        """Unparse form arguments.

        The `object' parameter must be a mapping of string names
        to DB-API types.
        """
        result = {}
        for co in self.m_outputs:
            result.update(co.unparse(object))
        if not keep_empty_values:
            keys = [ key for key in result if result[key] == '' ]
            for key in keys:
                del result[key]
        return result
