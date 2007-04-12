/* vi: ts=8 sts=4 sw=4 et
 *
 * compat.js: Javascript compatiblity library.
 *
 * This file is part of Draco2, a dynamic web content system in Python.
 * Draco2 is copyright (C) 1999-2005 Geert Jansen <geert@boskant.nl>.
 * All rights are reserved.
 *
 * $Revision: $
 */

function parentNode(el)
{
    if (el.parentNode)
        return el.parentNode;
    return el.parentElement;
}

function childNodes(el)
{
    if (el.childNodes)
        return el.childNodes;
    return el.children;
}

function isChildNode(p, c)
{
    while (parentNode(c) && (parentNode(c) != p))
        c = parentNode(c);
    return parentNode(c) != null;
}

function getAttribute(el, name)
{
    if (el.getAttribute)
        return el.getAttribute(name);
}

function getElementById(id, w)
{
    if (w == null)
        w = window;
    if (w.document.getElementById)
        return w.document.getElementById(id);
    return w.document.all[id];
}

function getElementsByTagName(tagname, w)
{
    if (w == null)
        w = window;
    if (w.document.getElementsByTagName)
        return w.document.getElementsByTagName(tagname);
    return w.document.all.tags(tagname);
}

function srcElement(event)
{
    if (event.srcElement)
        return event.srcElement;
    return event.target;
}

function activecursor()
{
    if (navigator.userAgent.indexOf("MSIE") > 0)
	return 'hand';
    else
	return 'pointer';
}

function normalcursor()
{
    return 'auto';
}

function tableRow()
{
    if (navigator.userAgent.indexOf("MSIE") > 0)
        return "block";
    else
        return "table-row";
}

function getXmlHttpRequest()
{
    if (window.XMLHttpRequest)
        return new XMLHttpRequest();
    else if (window.ActiveXObject)
        return new ActiveXObject("Microsoft.XMLHTTP");
}

function getEvent(event)
{
    if (event == null)
        event = window.event;
    return event;
}
