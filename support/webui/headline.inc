<%
    from draco2.webui.exception import WebUIError

    object = node.attrib.get('object')
    if not object:
        m = 'Required attribute "object" missing for <webui:headline />'
        raise WebUIError, m

    ns = api.handler
    start = handler.get('start', 0)
    results = handler.get('results', 0)
    count = handler.get('count', 0)
 
    print '<p>'
    print tr('Showing %s %d through %d out of a total of %d %s that match' \
             ' your query.') % (tr(object), start+1, start+results, count,
                                tr('plural:%s' % object))
    print '</p>'
%>
