# Author: Alex Ksikes 

import web
import config

from app.models import submission
from app.models import rss

from app.helpers import render
from config import view

class submit:
    def GET(self):
        return render.layout(view.submit_module(), 
            title='Submit - Google Modules')

    def POST(self):
        i = web.input(url='', tags='', _unicode=False)
        success, err_msg = submission.submit(i.url, i.tags)
        rss.update_rss()
        
        return render.layout(view.submitted_form(success, type='submit', err_msg=err_msg), 
            title='Submit - Google Modules')