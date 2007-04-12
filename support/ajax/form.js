/* vi: ts=8 sts=4 sw=4 et
 *
 * form.py: AJAX form handling
 *
 * This file is part of the Second Home Support website.
 * Copyright (c) 2005 Digital Fugue. All rights are reserved.
 *
 * $Revision: $
 */


function Form(name, action, fields)
{
    this.m_name = name;
    this.m_action = action;
    this.m_fields = fields;

    // Use closures to bind this parameter.
    var self = this;
    this.cb_submission_done = function(req) { self._submission_done(req); }
    this.cb_submission_error = function(req) { self._submission_error(req); }
}

Form.prototype.submit = function()
{
    var form, data;

    data = this._get_form_data();
    request = new AjaxRequest(this.cb_submission_done, this.cb_submission_error);
    request.start(this.m_action, "POST", data);
}

Form.prototype._submission_done = function(request)
{
    var message;

    data = this._parse_formresult(request.responseXML);
    if (data.status == "ok")
    {
        message = document.getElementById(this.m_name + "_message");
        dom_set_text_contents(message, data.message);
        message.className = "";
    } else
    {
        message = document.getElementById(this.m_name + "_message");
        dom_set_text_contents(message, data.message);
        message.className = "error";
        olderrors = document.getElementsByTagName('td');
        for (i=0; i<olderrors.length; i++)
            olderrors.item(i).className = "";
        for (i=0; i<data.fields.length; i++)
        {
            field = data.fields[i];
            label = document.getElementById(this.m_name + "_" + field
                                            + "_label");
            label.className = "error";
        }
    }
}

Form.prototype._submission_error = function(request)
{
    alert("Could not complete form submission. Please try again.")
}

Form.prototype._get_form = function()
{
    var form;

    form = document.getElementById(this.m_name);
    if (!form)
    {
        alert("Could not retrieve form DOM node.");
        return;
    }
    return form;
}

Form.prototype._get_form_data = function()
{
    var from, result, element, option;
    var i, j;

    result = new String("");
    form = this._get_form();
    for (i=0; i<form.elements.length; i++)
    {
        element = form.elements.item(i);
        if ((element.tagName == "input") &&
            ((element.type == "text") || (element.type == "password")))
        {
            result += "&" + element.name + "=" + encodeURI(element.value);
        }
        else if (element.tagName == "select")
        {
            for (j=0; j<element.options.length; j++)
            {
                option = element.options.item(j);
                if (option.selected)
                    result += "&" + element.name + "=" + option.value;
            }
        }
    }
    // remove the initial "&"
    result = result.substring(1, result.length);
    return result;
}

Form.prototype._parse_formresult = function(doc)
{
    var top, result, node, i;

    top = doc.documentElement;
    if (top.tagName != "formresult")
        return;
    result = Object();
    result.fields = new Array();
    for (i=0; i<top.childNodes.length; i++)
    {
        node = top.childNodes.item(i);
        if (!dom_is_text_node(node))
            return;
        if (node.tagName == "status")
            result.status = dom_get_text_contents(node);
        else if (node.tagName == "message")
            result.message = dom_get_text_contents(node);
        else if (node.tagName == "field")
            result.fields.push(dom_get_text_contents(node));
        else
            return;
    }
    if (!result.status || !result.message)
        return;
    return result;
}
