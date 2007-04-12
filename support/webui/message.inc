<%
    if message:
        print '<p><em>%s</em></p>' % message.encode('html')
    elif node.attrib.has_key('default'):
        print '<p>%s</p>' % node.attrib['default'].encode('html')
%>
