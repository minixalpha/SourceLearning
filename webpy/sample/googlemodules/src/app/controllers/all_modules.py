# Author: Alex Ksikes 

import web

from app.models import modules

from app.helpers import render
from config import view

class list_by:
    def GET(self, order_by='title', page_number='1'):
        if not order_by: order_by = ''
        
        page_number = web.intget(page_number, 0)

        m, has_next = modules.get_all_modules(order_by, offset=page_number*50)

        next_page_url = ''
        if has_next:
            if not order_by:
                next_page_url = '/modules/%s/' % (page_number + 1)
            else:
                next_page_url = '/modules/by-%s/%s/' % (order_by, page_number + 1)
        sub_title = 'Page %s' % (page_number + 1)
        
        return render.layout(
            view.all_modules(m, modules.get_count(), order_by, next_page_url, sub_title=sub_title),
            title = 'All modules - %s - Google Modules' % sub_title,
            mode = 'modeAllModules')
