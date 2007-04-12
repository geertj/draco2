/* vi: ts=8 sts=4 sw=4 et
 *
 * ajax.js: Javascript support for AJAX (Asynchronous Javascript and XML)
 *
 * This file is part of Draco2, a dynamic web content system in Python.
 * Draco2 is copyright (C) 1999-2005 Geert Jansen <geert@boskant.nl>.
 * All rights are reserved.
 */

/* Factory method: return an AjaxRequest object. */

function AjaxRequest(callback, error_callback)
{
    this.m_callback = callback;
    this.m_error_callback = error_callback;

    var self = this;
    this.cb_state_change = function() { self._state_change(); }
}

AjaxRequest.prototype._state_change = function()
{
    var req, callback;

    req = this.m_request;
    if (req.readyState == 4)
    {
        if (req.status == 200)
            callback = this.m_callback;
        else
            callback = this.m_error_callback;
        callback(req);
    }
}

AjaxRequest.prototype.start = function(url, method, data)
{
    var req;

    if (method == null)
        method = "GET";
    req = getXmlHttpRequest();
    this.m_request = req;
    req.onreadystatechange = this.cb_state_change;
    req.open(method, url, true);
    if (method == "GET")
    {
        req.send(null);
    } else if (method == "POST")
    {
        req.setRequestHeader("Content-Type",
                             "application/x-www-form-urlencoded");
        req.send(data);
    }
}

/* Empty class used as an associative array. */

function Record()
{
}


/* Parse an XML result set to a javascript array of objects. */

function parse_xml_resultset(doc)
{
    var root, resultset, start, size, total;
    var results, result, key, value, item
    var i, j

    root = doc.documentElement;
    if (root.tagName != "resultset")
        return; /* return on any incompliant XML */
    resultset = new Record();
    start = parseInt(root.getAttribute("start"));
    if (isNaN(start))
        return;
    size = parseInt(root.getAttribute("size"));
    if (isNaN(size))
        return;
    total = parseInt(root.getAttribute("total"));
    if (isNaN(total))
        return;
    resultset.start = start;
    resultset.size = size;
    resultset.total = total;
    resultset.data = new Array();
    results = root.getElementsByTagName("result");
    for (i=0; i<results.length; i++)
    {
        result = results.item(i);
        item = new Record()
        for (j=0; j<result.childNodes.length; j++)
        {
            key = result.childNodes.item(j);
            if (key.nodeType != key.ELEMENT_NODE)
                continue;
            if (key.childNodes.length == 0)
                value = "";
            else if (key.childNodes.length == 1)
            {
                value = key.childNodes.item(0);
                if (value.nodeType != value.TEXT_NODE)
                    return;
                value = value.data;
            } else
                return;
            item[key.tagName] = value;
        }
        resultset.data.push(item);
    }
    return resultset;
}
