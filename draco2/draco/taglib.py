# vi: ts=8 sts=4 sw=4 et
#
# taglib.py: tag libraries
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import re
import lxml.etree 

import draco2
from draco2.core.exception import DracoInterfaceError
from draco2.draco.exception import RewriteError
from draco2.draco.image import ImageInfo
from draco2.draco.parser import DracoParser
from draco2.util.singleton import singleton


class element(object):
    """Decorator to indentify XML elements in tag libraries."""

    def __init__(self, xpath):
        self.m_xpath = xpath

    def __call__(self, func):
        func.element = True
        func.xpath = self.m_xpath
        return func


class TagLibrary(object):
    """Base class of all tag libraries."""

    # Default priority for a tag library. By convention this should be
    # between 0 and 100 inclusive, 0 meaning highest priority.
    priority = 50

    @classmethod
    def _create(cls, api):
        taglib = cls()
        return taglib

    def _elements(self):
        for name in dir(self):
            attr = getattr(self, name)
            if name.startswith('_') or not callable(attr):
                continue
            # a .element property is not required
            if hasattr(attr, 'xpath'):
                xpath = attr.xpath
            else:
                xpath = '//' + name
            yield (xpath, attr)

    def _parse_template(self, template, **kwargs):
        """Parse a template and return a XML fragment."""
        parser = DracoParser()
        namespace = draco2.api.handler.copy()
        namespace.update(kwargs)
        opener = draco2.api.opener
        buffer = parser.parse(template, namespace=namespace, opener=opener)
        frag = self._parse_fragment(buffer)
        return frag

    def _parse_fragment(self, buffer):
        """Parse a string `buffer' into a XML fragment."""
        buffer = '<fragment xmlns="http://www.w3.org/1999/xhtml">' \
                 + buffer + '</fragment>'
        try:
            tree = lxml.etree.XML(buffer).getroottree()
        except SyntaxError, err:
            m = 'Syntax error in XML fragment.'
            raise RewriteError, m
        return tree.getroot()

    def _substitute_descendants(self, node1, node2):
        """Substitute the descendants (text and children) of `node2'
        in place of `node1'."""
        node1.text = node2.text
        node1[:] = node2.getchildren()

    def _add_text(self, t1, t2):
        """Add two text strings, both possibly None."""
        if t1 is None and t2 is None:
            return None
        s = t1 or ''
        s += t2 or ''
        return s

    def _remove_node(self, node):
        """Remove `node' from the tree."""
        parent = node.getparent()
        ix = parent.index(node)
        if ix > 0:
            parent[ix-1].tail = self._add_text(parent[ix-1].tail, node.tail)
        else:
            parent.text = self._add_text(parent.text, node.tail)
        del parent[ix]

    def _substitute_node(self, node, frag):
        """Substitute `node' with fragment `frag'."""
        parent = node.getparent()
        ix = parent.index(node)
        if len(frag):
            frag[-1].tail = node.tail
        elif ix > 0:
            parent[ix-1].tail = self._add_text(parent[ix-1].tail, node.tail)
        else:
            parent.text = self._add_text(parent.text, node.tail)
        parent[ix:ix+1] = frag[:]


class DracoTagLibrary(TagLibrary):
    """Draco tag library.

    This tag library contains the tags that make automated session
    management and image size detection work.
    """

    namespaces = { 'draco': 'http://www.digitalfugue.com/NS/draco',
                   'xhtml': 'http://www.w3.org/1999/xhtml' }

    def __init__(self, images=None):
        super(DracoTagLibrary, self).__init__()
        self._set_rewrite_links(True)
        self._set_rewrite_images(True)
        self._set_image_info(images)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        taglib = super(DracoTagLibrary, cls)._create(api)
        config = api.config.ns('draco2')
        taglib._set_extension(config['extension'])
        config = api.config.ns('draco2.api.rewriter')
        if config.has_key('rewritelinks'):
            taglib._set_rewrite_links(config['rewritelinks'])
        if config.has_key('rewriteimages'):
            taglib._set_rewrite_images(config['rewriteimages'])
        images = singleton(ImageInfo, api, factory=ImageInfo._create)
        taglib._set_image_info(images)
        return taglib

    def _set_extension(self, extension):
        self.m_extension = extension

    def _set_rewrite_links(self, links):
        self.m_rewrite_links = links

    def _set_rewrite_images(self, images):
        self.m_rewrite_images = images

    def _set_image_info(self, images):
        """Set the image information class to use."""
        if images is not None and not isinstance(images, ImageInfo):
            raise TypeError, 'Expecting ImageInfo instance or None.'
        self.m_images = images

    def _rewrite_link(self, node, name):
        """Rewrite link attribute `name'."""
        if not self.m_rewrite_links:
            return
        try:
            value = node.attrib[name]
        except KeyError:
            return
        # Quick first check to prevent a full parse for links that
        # are certainly not Draco links.
        if value.find('.' + self.m_extension) == -1:
            return
        value = draco2.api.response.rewrite_uri(value)
        node.attrib[name] = value

    def _rewrite_image(self, node):
        """Detect `width' and `height' attributes."""
        if not self.m_rewrite_images or not self.m_images:
            return
        if not node.attrib.has_key('src') or node.attrib.has_key('width') or \
                node.attrib.has_key('height'):
            return
        info = self.m_images.get_info(node.attrib['src'])
        if info:
            node.attrib['width'] = str(info[1])
            node.attrib['height'] = str(info[2])

    @element('//xhtml:head')
    def head(self, node):
        request = draco2.api.request
        opener = draco2.api.opener
        reluri = '/%s/%s.css' % (request.directory(), request.basename())
        if opener.access(reluri):
            frag = '<link rel="stylesheet" type="text/css" href="%s" />\n' % reluri
            frag = self._parse_fragment(frag)
            node.append(frag[0])
        reluri = '/%s/%s.js' % (request.directory(), request.basename())
        if opener.access(reluri):
            frag = '<script type="text/javascript" src="%s" />\n' % reluri
            frag = self._parse_fragment(frag)
            node.append(frag[0])

    @element('//xhtml:a')
    def a(self, node):
        self._rewrite_link(node, 'href')

    @element('//xhtml:form')
    def form(self, node):
        self._rewrite_link(node, 'action')

    @element('//xhtml:area')
    def area(self, node):
        self._rewrite_link(node, 'href')

    @element('//xhtml:link')
    def link(self, node):
        self._rewrite_link(node, 'href')

    @element('//xhtml:frame')
    def frame(self, node):
        self._rewrite_link(node, 'src')

    @element('//xhtml:iframe')
    def iframe(self, node):
        self._rewrite_link(node, 'src')

    @element('//xhtml:script')
    def script(self, node):
        self._rewrite_link(node, 'src')

    @element('//xhtml:img')
    def img(self, node):
        self._rewrite_image(node)
        self._rewrite_link(node, 'src')


class TranslationTagLibrary(TagLibrary):
    """Tag library that automatically translates strings in
    an XML document.
    """

    TRANSLATE = 0
    COLLECT_MESSAGES = 1

    priority = 40
    namespaces = { 'xhtml': 'http://www.w3.org/1999/xhtml' }
    re_message = re.compile('.*[a-z]', re.I|re.S)

    def __init__(self, mode=None):
        """Constructor."""
        if mode is None:
            mode = self.TRANSLATE
        self.m_mode = mode
        self.m_messages = []

    def messages(self):
        """Return the recorded messages."""
        if self.m_mode != self.COLLECT_MESSAGES:
            raise DracoInterfaceError, 'Not recording messages.'
        return self.m_messages

    def _node_text(self, node):
        """Serialize the contents of an XML node."""
        msg = lxml.etree.tostring(node)
        p1 = msg.find('>')
        p2 = msg.rfind('<')
        return msg[p1+1:p2]

    def _normalize_message(self, message):
        """Normalize a message."""
        return message.strip()

    def _translate_node(self, node):
        """Translate a node."""
        message = self._node_text(node)
        message = self._normalize_message(message)
        if not message:
            return
        context = node.attrib.get('context')
        name = node.attrib.get('name')
        if self.m_mode == self.TRANSLATE:
            trans = draco2.api.locale.translate(message, context, name)
            if trans != message:
                frag = self._parse_fragment(trans)
                self._substitute_descendants(node, frag)
        elif self.m_mode == self.COLLECT_MESSAGES:
            self.m_messages.append((message, context, name))

    @element('//xhtml:title')
    def title(self, node):
        self._translate_node(node)

    @element('//xhtml:h1')
    def h1(self, node):
        self._translate_node(node)

    @element('//xhtml:h2')
    def h2(self, node):
        self._translate_node(node)

    @element('//xhtml:h3')
    def h3(self, node):
        self._translate_node(node)

    @element('//xhtml:h4')
    def h4(self, node):
        self._translate_node(node)

    @element('//xhtml:h5')
    def h5(self, node):
        self._translate_node(node)

    @element('//xhtml:h6')
    def h6(self, node):
        self._translate_node(node)

    @element('//xhtml:*[@translate]')
    def translate(self, node):
        self._translate_node(node)
        del node.attrib['translate']
