# -*- coding: utf-8 -*-

# Author: Alex Ksikes

import web
from web import net

import strip_html

import re, urlparse, datetime, urllib, types

def format_date(d, f):
    return d.strftime(f)

def url_quote(url):
    return urllib.quote_plus(url.encode('utf8')).decode('utf8')

def cut_length(s, max=40):
    if len(s) > max:
        s = s[0:max] + '...'
    return s

def get_nice_url(url):
    print url
    host, path = urlparse.urlparse(url)[1:3]
    if path == '/':
        path = ''
    return cut_length(host+path)

def text2html(s):
    s = html_quote(s)
    s = replace_links(s)
    s = replace_breaks(s)
    s = replace_indents(s)
    return s
    
def replace_breaks(s):
    return re.sub('\n', '<br/>', s)

def replace_indents(s):
    s = re.sub('\t', 4*' ', s)
    return re.sub('\s{2,}', '&nbsp;', s)

def replace_links(s):
    return re.sub('(http://[^\s]+)', 
        lambda m: '<a class="commentLink" rel="nofollow" href="%s">%s</a>' % (m.group(1), get_nice_url(m.group(1))), 
        s, re.I)

# we may want to get months ago as well
def how_long(d):
    return web.datestr(d, datetime.datetime.now())

def httpdate(date):
    return web.httpdate(date)

def html_quote(text):
    return net.htmlquote(text)

def html_quote_plus(text):
    text = html_quote(text)
    text = text.replace(' ', '&nbsp;')
    return text

def html_unquote(html):
    return net.htmlunquote(html)

def html_unquote_plus(html):
    html = html_unquote(html)
    html = html.replace('&nbsp;', ' ')
    return html

def nice_text(text):
    return text.replace('-', '--') \
               .replace('’', '\'') \
               .replace('“', '"')  \
               .replace('”', '"')

def strip_tags(html):
    html = html_unquote_plus(html)
    html = strip_html.strip(html)
    return html
    return nice_text(html)
