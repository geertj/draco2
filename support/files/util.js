/* 
 * util.js: javascript utilities for Orion.
 *
 * Copyright (c) 2005 Digital Fugue.
 */

function window_width(w)
{
    if (w == null)
        w = window;
    if (w.outerWidth)
        // Mozilla and others
        return w.outerWidth;
    else if (w.document.documentElement &&
             w.document.documentElement.offsetWidth)
        // Explorer in strict mode
        return w.document.documentElement.offsetWidth;
    else if (w.document.body &&
             w.document.body.offsetWidth)
        // Explorer
        return w.document.body.offsetWidth;
}

function window_height(w)
{
    if (w == null)
        w = window;
    if (w.outerHeight)
        // Mozilla and others
        return w.outerHeight;
    else if (w.document.documentElement &&
             w.document.documentElement.offsetHeight)
        // Explorer in strict mode
        return w.document.documentElement.offsetHeight;
    else if (w.document.body &&
             w.document.body.offsetHeight)
        // Explorer
        return w.document.body.offsetHeight;
}

function window_top(w)
{
    if (w == null)
        w = window;
    if (w.screenY)
        return w.screenY;
    else
        return w.screenTop;
}

function window_left(w)
{
    if (w == null)
        w = window;
    if (w.screenX)
        return w.screenX;
    else
        return w.screenLeft;
}

function set_window_width(width, w)
{
    if (w == null)
        w = window;
    if (w.outerWidth)
        w.outerWidth = width;
    else
        w.document.body.offsetWidth = width;
}

function set_window_height(height, w)
{
    if (w == null)
        w = window;
    if (w.outerHeight)
        w.outerHeight = height;
    else
        w.document.body.offsetHeight = height;
}

function set_window_top(top, w)
{
    if (w == null)
        w = window;
    if (w.screenY)
        w.screenY = top;
    else
        w.screenTop = top;
}

function set_window_left(left, w)
{
    if (w == null)
        w = window;
    if (w.screenX)
        w.screenX = left;
    else
        w.screenLeft = left;
}

function _open(url, name, width, height, top, left, options)
{
    var features, w;

    features = "width=" + width;
    features += ",height=" + height;
    features += ",top=" + top;
    features += ",left=" + left;
    if (options != null)
        features += "," + options;
    w = window.open(url, name, features);
    return w
}

function open_dialog(url, name, width, height, options)
{
    var features, top, left, w;

    if (name == null)
        name = 'dialog';
    if (width == null)
        width = 300;
    if (height == null)
        height = 200;
    features = "resizable=yes,dependent=yes";
    if (options != null)
        features += "," + options;
    top = window_top() + ((window_height() - height) / 4);
    left = window_left() + ((window_width() - width) / 2);
    w = _open(url, name, width, height, top, left, features);
    return w
}

function open_window(url, name, width, height, options)
{
    var features, top, left, w;

    if (name == null)
        name = "window";
    if (width == null)
        width = window_width();
    if (height == null)
        height = window_height();
    features = "resizable=yes,status=yes,scrollbars=yes";
    if (options != null)
        features += "," + options;
    top = window_top() + 20;
    left = window_left() + 20;
    w = _open(url, name, width, height, top, left, features);
    return w;
}

function open_location(url)
{
    var at = getAttribute(url, "href");
    if (at != null)
        self.window.location.href = at;
    else
        self.window.location.href = url;
}

function open_external(url)
{
    window.open(url);
    return false;
}

function resize_dialog(width, height)
{
    var w = window.parent;
    var left = window_left(w) + ((window_width(w) - width) / 2);
    var top = window_top(w) + ((window_height(w) - height) / 2);
    w.moveTo(left, top);
    w.resizeTo(width, height);
}
