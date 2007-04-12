# vi: ts=8 sts=4 sw=4 et
#
# rewrite.py: draco rewriter
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import lxml.etree

import draco2
from draco2.core.exception import FilterError
from draco2.core.filter import Filter
from draco2.draco.taglib import TagLibrary
from draco2.draco.taglib import DracoTagLibrary, TranslationTagLibrary


class RewriteError(FilterError):
    """Rewriter error."""


class Rewriter(Filter):
    """Abstract base class for rewriters."""

    def __init__(self):
        """Constructor."""
        super(Rewriter, self).__init__()
        self.m_tag_libraries = []

    @classmethod
    def _create(cls, api):
        """Factory method."""
        rewriter = cls()
        return rewriter

    def add_tag_library(self, taglib, priority=None):
        """Add tag library `taglib' to the rewriter."""
        if not isinstance(taglib, TagLibrary):
            m = 'Expecting "TagLibrary" instance (got %s).'
            raise TypeError, m % type(taglib)
        if priority is None:
            priority = taglib.priority
        self.m_tag_libraries.append((priority, taglib))
        self.m_tag_libraries.sort()

    def tag_libraries(self):
        """Return a list of tag libraries."""
        libraries = [ tl[1] for tl in self.m_tag_libraries ]
        return libraries


class DracoRewriter(Rewriter):
    """The default Draco rewrite filter."""

    def __init__(self):
        """Constructor."""
        super(DracoRewriter, self).__init__()
        self.m_namespaces = {}

    @classmethod
    def _create(cls, api):
        """Factory method."""
        rewriter = super(DracoRewriter, cls)._create(api)
        taglib = DracoTagLibrary._create(api)
        rewriter.add_tag_library(taglib)
        taglib = TranslationTagLibrary._create(api)
        rewriter.add_tag_library(taglib)
        taglibs = api.loader.load_classes('__taglib__.py', TagLibrary,
                                          scope='__docroot__')
        for taglib in taglibs:
            obj = taglib._create(api)
            rewriter.add_tag_library(obj)
        return rewriter

    def add_tag_library(self, taglib, priority=None):
        """Add tag library `taglib' to the rewriter."""
        super(DracoRewriter, self).add_tag_library(taglib, priority)
        self.m_namespaces.update(taglib.namespaces)

    def namespaces(self):
        """Return a directionary of namespace prefixes."""
        return self.m_namespaces

    def _filter_tree(self, tree):
        """Filter an XML tree `tree'."""
        for taglib in self.tag_libraries():
            for xpath,handler in taglib._elements():
                try:
                    nodes = tree.xpath(xpath, namespaces=self.m_namespaces)
                except lxml.etree.Error, err:
                    raise RewriteError, str(err)
                for node in nodes:
                    handler(node)
        return tree

    def filter(self, buffer):
        try:
            tree = lxml.etree.XML(buffer).getroottree()
        except lxml.etree.Error, err:
            raise RewriteError, str(err)
        self._filter_tree(tree)
        output = tree.docinfo.doctype
        output += lxml.etree.tostring(tree, xml_declaration=False)
        return output
