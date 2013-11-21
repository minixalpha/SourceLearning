# Author: Alex Ksikes 

# TODO:
# - _mysql_exceptions.ProgrammingError for bad input parameters

import web

from app.models import modules

from app.helpers import render
from app.helpers import utils

from config import view

class search:
    def GET(self):
        i = web.input(q='', page_number=0)
        
        page_number = int(i.page_number)
        
        searched, has_next = modules.search(i.q, offset=page_number*10)
                
        next_page_url = ''
        if has_next:
            next_page_url = '/search?q=%s&page_number=%s' % (i.q, page_number + 1)
        
        sub_title = 'You searched for: %s' % i.q
        if page_number:
             sub_title += ' - Page %s' % (page_number + 1)
        
        return render.layout(
            view.list_modules(searched, next_page_url=next_page_url, sub_title=sub_title),
            title = '%s - Google Modules' % sub_title, query = i.q)

class list_by_tag:
    def GET(self, tag):
        tag = utils.url_unquote(tag)
        listed = modules.filter_by_tag(tag)

        sub_title = 'Tag: %s' % tag
        return render.layout(
            view.list_modules(listed, sub_title=sub_title),
            title = '%s - Google Modules' % sub_title)