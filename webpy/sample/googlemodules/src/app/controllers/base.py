# Author: Alex Ksikes 

import web

from app.models import modules

from app.helpers import utils
from app.helpers import render
from app.helpers import misc

from config import view

class index:
    def GET(self):
        if web.input().has_key('q'):
           return web.seeother('/search/?' + utils.url_encode(web.input()))
            
        latest_modules, has_next = modules.get_latest()
        return render.layout(
            view.list_modules(latest_modules, next_page_url='/page/1/', sub_title='Latest Modules'))

class list:
    def GET(self, page_number):
        page_number = int(page_number)

        latest_modules, has_next = modules.get_latest(offset=page_number*10)
        
        next_page_url = ''
        if has_next:
            next_page_url = '/page/%s/' % (page_number + 1)
        
        sub_title = 'Latest Modules'
        if page_number:
             sub_title += ' - Page %s' % (page_number + 1)
        
        return render.layout(
            view.list_modules(latest_modules, next_page_url=next_page_url, sub_title=sub_title),
            title = page_number and 'Page %s - Google Modules' % (page_number + 1) or 'Google Modules')
    
class about:
    def GET(self):
        return render.layout(
            view.about(misc.get_credits()), title='About - Google Modules')
    
class help:
    def GET(self):
        return render.layout(view.help(modules.get_count()), title='FAQ - Google Modules')
