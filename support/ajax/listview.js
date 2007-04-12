/* vi: ts=8 sts=4 sw=4 et
 *
 * listview.js: Javascript support for a listview in html.
 *
 * This file is part of Draco2, a dynamic web content system in Python.
 * Draco2 is copyright (C) 1999-2005 Geert Jansen <geert@boskant.nl>.
 * All rights are reserved.
 */


/* ListView factory function. */

function ListView(name, url, columns, actions, start, pagesize)
{
    /* Instance variables. */
    this.m_name = name;
    this.m_url = url;
    this.m_columns = columns;
    this.m_actions = actions;
    this.m_start = start;
    this.m_pagesize = pagesize;

    /* This brain damage is necessary because event handlers get
     * a different "this" pointer.... */

    var self = this;
    this.e_select = function(event) { self.select(event); }
    this.e_deselect = function(event) { self.deselect(event); }
    this.e_update_handler = function(req) { self._update_handler(req); }
    this.e_error_handler = function(req) { self._error_handler(req); }
}

/* ListView methods follow. */

ListView.prototype._get_div = function()
{
    var div;

    div = document.getElementById(this.m_name);
    if (div == null)
    {
        alert("Could not load listview DOM node.");
        return;
    }
    return div;
}

ListView.prototype._get_tbody = function()
{
    var div, tbodies;

    div = this._get_div();
    tbodies = div.getElementsByTagName('tbody');
    if (tbodies.length == 0)
    {
        alert('Could not load table body DOM node.')
        return;
    }
    return tbodies.item(0);
}

ListView.prototype._get_selection = function()
{
    var selection;

    selection = document.getElementById(this.m_name + "_selection");
    return selection;
}

ListView.prototype._get_rows = function()
{
    var tbody, rows;

    tbody = this._get_tbody();
    rows = tbody.getElementsByTagName('tr');
    return rows;
}

ListView.prototype._get_buttons = function()
{
    var div, inputs, input, buttons;

    div = this._get_div();
    inputs = div.getElementsByTagName('input');
    buttons = new Array();
    for (i=0; i<inputs.length; i++)
    {
        input = inputs.item(i);
        if (input.getAttribute("type") == "button")
            buttons.push(input);
    }
    return buttons;
}

ListView.prototype._append_row = function()
{
    var tbody, row, cell, i;

    tbody = this._get_tbody();
    row = document.createElement('tr');
    row.onclick = this.e_select;
    row.setAttribute("style", "cursor: pointer")
    for (i=0; i<this.m_columns.length; i++)
    {
        cell = document.createElement('td');
        row.appendChild(cell);
    }
    tbody.appendChild(row);
    return row;
}

ListView.prototype._remove_row = function()
{
    var tbody, rows;

    tbody = this._get_tbody();
    rows = tbody.getElementsByTagName('tr');
    if (rows.length == 0)
    {
        alert('Removing row from empty table!')
        return;
    }
    tbody.removeChild(rows.item(rows.length-1));
}

ListView.prototype._set_node_text = function(node, text)
{
    var i;
    for (i=0; i<node.childNodes.length; i++)
        node.removeChild(node.childNodes.item(i));
    text = document.createTextNode(text);
    node.appendChild(text);
}

ListView.prototype._update_row = function(row, data)
{
    var cells, cell, i, j;
    var value, text;

    cells = row.getElementsByTagName('td');
    if (cells.length != this.m_columns.length)
    {
        alert('Cannot update row with wrong # of cells.')
        return;
    }
    row.id = this.m_name + "_" + data["id"];
    for (i=0; i<cells.length; i++)
    {
        cell = cells.item(i);
        value = data[this.m_columns[i]];
        if (!value)
            continue;
        this._set_node_text(cell, value);
    }
}

ListView.prototype._update_links = function()
{
    var prev, next;
    prev = document.getElementById(this.m_name + "_prev");
    if (this.m_start > 0)
        prev.setAttribute("style", "display: table-cell");
    else
        prev.setAttribute("style", "display: none");
    next = document.getElementById(this.m_name + "_next");
    if (this.m_start + this.m_size < this.m_total)
        next.setAttribute("style", "display: table-cell");
    else
        next.setAttribute("style", "display: none");
}

ListView.prototype._update_heading = function()
{
    var start, end, total;
    start = getElementById(this.m_name + "_start");
    this._set_node_text(start, this.m_start + 1);
    end = getElementById(this.m_name + "_end");
    this._set_node_text(end, this.m_start + this.m_size);
    total = getElementById(this.m_name + "_total");
    this._set_node_text(total, this.m_total);
}

ListView.prototype._update_handler = function(req)
{
    var result, rows, i;
    var prev, next, remove;

    result = parse_xml_resultset(req.responseXML);
    if (result == null)
    {
        alert('Could not parse XML response.');
        return;
    }
    rows = this._get_rows();
    for (i=0; i<result.data.length; i++)
    {
        if (i >= rows.length)
            row = this._append_row();
        else
            row = rows[i];
        this._update_row(row, result.data[i]);
    }
    remove = rows.length - result.data.length;
    for (i=0; i<remove; i++)
    {
        this._remove_row();
    }
    this.m_start = result.start;
    this.m_size = result.size;
    this.m_total = result.total;

    this._update_links()
    this._update_heading()
    default_cursor();
}

ListView.prototype._error_handler = function(req)
{
    alert("Could not load XML data source. Server response was: " + req.status);
}

ListView.prototype.initialize = function()
{
    this.update(this.m_start, this.m_pagesize);
}

ListView.prototype.update = function(start, pagesize)
{
    var req, url;

    url = this.m_url + "?start=" + start + "&pagesize=" + pagesize;
    req = new AjaxRequest(url, this.e_update_handler, this.e_error_handler);
    req.start();
    hourglass_cursor();
}

ListView.prototype.prevpage = function()
{
    var start;
    if (this.m_start == 0)
        return;
    start = this.m_start - this.m_pagesize;
    if (start < 0)
        start = 0;
    this.update(start, this.m_pagesize);
}

ListView.prototype.nextpage = function()
{
    var start;
    if (this.m_total == null)
        return;  /* Not initialized yet. */
    if (this.m_start + this.m_pagesize >= this.m_total)
        return;
    start = this.m_start + this.m_pagesize;
    this.update(start, this.m_pagesize);
}

ListView.prototype.select = function(event, modifier)
{
    event = getEvent(event);

    var el = srcElement(event);
    while (el && el.tagName != 'tr')
    {
        el = parentNode(el);
    }
    if (el.tagName != 'tr')
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
    this.select_id(id, modifier);
}

ListView.prototype.select_id = function(id, modifier)
{
    var row, selected, selection, i, row, pos;
    var rowid, buttons, button, name, mincard, maxcard, field;

    selected = 0;
    selection = '';
    rows = this._get_rows();
    for (i=0; i<rows.length; i++)
    {
        row = rows[i];
        pos = row.id.indexOf('_');
        rowid = row.id.substring(pos+1, row.id.length);
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
    buttons = this._get_buttons();
    for (var i=0; i<buttons.length; i++)
    {
        button = buttons[i];
        name = button.name;
        mincard = this.m_actions[name][0];
        maxcard = this.m_actions[name][1];
        if ((selected >= mincard) && (selected <= maxcard))
            button.disabled = false;
        else
            button.disabled = true;
    }
    field = this._get_selection();
    field.setAttribute("value", selection);
}

ListView.prototype.deselect = function(event)
{
    var el = srcElement(event);
    while (((el.tagName != 'div') ||
            (el.className != 'listview')) && parentNode(el))
    {
        if (el.tagName == 'tr')
            break;
        el = parentNode(el);
    }
    if (el.tagName != 'div')
        return;
    var rows = this._get_rows();
    for (var i=0; i<rows.length; i++)
    {
        var row = rows[i]
        row.className = '';
    }
    var buttons = this._get_buttons();
    for (var i=0; i<buttons.length; i++)
    {
        var button = buttons[i];
        var name = button.name;
        var mincard = this.m_actions[name][0];
        if (mincard == 0)
            button.disabled = false;
        else
            button.disabled = true;
    }
    var field = this.m_name + '_selection';
    var form = webui_get_form();
    form[field].value = '';
}

function hourglass_cursor()
{
    var body = document.getElementsByTagName('body').item(0);
    body.style.cursor = "wait";
}

function default_cursor()
{
    var body = document.getElementsByTagName('body').item(0);
    body.style.cursor = "default";
}
