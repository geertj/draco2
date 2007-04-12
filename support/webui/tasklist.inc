<script type="text/javascript">
<%
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    for action in actions:
        print parser.include('/support/webui/action.inc', node=action)
%>
</script>
<p translate="translate"> Tasklist: </p>
<ul class="tasklist">
<%
    from draco2.webui.exception import WebUIError

    try:
        tasklist = node.attrib['name']
    except KeyError:
        m = 'Required attribute "name" not set for <webui:tasklist>.'

    for action in actions:
        try:
            name = action.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set for <webui:action>.'
        label = action.attrib.get('label', name)
        print '<li> <a href="javascript:action_%s_%s()">%s</a> </li>' \
                % (tasklist, name, tr(label))
%>
</ul>
