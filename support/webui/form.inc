<script type="text/javascript">
<%
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    for action in actions:
        print parser.include('/support/webui/action.inc', node=action)
%>
</script>

<div class="form">
<%
    import sys
    from draco2.webui.exception import WebUIError

    ns = api.handler
    try:
        form = node.attrib['name']
    except KeyError:
        m = tr('Required attribute "name" not set in <webui:form>.')
        raise WebUIError, m

    print '<table class="form" id="%s">' % form
    fields = node.xpath('.//webui:field', api.rewriter.namespaces())
    for field in fields:
        name = field.attrib.get('name')
        type = field.attrib.get('type', 'text')
        if not name or not type:
            continue
        value = ns.get(name)
        if type == 'hidden':
            print '<input type="hidden" name="%s"' % name
            if value:
                print ' value="%s"' % value.encode('html')
            print ' />'
            continue
        print '<tr> <td'
        if name in error_fields:
            print ' class="error"'
        label = field.attrib.get('label', name)
        print '> %s </td>' % tr(label)
        print '<td>'
        if type in ('text', 'password', 'checkbox', 'file'):
            print '<input type="%s" name="%s"' % (type, name)
            if field.attrib.has_key('class'):
                print ' class="%s"' % field.attrib['class']
            if field.attrib.has_key('readonly'):
                print ' readonly="%s"' % field.attrib['readonly']
            if type == 'checkbox':
                print ' value="true"'
            if value:
                if type == 'checkbox':
                    print ' checked="checked"'
                elif type != 'file':
                    print ' value="%s"' % value.encode('html')
            print ' />'
        elif type == 'textarea':
            print '<textarea name="%s"' % name
            if field.attrib.has_key('class'):
                print ' class="%s"' % field.attrib['class']
            if field.attrib.has_key('readonly'):
                print ' readonly="%s"' % field.attrib['readonly']
            sys.stdout.write('>')  # no newline
            if ns.has_key(name):
                sys.stdout.write(ns[name].encode('html'))
            print '</textarea>'
        elif type == 'select':
            print '<select name="%s" id="%s_%s"' % (name, form, name)
            if field.attrib.has_key('class'):
                print ' class="%s"' % field.attrib['class']
            if field.attrib.has_key('readonly'):
                print ' readonly="%s"' % field.attrib['readonly']
            if field.attrib.has_key('multiple'):
                print ' multiple="%s"' % field.attrib['multiple']
            if field.attrib.get('onchange'):
                print ' onchange="%s"' % field.attrib['onchange']
            print '>'
            print '<option value="">%s</option>' % tr('Select...')
            values = ns.get(name, [])
            if not isinstance(values, list):
                values = [values]
            options = field.xpath('.//webui:option', api.rewriter.namespaces())
            for option in options:
                name = option.attrib.get('name')
                if not name:
                    continue
                print '<option value="%s"' % name
                if str(name) in values:
                    print ' selected="selected"'
                label = option.attrib.get('label', name)
                print '>%s</option>' % tr(label)
            print '</select>'
        hints = []
        hint = field.attrib.get('hint')
        if hint:
            hints.append(tr(hint))
        required = field.attrib.get('required', 'true')
        if required in ('no', 'false'):
            hints.append(tr('optional'))
        hint = ', '.join(hints)
        if hint:
            print '<em>(%s)</em>' % tr(hint)
        print '</td> </tr>'

    print '<tr> <td colspan="2">'
    actions = node.xpath('.//webui:action', api.rewriter.namespaces())
    for action in actions:
        name = action.attrib.get('name')
        if not name:
            continue
        label = action.attrib.get('label', name)
        print '<input type="button" name="%s" value="%s"' % (name, tr(label))
        if action.attrib.has_key('class'):
            print ' class="%s"' % action.attrib['class']
        print ' onclick="action_%s_%s()" />' % (form, name)
    print '</td> </tr>'
    print '</table>'
%>
</div>

<script type="text/javascript">
<%
    if error_fields:
        focus = error_fields[0]
    else:
        fields = node.xpath('.//webui:field', api.rewriter.namespaces())
        for field in fields:
            if not field.attrib.has_key('readonly'):
                focus = field.attrib['name']
                break
        else:
            focus = ''
        if ns.get(focus):
            focus = ''
    if focus:
        print """
            function %s_init()
            {
                webui_focus("%s");
            }
            webui_add_init_func(%s_init);
            """ % (form, focus, form)
%>
</script>
