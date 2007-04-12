# vi: ts=8 sts=4 sw=4 et
#
# http.py: various HTTP related utilties
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import os.path
import re
import stat
import tempfile
import cStringIO
import codecs
import datetime

from draco2.util.uri import unquote_form, parse_query
from draco2.util.timezone import LocalTime, GMT

# HTTP response codes as defined in RFC 2616.

HTTP_CONTINUE = 100
HTTP_SWITCHING_PROTOCOLS = 101
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NON_AUTHORATIVE_INFORMATION = 203
HTTP_NO_CONTENT = 204
HTTP_RESET_CONTENT = 205
HTTP_PARTIAL_CONTENT = 206
HTTP_MULTIPLE_CHOICES = 300
HTTP_MOVED_PERMANENTLY = 301
HTTP_FOUND = 302
HTTP_SEE_OTHER = 303
HTTP_NOT_MODIFIED = 304
HTTP_USE_PROXY = 305
HTTP_TEMPORARY_REDIRECT = 307
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_PAYMENT_REQUIRED = 402
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_NOT_ACCEPTABLE = 406
HTTP_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_REQUEST_TIMEOUT = 408
HTTP_CONFLICT = 409
HTTP_GONE = 410
HTTP_LENGTH_REQUIRED = 411
HTTP_PRECONDITION_FAILED = 412
HTTP_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_REQUEST_URI_TOO_LONG = 414
HTTP_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_REQUEST_RANGE_NOT_SATISFIABLE = 416
HTTP_EXPECTATION_FAILED = 417
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505

http_reason_strings = \
{
    HTTP_CONTINUE: 'Continue',
    HTTP_SWITCHING_PROTOCOLS: 'Switching Protocols',
    HTTP_OK: 'OK',
    HTTP_CREATED: 'Created',
    HTTP_ACCEPTED: 'Accepted',
    HTTP_NON_AUTHORATIVE_INFORMATION: 'Non-Authoritative Information',
    HTTP_NO_CONTENT: 'No Content',
    HTTP_RESET_CONTENT: 'Reset Content',
    HTTP_PARTIAL_CONTENT: 'Partial Content',
    HTTP_MULTIPLE_CHOICES: 'Multiple Choices',
    HTTP_MOVED_PERMANENTLY: 'Moved Permanently',
    HTTP_FOUND: 'Found',
    HTTP_SEE_OTHER: 'See Other',
    HTTP_NOT_MODIFIED: 'Not Modified',
    HTTP_USE_PROXY: 'Use Proxy',
    HTTP_TEMPORARY_REDIRECT: 'Temporary Redirect',
    HTTP_BAD_REQUEST: 'Bad Request',
    HTTP_UNAUTHORIZED: 'Unauthorized',
    HTTP_PAYMENT_REQUIRED: 'Payment Required',
    HTTP_FORBIDDEN: 'Forbidden',
    HTTP_NOT_FOUND: 'Not Found',
    HTTP_METHOD_NOT_ALLOWED: 'Method Not Allowed',
    HTTP_NOT_ACCEPTABLE: 'Not Acceptable',
    HTTP_PROXY_AUTHENTICATION_REQUIRED: 'Proxy Authentication Required',
    HTTP_REQUEST_TIMEOUT: 'Request Timeout',
    HTTP_CONFLICT: 'Conflict',
    HTTP_GONE: 'Gone',
    HTTP_LENGTH_REQUIRED: 'Length Required',
    HTTP_PRECONDITION_FAILED: 'Precondition Failed',
    HTTP_REQUEST_ENTITY_TOO_LARGE: 'Request Entitty Too Large',
    HTTP_REQUEST_URI_TOO_LONG: 'Request-URI Too Long',
    HTTP_UNSUPPORTED_MEDIA_TYPE: 'Unsupported Media Type',
    HTTP_REQUEST_RANGE_NOT_SATISFIABLE: 'Requested Range Not Satisfiable',
    HTTP_EXPECTATION_FAILED: 'Expectation Failed',
    HTTP_INTERNAL_SERVER_ERROR: 'Internal Server Error',
    HTTP_NOT_IMPLEMENTED: 'Not Implemented',
    HTTP_BAD_GATEWAY: 'Bad Gateway',
    HTTP_SERVICE_UNAVAILABLE: 'Service Unavailable',
    HTTP_GATEWAY_TIMEOUT: 'Gateway Timeout',
    HTTP_VERSION_NOT_SUPPORTED: 'HTTP Version Not Supported'
}


# The full date format as required by RFC2616. Note that the
# timezone is required to be GMT!

rfc1123_datetime = '%a, %d %b %Y %H:%M:%S %Z'

# These are duplicated from the draco locale database so that this
# module can be independant. English days/months are required for
# RFC1123 and Netscape cookie date format.
english_days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
english_months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


# HTTP request parsing

class HTTPError(Exception):
    """HTTP Error."""

    def __init__(self, status, headers=None, message=None):
        self.m_status = status
        if headers is None:
            headers = {}
        self.m_headers = headers
        if message is None:
            message = ''
        self.m_message = message

    def status(self):
        return self.m_status

    def headers(self):
        return self.m_headers

    def message(self):
        return self.m_message


def parse_request(input):
    """Parse a HTTP request."""
    proto, method, uri = parse_request_line(input)
    headers = parse_headers(input)
    return proto, method, uri, headers


def parse_request_line(input):
    """Parse a HTTP request line."""
    line = input.readline().strip()
    try:
        method, uri, proto = line.split()
    except ValueError:
        raise HTTPError, HTTP_BAD_REQUEST
    return proto, method, uri


def parse_headers(input):
    """Parse RFC822-style headers.

    None of the advanced features from RFC822, such as long lines
    and (un)structured fields are supported.
    """
    headers = {}
    while True:
        line = input.readline()
        if not line:
            raise HTTPError, HTTP_BAD_REQUEST
        line = line.rstrip()
        if not line:
            break
        if line[:1].isspace():
            # We don't support RFC822 style continued headers
            raise HTTPError, HTTP_NOT_IMPLEMENTED
        p1 = line.find(':')
        if p1 == -1:
            raise HTTPError, HTTP_BAD_REQUEST
        name = line[:p1].lower()
        value = line[p1+1:].lstrip()
        try:
            headers[name].append(value)
        except KeyError:
            headers[name] = [value]
    return headers


# Form argument parsing

class FileUpload(object):
    """File upload form field."""

    def __init__(self, name, file, content_type, filename):
        self.name = name
        self.file = file
        self.content_type = content_type
        self.filename = filename

    def __getstate__(self):
        """Method called by pickle.dump()."""
        # File objects cannot be picled. As http arguments are often
        # pickled (for form postback), make sure we don't get an error.
        state = self.__dict__.copy()
        # XXX don't understand why `file' would not be here, but it
        # happens with pickle format 2.
        if state.has_key('file'):
            del state['file']
        return state


def parse_header_options(data):
    """Parse a header options.

    The return value is dictionary of lower-case strings
    mapping to lists of strings.

    Exceptions: TypeError or ValueError.
    """
    parts = [ i.strip() for i in data.split(';') ]
    ctype = parts[0]
    options = {}
    for part in parts[1:]:
        key, value = part.split('=')
        key = key.strip().lower()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        try:
            options[key].append(value)
        except KeyError:
            options[key] = [value]
    return ctype, options

def skip_until_boundary(input, boundary):
    """Skip input until RFC2046-style `boundary' is read.

    Exceptions: HTTPError
    """
    while True:
        line = input.readline()
        if line.startswith(boundary):
            break
        if not line:
            raise HTTPError, HTTP_BAD_REQUEST

def read_until_boundary(input, output, boundary):
    """Pass data from `input' to `output' until `boundary.

    If the end boundary is reached, return True, otherwise False.
    Exceptions: HTTPError
    """
    # Things are complicated by the fact that whitespace _before_ the
    # boundary belongs to the boundary.
    eol = oldeol = ''
    end_boundary = boundary + '--'
    while True:
        line = input.readline()
        if not line:
            raise HTTPError, HTTP_BAD_REQUEST
        if line.startswith(boundary):
            break
        if line.endswith('\r\n'):
            eol = '\r\n'
        elif line.endswith('\n'):
            eol = '\n'
        line = line[:-len(eol)]
        output.write(oldeol + line)
        oldeol = eol
    return line.startswith(end_boundary)

def parse_post(headers, input):
    """Parse POST style query string.

    The `headers' arguments must be a dictionary of HTTP headers,
    `input' must be a file-like object with read() and readline()
    methods.

    Exceptions: HTTPError
    """
    try:
        ctype = headers['content-type'][0]
    except KeyError:
        type = 'application/x-www-form-urlencoded'
    try:
        clen = int(headers['content-length'][0])
    except (KeyError, ValueError):
        raise HTTPError, HTTP_LENGTH_REQUIRED
    ctype, options = parse_header_options(ctype)

    # Traditional POST requests
    if ctype == 'application/x-www-form-urlencoded':
        data = input.read(clen)
        args = parse_query(data)
        return args

    # Newer POST requests with support for file uploads
    elif ctype.startswith('multipart/'):
        try:
            boundary = options['boundary'][0]
        except KeyError:
            raise HTTPError, HTTP_BAD_REQUEST
        boundary = '--' + boundary
        skip_until_boundary(input, boundary)

        args = {}
        while True:
            subheaders = parse_headers(input)
            try:
                cdisp = subheaders['content-disposition'][0]
            except KeyError:
                raise HTTPError, HTTP_BAD_REQUEST
            cdisp, dispoptions = parse_header_options(cdisp)
            try:
                name = dispoptions['name'][0]
            except KeyError:
                raise HTTPError, HTTP_BAD_REQUEST
            try:
                filename = dispoptions['filename'][0]
            except KeyError:
                filename = None
            if filename:
                output = tempfile.TemporaryFile()
            else:
                output = cStringIO.StringIO()
            atend = read_until_boundary(input, output, boundary)
            if filename:
                output.seek(0)
                try:
                    subctype = subheaders['content-type'][0]
                except KeyError:
                    raise HTTPError, HTTP_BAD_REQUEST
                value = FileUpload(name, output, subctype, filename)
            else:
                value = output.getvalue().decode('utf-8')
            if name in args:
                args[name].append(value)
            else:
                args[name] = [value]
            if atend:
                break
        return args

    else:
        raise HTTPError, HTTP_BAD_REQUEST


# Cookie parsing

class Cookie(object):
    """A single cookie with its attributes.

    The standard that is implemented here is the so-called Netscape cookie
    standard. See the file `docs/cookie.txt' in the source directory for more
    information.
    """

    # Format for the "Expires" cookie attribute. The time zone must be in
    # GMT and the day/month names must be in english. This format is a
    # hybrid from four (!) RFCs 822/850/1036/1123. Would you believe that?
    nscookie_datetime = '%a, %d-%b-%Y %H:%M:%S %Z'

    def __init__(self, name, value, path=None, domain=None, expires=None,
                 secure=None):
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.expires = expires
        self.secure = secure

    def encode(self):
        """
        Encode the cookie for use in a `Set-Cookie' header.
        """
        s = '%s=%s' % (self.name.encode('form'), self.value.encode('form'))
        if self.path is not None:
            s += '; Path=%s' % self.path
        if self.domain is not None:
            s += '; Domain=%s' % self.domain
        if self.expires is not None:
            value = _format_english_gmt_date(self.expires,
                                             self.nscookie_datetime)
            s += '; Expires=%s' % value
        if self.secure:
            s += '; Secure'
        return s

def parse_cookie(data):
    """Parse a `Cookie:' header and return a dictionary of Cookie objects."""
    cookies = {}
    parts = data.split(';')
    for part in parts:
        p1 = part.find('=')
        if p1 != -1:
            name = unquote_form(part[:p1].strip())
            value = unquote_form(part[p1+1:].strip())
        else:
            name = unquote_form(part.strip())
            value = ''
        cookie = Cookie(name, value)
        try:
            cookies[name].append(cookie)
        except KeyError:
            cookies[name] = [cookie]
    return cookies


# User-agent parsing

re_agent = re.compile('(?:([a-zA-Z]+)\s+([0-9.]+)|([^/(]*)(?:/([\w.]+))?)' \
                      '[^(]*(?:\((.*)\))?')
re_split = re.compile('\s*[;,]\s*')

def _parse_user_agent(data):
    """Low-level parse function."""
    mobj = re_agent.match(data)  # always matches
    if mobj.group(1) is None:
        assert mobj.group(3) is not None
        name, version = mobj.group(3), mobj.group(4)
    else:
        assert mobj.group(3) is None
        name, version = mobj.group(1), mobj.group(2)
    if version is None:
        version = ''
    info = mobj.group(5)
    return name, version, info

def parse_user_agent(data):
    """Parse the 'User-Agent' http header.

    The return value is a 3-tuple: browser, version, info. The browser
    is the short browser name, version is its version, and info is a
    is a list of extra strings passed by the client.
    """
    name, version, info = _parse_user_agent(data)
    if info:
        info = re_split.split(info)
        if len(info) >= 2 and info[0] == 'compatible':
            name, version, dummy = _parse_user_agent(info[1])
            info = info[2:]
    else:
        info = []
    return name, version, info


# Various other utilities

def parse_accept_encoding(data):
    """Parse the accept-encoding HTTP header.

    The result is returned as a list of supported encodings.
    """
    encodings = [ x.strip().lower() for x in data.split(',') ]
    return encodings


def _get_header(input, size=32):
    """Return a `size' bytes header for `input'.

    The `input' may be a file objects or a string.

    Exceptions: HTTPError (in case of file inputs), TypeError.
    """
    if isinstance(input, basestring):
        head = input[:size]
    elif hasattr(input, 'seek'):
        try:
            input.seek(0)
            head = input.read(size)
        except IOError:
            raise HTTPError, HTTP_NOT_FOUND
    else:
        raise TypeError, 'Expecting string or file-object.'
    return head


re_text = re.compile('^[\x09\x0a\x0d\x20-\x7e]+$')

def get_mime_type(input, fname='', default='application/octet-stream'):
    """Return the MIME type a file.

    The MIME type is detected form the file header. Only a small
    subset of MIME types are supported.
    """
    head = _get_header(input, size=200)
    # Need to make a special cases for unicode where the test strings
    # contain bytes >= \x80, as those cannot be decoded to ascii to
    # make the comparison.
    ucode = isinstance(head, unicode)
    if ucode and head.startswith(u'\x89PNG\r\n\x1a\n'):
        mime_type = 'image/png'
    elif not ucode and head.startswith('\x89PNG\r\n\x1a\n'):
        mime_type = 'image/png'
    elif head[:6] in ('GIF87a', 'GIF89a'):
        mime_type = 'image/gif'
    elif ucode and head[:4] == u'\xff\xd8\xff\xe0' and head[6:10] == 'JFIF':
        mime_type = 'image/jpeg'
    elif not ucode and head[:4] == '\xff\xd8\xff\xe0' and head[6:10] == 'JFIF':
        mime_type = 'image/jpeg'
    elif head.find('<?xml') != -1:
        mime_type = 'text/xml'
    elif head.find('//W3C//DTD XHTML') != -1:
        mime_type = 'application/xhtml+xml'
    elif head.find('<html') != -1:
        mime_type = 'text/html'
    elif fname.endswith('.xml'):
        mime_type = 'text/xml'
    elif fname.endswith('.js'):
        mime_type = 'text/javascript'
    elif fname.endswith('.css'):
        mime_type = 'text/css'
    elif re_text.match(head):
        mime_type = 'text/plain'
    else:
        mime_type = default
    return mime_type


def get_encoding(input, default='utf-8'):
    """Return the encoding of a file.

    The file should be a text file, i.e. have a MIME type of text/*.
    """
    head = _get_header(input)
    if head.startswith(codecs.BOM_UTF8):
        encoding = 'utf8'
    elif head.startswith(codecs.BOM_UTF16_BE):
        encoding = 'utf16-be'
    elif head.startswith(codecs.BOM_UTF16_LE):
        encoding = 'utf16-le'
    elif head.startswith(codecs.BOM_UTF32_BE):
        encoding = 'utf32-be'
    elif head.startswith(codecs.BOM_UTF32_LE):
        encoding = 'utf32-le'
    else:
        encoding = default
    return encoding


def _format_english_gmt_date(dt, format):
    """Format a datetime object in in GMT, using English day/month names."""
    # Assume local time if naive. Convert to GMT.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LocalTime())
    dt = dt.astimezone(GMT())
    # This makes formatting locale agnostic, so that we can run in an
    # environment with non-default locale.
    format = format.replace('%a', english_days[dt.weekday()]) \
                   .replace('%b', english_months[dt.month-1])
    return dt.strftime(format)


def get_last_modified(st):
    """Return a the last modification header from a stat result.

    The format looks like: Sun, 06 Nov 1994 08:49:37 GMT.

    Exceptions: HTTPError
    """
    dt = datetime.datetime.fromtimestamp(st.st_mtime)
    result = _format_english_gmt_date(dt, rfc1123_datetime)
    return result


def simple_response(conn, status=None, headers=None, message=None):
    """Write a simple HTTP response."""
    if status is None:
        status = HTTP_OK
    if headers is None:
        headers = {}
    if message is None:
        message = ''
    conn.write('HTTP/1.1 %d %s\r\n' % (status, http_reason_strings[status]))
    headers['content-type'] = ['text/plain']
    headers['content-length'] = [str(len(message))]
    headers['connection'] = ['close']
    for key in headers:
        for value in headers[key]:
            conn.write('%s: %s\r\n' % (key, value))
    conn.write('\r\n')
    conn.write(message)
