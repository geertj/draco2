# vi: ts=8 sts=4 sw=4 et
#
# taglib.py: webui tag library
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
from draco2.draco.taglib import element, TagLibrary


class WebUITagLibrary(TagLibrary):
    """Tag library for the Draco web-ui."""

    # High priority because we generate XHTML that need to be processed
    # further.
    priority = 10

    namespaces = { 'xhtml': 'http://www.w3.org/1999/xhtml',
                   'webui': 'http://www.digitalfugue.com/NS/webui' }

    def __init__(self):
        super(WebUITagLibrary, self).__init__()
        self._set_support_path('support')
 
    def _create(self, api):
        """Factory method."""
        taglib = super(WebUITagLibrary, self)._create(api)
        section = api.config.ns('draco2.core')
        path = section.get('supportpath')
        if path:
            self._set_content_path(path)

    def _set_support_path(self, path):
        """Set the path where the Draco support files can be found."""
        self.m_support_path = path

    def _parse_template(self, template, **kwargs):
        """Parse a template and return a XML fragment."""
        template = '/%s/webui/%s' % (self.m_support_path, template)
        frag = super(WebUITagLibrary, self)._parse_template(template, **kwargs)
        return frag

    @element('//xhtml:head')
    def head(self, node):
        frag = self._parse_template('head_start.inc', node=node)
        node[0:0] = frag[:]

    @element('//xhtml:body')
    def body(self, node):
        node.attrib['onload'] = 'webui_body_onload();'

    @element('//webui:context')
    def context(self, node):
        node.tag = '{%s}form' % self.namespaces['xhtml']
        #node.attrib.clear()
        node.attrib['class'] = 'webui'
        node.attrib['method'] = 'post'
        node.attrib['enctype'] = 'multipart/form-data'
        frag = self._parse_template('context_start.inc', node=node)
        node[0:0] = frag[:]

    @element('//webui:form')
    def form(self, node):
        frag = self._parse_template('form.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:listview')
    def listview(self, node):
        frag = self._parse_template('listview.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:buttonlist')
    def buttonlist(self, node):
        frag = self._parse_template('buttonlist.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:tasklist')
    def tasklist(self, node):
        frag = self._parse_template('tasklist.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:message')
    def message(self, node):
        frag = self._parse_template('message.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:parameter')
    def parameter(self, node):
        frag = self._parse_template('parameter.inc', node=node)
        self._substitute_node(node, frag)

    @element('//webui:headline')
    def headline(self, node):
        frag = self._parse_template('headline.inc', node=node)
        self._substitute_node(node, frag)
