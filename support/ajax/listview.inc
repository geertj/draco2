<script type="text/javascript">
<%
    from draco2.webui import WebUIError
    from draco2.webui.util import parse_cardinality

    try:
        listview = node.attrib['name']
        source = node.attrib['source']
    except KeyError:
        m = 'Required attributes "name"/"url" not set on <webui:listview>.'
        raise WebUIError, m
    start = 0
    pagesize = int(node.attrib.get('pagesize', 20))
    source = api.response.resolve_uri(source)

    jsobj = 'listview_%s' % listview
    print 'var %s_columns = new Array();' % listview
    columns = node.xpath('.//webui:column', api.rewriter.namespaces())
    for column in columns:
        try:
            name = column.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set on <webui:column>.'
            raise WebUIError, m
        print '%s_columns.push("%s");' % (listview, name)
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    print 'var %s_actions = new Array(%d);' % (listview, len(actions))
    for action in actions:
        try:
            name = action.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set on <webui:action>.'
            raise WebUIError, m
        print parser.include('/support/webui/action.inc', node=action)
        card = parse_cardinality(action.attrib.get('cardinality', '0,n'))
        print '%s_actions["%s"] = new Array(%d, %d);' % \
                    (listview, action.attrib['name'], card[0], card[1])
    print 'var %s = new ListView("%s", "%s", %s_columns, %s_actions, %d, %s);' \
                % (jsobj, listview, source, listview, listview, start, pagesize)
%>
</script>

<input type="hidden" id="<%=listview%>_selection" name="<%=listview%>_selection" />
<div class="listview" id="<%=listview%>" onclick="<%=jsobj%>.deselect(event)">

<p>
<%
    args = ('<strong id="%s_start"></strong>' % listview,
            '<strong id="%s_end"></strong>' % listview,
            '<strong id="%s_total"></strong>' % listview)
    print tr('Displayed: entry %s through %s out of a total of %s.') % args
%>
</p>

<table class="listview">
<thead>
<tr>
<%
    columns = node.xpath('.//webui:column', api.rewriter.namespaces())
    for column in columns:
        name = column.attrib['name']
        label = column.attrib.get('label', name)
        print '<td>%s</td>' % label
%>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table class="pagebar">
<tr>
<%
    print '<td id="%s_prev"> <a onclick="%s.prevpage()">' \
            % (listview, jsobj)
    print '&lt;-- %s </a> </td>' % tr('previous page')
    print '<td id="%s_next"> <a onclick="%s.nextpage()">' \
            % (listview, jsobj)
    print '%s --&gt; </a> </td>' % tr('next page')
%>
</tr>
</table>

<div class="buttonlist">
<%
    for action in actions:
        print parser.include('/support/webui/button.inc', node=action)
%>
</div>
<script type="text/javascript">
<%
    print 'function %s_init()' % listview
    print '{ %s.initialize(); }' % jsobj
    print 'webui_add_init_func(%s_init);' % listview
%>
</script>

</div>
