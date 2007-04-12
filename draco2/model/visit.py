# vi: ts=8 sts=4 sw=4 et
#
# visitor.py: visits nodes in a model
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $


class ModelVisitor(object):
    """Visitor class that visits all nodes in a model."""

    def visit(self, model):
        """Visit each node in the model, natural order."""
        self.model = model
        for en in model.entities:
            for at in en.attributes:
                self.visit_attribute(at)
            self.visit_entity(en)
            for ix in en.indexes:
                self.visit_index(ix)
        for re in model.relationships:
            for at in re.attributes:
                self.visit_attribute(at)
            self.visit_relationship(re)
            for ix in re.indexes:
                self.visit_index(ix)
        for vi in model.views:
            self.visit_view(vi)
        self.visit_model(model)

    def visit_reversed(self, model):
        """Visit each node in the model, reversed."""
        self.model = model
        self.visit_model(model)
        for vi in model.views:
            self.visit_view(vi)
        for re in model.relationships:
            for ix in re.indexes:
                self.visit_index(ix)
            self.visit_relationship(re)
            for at in re.attributes:
                self.visit_attribute(at)
        for en in model.entities:
            for ix in en.indexes:
                self.visit_index(ix)
            self.visit_entity(en)
            for at in en.attributes:
                self.visit_attribute(at)

    def visit_attribute(self, attrbute):
        pass

    def visit_index(self, index):
        pass

    def visit_entity(self, entity):
        pass

    def visit_relationship(self, relationship):
        pass

    def visit_view(self, view):
        pass

    def visit_model(self, model):
        pass
