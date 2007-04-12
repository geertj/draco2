<%
    from draco2.webui.exception import WebUIError

    try:
        name = node.attrib['name']
    except KeyError:
        m = 'Required attribute "name" not set on <draco:parameter>.'
        raise WebUIError, m
    type = node.attrib.get('type')
    if type:
        name = '%s:%s' % (type, name)
    print '<input type="hidden" name="%s"' % name
    value = node.attrib.get('value')
    if value:
        print ' value="%s"' % value
    print ' />'
%>
