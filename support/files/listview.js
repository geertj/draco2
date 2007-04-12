/* 
 * listview.js: Javascript support for a listview in html.
 *
 * Copyright (c) 2005 Digital Fugue. All rights are reserved.
 */

function listview_get_rows()
{
    var list = getElementById('listview_' + this.name);
    var tags = getElementsByTagName('tr');
    var rows = new Array(tags.length);
    var i, count = 0;
    for (i=0; i<tags.length; i++)
    {
        tag = tags.item(i);
        if (isChildNode(list, tag) && (tag.className != 'head'))
            rows[count++] = tag;
    }
    rows.length = count;
    return rows;
}

function listview_get_buttons()
{
    var list = getElementById('listview_' + this.name);
    var tags = getElementsByTagName('input');
    var buttons = new Array(tags.length);
    var i, count = 0;
    for (i=0; i<tags.length; i++)
    {
        tag = tags.item(i);
        if (isChildNode(list, tag) && (tag.type == 'button'))
            buttons[count++] = tag;
    }
    buttons.length = count;
    return buttons;
}

function listview_activate(event, modifier)
{
    var el = srcElement(event);
    while (el && el.tagName.toLowerCase() != 'tr')
    {
        el = parentNode(el);
    }
    if (el.tagName.toLowerCase() != 'tr')
        return;
    var pos = el.id.indexOf('_');
    var id = el.id.substring(pos+1, el.id.length);
    if (modifier == null)
    {
        if (event.ctrlKey)
            modifier = 'control';
        else
            modifier = 'click';
    }
    this.activate_id(id, modifier);
}

function listview_activate_id(id, modifier)
{
    var selected = 0;
    var selection = '';
    var rows = this.get_rows();
    for (var i=0; i<rows.length; i++)
    {
        var row = rows[i];
        var pos = row.id.indexOf('_');
        var rowid = row.id.substring(pos+1, row.id.length);
        if (id == rowid)
        {
            if (modifier == 'dblclick' || row.className == '')
                row.className = 'active';
            else
                row.className = '';
        } else if (modifier != 'control')
            row.className = '';
        if (row.className == 'active')
        {
            if (selection)
                selection += ',';
            selection += rowid;
            selected += 1;
        }
    }
    var buttons = this.get_buttons();
    for (var i=0; i<buttons.length; i++)
    {
        var button = buttons[i];
        var name = button.name;
        var mincard = this.actions[name][0];
        var maxcard = this.actions[name][1];
        if ((selected >= mincard) && (selected <= maxcard))
            button.disabled = false;
        else
            button.disabled = true;
    }
    var field = this.name + '_selection';
    var form = webui_get_form();
    form[field].value = selection;
}

function listview_deactivate(event)
{
    var el = srcElement(event);
    while (((el.tagName.toLowerCase() != 'div') ||
            (el.className != 'listview')) && parentNode(el))
    {
        if (el.tagName.toLowerCase() == 'tr')
            break;
        el = parentNode(el);
    }
    if (el.tagName.toLowerCase() != 'div')
        return;
    var rows = this.get_rows();
    for (var i=0; i<rows.length; i++)
    {
        var row = rows[i]
        row.className = '';
    }
    var buttons = this.get_buttons();
    for (var i=0; i<buttons.length; i++)
    {
        var button = buttons[i];
        var name = button.name;
        var mincard = this.actions[name][0];
        if (mincard == 0)
            button.disabled = false;
        else
            button.disabled = true;
    }
    var field = this.name + '_selection';
    var form = webui_get_form();
    form[field].value = '';
}

function Listview(name, actions)
{
    this.name = name;
    this.actions = actions;
    this.get_rows = listview_get_rows;
    this.get_buttons = listview_get_buttons;
    this.activate = listview_activate;
    this.activate_id = listview_activate_id;
    this.deactivate = listview_deactivate;
}
