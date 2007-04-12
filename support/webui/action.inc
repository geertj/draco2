<%
    from draco2.webui.exception import WebUIError

    try:
        name = node.attrib['name']
    except KeyError:
        m = 'Required attribute "name" not present in <webui:action>.'
        raise WebUIError, m
    type = node.attrib.get('type', 'open_location')
    handler = node.attrib.get('handler', api.request.filename())
    if not handler.startswith('/'):
        handler = '/%s/%s' % (api.request.directory(), handler)
    if not handler.endswith('.' + api.request.extension()):
        handler = '%s.%s' % (handler, api.request.extension())
    context = node.attrib.get('context', 'keep')
    if type == 'open_location':
        destination = handler
        target = ''
    elif type in ('open_dialog', 'open_window', 'close_dialog',
                  'close_window'):
        destination = '/%s/%s' % (api.request.directory(), api.request.filename())
        target = handler
    options = 'context=%s' % context
    if node.attrib.has_key('context_name'):
        options += ',context_name=%s' % node.attrib['context_name']
    if node.attrib.has_key('width'):
        options += ',width=%s' % node.attrib['width']
    if node.attrib.has_key('height'):
        options += ',height=%s' % node.attrib['height']
    command = '%s:%s:%s' % (type, target, options)
    destination = api.response.rewrite_uri(destination)
    code = """
        function action_%s_%s()
        {
            var form = webui_get_form();
            form.action = "%s";
            form["transient:command"].value = "%s";
            form.submit();
        }
        """ % (node.getparent().attrib['name'], name, destination, command)
    print code.encode('html')
%>
