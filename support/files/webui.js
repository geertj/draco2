 /* vi: ts=8 sts=4 sw=4 et
 *
 * webui.js: javascript functions for webui
 *
 * This file is part of Draco2, a dynamic web content system in Python.
 * Draco2 is copyright (C) 1999-2005 Geert Jansen <geert@boskant.nl>.
 * All rights are reserved.
 *
 * $Revision: $
 */

function webui_get_form()
{
    var elements = getElementsByTagName("form");
    for (var i=0; i<elements.length; i++)
    {
        var el = elements[i];
        if (el.className == "webui")
            return el;
    }
}

function webui_focus(name)
{
    var form = webui_get_form();
    var el = form[name];
    if (el)
    {
        if (el.focus) el.focus();
        if (el.select) el.select();
    }
}

var webui_init_funcs = new Array(0);

function webui_add_init_func(func)
{
    webui_init_funcs.push(func);
}

function webui_body_onload()
{
    for (var i=0; i < webui_init_funcs.length; i++)
    {
        webui_init_funcs[i]();
    }
}

/* Remove all children from `node', and insert a new text
 * node containing `text'. */

function dom_set_text_contents(node, text)
{
    var textnode;
    while (node.childNodes.length)
        node.removeChild(node.childNodes.item(0));
    textnode = node.ownerDocument.createTextNode(text);
    node.appendChild(textnode);
    return node;
}

function dom_is_text_node(node)
{
    if (node.nodeType != node.ELEMENT_NODE)
        return 0;
    if (node.childNodes.length > 1)
        return 0;
    if ((node.childNodes.length == 1) &&
            (node.childNodes.item(0).nodeType != node.TEXT_NODE))
        return 0;
    return 1;
}

function dom_get_text_contents(node)
{
    if (!dom_is_text_node(node))
        return;
    return node.childNodes.item(0).data;
}
