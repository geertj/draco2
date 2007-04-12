# vi: ts=8 sts=4 sw=4 et
#
# taglib.py: form tag library
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import draco2
from draco2.draco.taglib import TagLibrary, element


class FormTagLibrary(TagLibrary):
    """Form Tag library.

    This tag library write back values from a namespace into their
    respective form tags.
    """

    namespaces = { 'xhtml': 'http://www.w3.org/1999/xhtml' }

    def __init__(self, namespace, form=None):
        """Constructor."""
        super(FormTagLibrary, self).__init__()
        self.m_namespace = namespace
        self.m_form = form

    def _check_form(self, node):
        """Check if this node is part of the current form."""
        if not self.m_form:
            return True
        forms = node.xpath('ancestor::xhtml:form[@id="%s"]' % self.m_form,
                           namespaces=self.namespaces)
        return bool(forms)

    @element('//xhtml:input')
    def input(self, node):
        """Paste in value from the namespace."""
        if not self._check_form(node):
            return
        try:
            name = node.attrib['name']
            type = node.attrib['type']
        except KeyError:
            return
        curval = node.attrib.get('value')
        newval = self.m_namespace.get(name)
        if type in ('text', 'hidden', 'password'):
            if isinstance(newval, basestring):
                node.attrib['value'] = newval
        if type in ('checkbox', 'radio'):
            if not isinstance(newval, list):
                newval = [newval]
            if curval in newval:
                node.attrib['checked'] = 'checked'
            elif node.attrib.get('selected'):
                del node.attrib['selected']

    @element('//xhtml:option')
    def option(self, node):
        """Select the right option."""
        if not self._check_form(node):
            return
        try:
            select = node.xpath('ancestor::xhtml:select',
                                draco2.api.rewriter.namespaces())
            select = select[0].attrib['name']
        except (IndexError, KeyError):
            return
        curval = node.attrib.get('value')
        newval = self.m_namespace.get(select)
        if not isinstance(newval, list):
            newval = [newval]
        if curval in newval:
            node.attrib['selected'] = 'selected'
        elif node.attrib.get('selected'):
            del node.attrib['selected']

    @element('//xhtml:textarea')
    def textarea(self, node):
        """Append text after <textarea>."""
        if not self._check_form(node):
            return
        try:
            name = node.attrib['name']
        except KeyError:
            return
        newval = self.m_namespace.get(name)
        if isinstance(newval, basestring):
            if node.text is None:
                node.text = newval
            else:
                node.text += newval
