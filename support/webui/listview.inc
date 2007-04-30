<script type="text/javascript">
<%
    import sys
    from draco2.webui.exception import WebUIError

    # XXX: Python bug
    global sys, get_cardinality

    def get_cardinality(node):
        try:
            card = node.attrib['cardinality']
            if ',' in card:
                card = card.split(',')
            else:
                card = [card, card]
            for i in range(2):
                if card[i] == 'n':
                    card[i] = sys.maxint
                else:
                    card[i] = int(card[i])
        except (KeyError, ValueError):
            card = [0, sys.maxint]
        return card

    lvname = node.attrib.get('name')
    if not lvname:
        m = 'Required attribute "name" not set on <webui:listview>.'
        raise WebUIError, m
    jsname = 'listview_%s' % lvname
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    print 'var actions_%s = new Array(%d);' % (lvname, len(actions))
    for action in actions:
        try:
            name = action.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set on <webui:action>.'
            raise WebUIError, m
        print parser.include('/support/webui/action.inc', node=action)
        card = get_cardinality(action)
        print 'actions_%s["%s"] = new Array(%d, %d);' \
                    % (lvname, name, card[0], card[1])
    print 'var %s = new Listview("%s", actions_%s);' \
                % (jsname, lvname, lvname)
%>
</script>

<input type="hidden" name="<%=lvname%>_selection" />
<div class="listview" id="<%=jsname%>" onclick="<%=jsname%>.deactivate(event)">
<table class="listview">
<thead>
<tr>
<%
    columns = node.xpath('.//webui:column', api.rewriter.namespaces())
    for column in columns:
        try:
            name = column.attrib['name']
        except KeyError:
            m = 'Required attribute "name" not set on webui:column.'
            raise WebUIError, m
        label = column.attrib.get('label', name)
        print '<td>%s</td>' % tr(label)
%>
</tr>
</thead>
<tbody>
<%
    ns = api.handler
    try:
        data = node.attrib['data']
    except KeyError:
        m = 'Required attribute "data" not set on <webui:listview>.'
        raise WebUIError, m
    data = ns.get(data, [])
    default_action = node.attrib.get('default_action')
    for row in data:
        print '<tr onclick="%s.activate(event)" style="cursor: pointer"' % jsname
        if default_action:
            print ' ondblclick="%s.activate(event, \'dblclick\'); action_%s_%s()"' % \
                    (jsname, lvname, default_action)
        print 'id="%s_%s">' % (lvname, row['id'])
        for column in columns:
            print '<td>%s</td>' % unicode(row[column.attrib['name']]).encode('html')
        print '</tr>'
%>
</tbody>
</table>
<div class="navbar">
<%
    from __future__ import division

    if count is not '' and start is not '' and navurl and pagesize:
        args = {}
        if start > 0:
            args['start'] = str(max(start-pagesize, 0))
            url = api.response.patch_uri(navurl, args=args)
            print '<span class="prev"><a href="%s">&lt; %s </a></span>' % (url, tr('previous'))
        if start+len(data) < count:
            args['start'] = str(start + pagesize)
            url = api.response.patch_uri(navurl, args=args)
            print '<span class="next"><a href="%s">%s &gt;</a></span>' % (url, tr('next'))
        if count > pagesize:
            npages = 10
            firstpage = 0
            curpage = start // pagesize
            lastpage = (count + pagesize - 1) // pagesize
            if (lastpage - firstpage) < npages:
                startpage = firstpage
                endpage = lastpage
            elif curpage < npages//2:
                startpage = 0
                endpage = startpage + npages
            elif (lastpage - curpage) < npages//2:
                startpage = lastpage - npages
                endpage = lastpage
            else:
                startpage = curpage - npages//2
                endpage = curpage + npages//2
            pages = []
            for i in range(startpage, endpage):
                args['start'] = str(i*pagesize)
                url = api.response.patch_uri(navurl, args=args)
                if i == curpage:
                    pages.append('[ %s ]' % (curpage + 1))
                else:
                    pages.append('<a href="%s"> %s </a>' % (url, i+1))
            print '<span class="pages"> %s </span>' % ' - '.join(pages)
%>
</div>
<div class="buttonlist">
<%
    for action in actions:
        name = action.attrib['name']
        label = action.attrib.get('label', name)
        print '<input type="button" name="%s" value="%s"' % (name, tr(label))
        print ' onclick="action_%s_%s()"' % (lvname, name)
        card = get_cardinality(action)
        if card[0] > 0:
            print ' disabled="disabled"'
        print ' />'
%>
</div>
<script type="text/javascript">
<%
    print 'function listview_%s_activate()' % lvname
    print '{'
    for id in ns.get('%s_selection' % lvname, []):
        print '%s.activate_id("%s", true);' % (jsname, id)
    print '}'
    print 'webui_add_init_func(listview_%s_activate);' % lvname
%>
</script>

</div>
