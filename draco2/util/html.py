# vi: ts=8 sts=4 sw=4 et
#
# html.py: html utilities
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

# HTML encoding

html_encode =  { '<': 'lt', '>': 'gt', '&': 'amp', '"': 'quot', "'": 'apos' }
html_decode =  { 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': "'" }

def quote_html(s, unsafe='<>&"\''):
    """
    Encode a string by replacing unsafe characters with their
    SGML entity reference.
    """
    res = list(s)
    for i in range(len(res)):
        if res[i] in unsafe:
            res[i] = '&' + html_encode[res[i]] + ';'
    return ''.join(res)

def unquote_html(s):
    """
    Unquote SGML entities with their ASCII representation.
    """
    lst = s.split('&')
    res = [lst[0]]
    for s in lst[1:]:
        p1 = s.find(';')
        if p1 != -1:
            try:
                res.append(html_decode[s[:p1]])
                res.append(s[p1+1:])
            except KeyError:
                res.append('&' + s)
        else:
            res.append('&' + s)
    return ''.join(res)
