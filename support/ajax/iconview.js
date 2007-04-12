/* vi: ts=8 sts=4 sw=4 et
 *
 * iconview.js: Javscript support for an iconview in html.
 *
 * This file is part of Draco2, a dynamic web content system in Python.
 * Draco2 is copyright (C) 1999-2005 Geert Jansen <geert@boskant.nl>.
 * All rights are reserved.
 *
 * $Revision: $
 */

function iconview_select(event, event_type)
{
    var el = srcElement(event);
    while (el && el.tagName != 'td')
    {
        el = parentNode(el);
    }
    if (el == null || el.tagName != 'td')
        return;
    var pos = el.id.indexOf('_');
    var id = el.id.substring(pos+1, el.id.length);
    if (modifier == null)
    {
        if (event.ctrlKey)
            event_type = 'ctrl_click';
        else
            event_type = 'click';
    }
    this.activate(id, event_type);
}

function iconview_activate(id, event_type)
{
}


function IconView(name, actions)
{
    this.name = name;
    this._actions = actions;
    this.select = iconview_select;
    this.deselect = iconview_deselect;
    this._activate = _iconview_activate;
    this._get_items = _iconview_get_items();
}
