# Author: Alex Ksikes 

import web
from web import http

import pycurl, random, re, cStringIO, types, urllib
import urlparse as _urlparse

from lxml import etree
from md5 import md5
from datetime import datetime

def url_encode(url):
    return http.urlencode(url)

def url_unquote(url):
    return urllib.unquote_plus(url)

def url_parse(url):
    return web.storage(
        zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'), _urlparse.urlparse(url)))

def url_join(url, url_relative):
    if '://' not in url_relative:
        if not url_relative.startswith('/'):
            url_relative = '/' + url_relative
    return _urlparse.urljoin(url, url_relative)
    
def get_user_ip():
    return web.ctx.get('ip', '000.000.000.000')

def parse_xml(txt):
    xml = re.sub('xmlns\s*=\s*["\'].*?["\']', ' ', txt) # we remove the xmlns for simplicity
    return etree.fromstring(xml, parser=etree.XMLParser(resolve_entities=False))

def curl_init():
    curl = pycurl.Curl()
    curl.setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)")
    curl.setopt(pycurl.FOLLOWLOCATION, True)
    #curl.setopt(pycurl.CONNECTTIMEOUT, 3)
    #curl.setopt(pycurl.TIMEOUT, 30)
    
    return curl

# PIL complains when only f is returned but all we are doing is stringIO(f.getvalue()) twice.
def open_url(curl, url, referer=None):
    curl.setopt(pycurl.URL, url)
    if referer:
        curl.setopt(pycurl.REFERER, referer)
    
    f = cStringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, f.write)
    curl.perform()
    
    html = f.getvalue()
    f.close()

    return html
    
def dnl(url, referer = None):
    c = curl_init()
    f = open_url(c, url, referer)
    c.close()
    
    return f

def dict_remove(d, *keys):
    for k in keys:
        if d.has_key(k):
            del d[k]
        
def get_extension_from_url(url):
    path = url_parse(url).path
    return path[path.rindex('.')+1:]
        
def get_unique_md5():
    return md5(str(datetime.now().microsecond)).hexdigest()

def get_guid():
    guid = get_unique_md5().upper()
    return '%s-%s-%s-%s-%s' % (guid[0:8], guid[8:12], guid[12:16], guid[16:20], guid[20:32])

def get_all_functions(module):
    functions = {}
    for f in [module.__dict__.get(a) for a in dir(module)
        if isinstance(module.__dict__.get(a), types.FunctionType)]:
        functions[f.__name__] = f
    return functions

def email_errors():
    if web.config.email_errors:
        web.emailerrors(web.config.email_errors, djangoerror())
        
def is_blacklisted(text, blacklist):
    text = text.strip().lower()
    for banned_word in blacklist:
        banned_word = banned_word.decode('utf-8').strip()
        if banned_word.lower() in text:
            return banned_word
    return False
