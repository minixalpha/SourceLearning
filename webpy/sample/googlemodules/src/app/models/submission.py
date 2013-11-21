# Author: Alex Ksikes

# TODO:
# - if the module submitted is in quoted HTML then it must unquoted
# - bad idea to catch generic exceptions

import web, os, sys

from app.models import modules

from app.helpers import utils
from app.helpers import image

def submit(module_url, tags=''):    
    success, err_msg = False, ''
    try:
        # parse the module xml
        module = parse_module(module_url)
        
        # set some default values
        set_defaults(module)
            
        # check if the module is valid
        is_valid(module)
        
        # get the module screenshot
        module.screenshot = grab_screenshot(module.screenshot)
    
    except:
        err_msg = sys.exc_info()[0]
    
    else:
        # add module and its tags to the db
        modules.add(module, tags)
        success = True
    
    return success, err_msg

def parse_module(module_url):
    module = web.storage(
        url=module_url, cached_xml='', screenshot='', title='', title_url='', 
        directory_title='', description='', author='', author_email='', 
        author_affiliation='', author_location='', render_inline='')
    
    if not module_url.startswith('http://'):
        raise 'Ooops! Submission has failed &#8211; the URL seems to be invalid.'
    
    try:
        html = utils.dnl(module_url)
        html = web.htmlunquote(html)  # this may confuse the parser
        xml = utils.parse_xml(html)
    except:
        raise 'Ooops! Submission has failed &#8211; the XML or HTML page could not be loaded successfully.'
    
    xnodes = xml.xpath('//ModulePrefs')
    if not xnodes:
        raise 'Ooops! The XML is valid, but we cannot find the module.'
    xnodes = xnodes[0]
    
    for attr in module:
        module[attr] = xnodes.get(attr) or module[attr]
    
    return module

def set_defaults(module):
    if not module.screenshot.startswith('http://'):
        module.screenshot = utils.urljoin(module.url, module.screenshot)
    
    if module.directory_title:
        module.title = module.directory_title
    
    if not module.render_inline:
        module.render_inline = 'never'
    
def is_valid(module):
    if modules.is_banned_site(module.url):
        raise '<p>Ooops! The site you tried to submit is banned...</p>'
    
    elif not module.title or not module.author:
        raise 'Ooops! Submission has failed &#8211; please provide title and author name in your XML.'
    
    elif module.render_inline not in ['never', 'optional', 'required']:
        raise 'Ooops! Submission has failed &#8211; ' \
            + 'your <em>render_inline</em> value must be either "optional", "required" or "never".'
    
    elif not module.screenshot:
        raise 'Ooops! Submission has failed &#8211; please provide a link to a screenshot in your XML.'
    
    elif modules.already_exists(module.url):
        raise 'Ooops! Submission has failed &#8211; this module has been submitted already ' \
            + '(possible changes will automatically be updated).';

def grab_screenshot(screenshot_url):
    try:
        data = utils.dnl(screenshot_url)
        guid = utils.get_guid() + '.' + utils.get_extension_from_url(screenshot_url)
        image.save(data, 'public/img/screenshot/' + guid)
    
    except:
        raise 'Ooops! Submission has failed &#8211; <a href="%s">' % web.urlquote(screenshot) \
            + ' the screenshot</a> in your XML could not be found, was broken, or had the wrong dimensions' \
            + ' (should be above 30x20 and below 460x420).'
            
    return guid
