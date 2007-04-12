<script type="text/javascript">
<%
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    for action in actions:
        print parser.include('/support/webui/action.inc', node=action)
%>
</script>
<div class="buttonlist">
<%
    from draco2.webui.exception import WebUIError

    try:
        buttonlist = node.attrib['name']
    except KeyError:
        m = 'Required attribute "name" not set for <draco:buttonlist>.'
        raise WebUIError, m
    for action in actions:
        try:
            name = action.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set for <draco:action>.'
            raise WebUIError, m
        label = action.attrib.get('label', name)
        print '<input type="button" name="%s" value="%s"' % (name, tr(label))
        print 'onclick="action_%s_%s()" />' % (buttonlist, name)
%>
</div>
