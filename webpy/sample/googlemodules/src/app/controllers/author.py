# Author: Alex Ksikes 

import web

from app.models import modules
from app.models import comments

from app.helpers import render
from config import view

import urllib

class show:
    def GET(self, author_name):
        author_name = urllib.unquote_plus(author_name)
        all_modules = modules.get_from_author(author_name)
        latest_comments = comments.get_latest_for_author(author_name)
        
        return render.layout(
            view.list_modules_by_author(all_modules, latest_comments, author_name),
            title='Modules by %s - Google Modules' % author_name, mode='modeViewAuthor')
