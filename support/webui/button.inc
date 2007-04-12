<%
    from draco2.webui.exception import WebUIError
    from draco2.webui.util import parse_cardinality

    try:
        name = node.attrib['name']
    except KeyError:
        m = 'Required attribute "name" not set on <webui:action>.'
        raise WebUIError, m
    label = node.attrib.get('label', name)
    card = parse_cardinality(node.attrib.get('cardinality', '0,n'))
    parent = node.getparent().attrib['name']

    print '<input type="button" name="%s" value="%s"' % (name, label)
    if card[0] > 0:
        print 'disabled="disabled"'
    print 'onclick="action_%s_%s()" />' % (parent, name)
%>
