<script type="text/javascript">
<%
    from draco2.webui.command import parse_command

    # XXX: Python bug
    global handle_command, output_reload, parse_command

    def handle_command(command):
        try:
            action, destination, options = parse_command(command)
        except ValueError:
            return
        uri = api.response.rewrite_uri(destination)
        name = destination.replace('/', '_').replace('.', '_')
        width = options.get('width', 'null')
        height = options.get('height', 'null')
        if action == 'open_window':
            print 'open_window("%s", "%s", %s, %s);' % (uri, name, width, height)
        elif action == 'open_dialog':
            print 'open_dialog("%s", "%s", %s, %s);' % (uri, name, width, height)
        elif action == 'close_dialog':
            print 'window.close();'
        elif action == 'close_window':
            print 'window.close();'

    def output_reload():
        destination = api.response.resolve_uri(api.request.filename())
        destination = api.response.rewrite_uri(destination)
        code = """
            function action_reload()
            {
                var form = webui_get_form();
                form.action = "%s";
                form["transient:command"].value = "reload::";
                form.submit();
            }
        """ % destination
        print code.encode('html')

    if command:
        handle_command(command)
    output_reload()
%>
</script>
<input type="hidden" name="transient:command" />
