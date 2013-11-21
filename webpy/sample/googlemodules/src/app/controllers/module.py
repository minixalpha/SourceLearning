# Author: Alex Ksikes 

import web

from app.models import modules
from app.models import tags
from app.models import comments
from app.models import votes
from app.models import submission
from app.models import rss

from app.helpers import render
from app.helpers import misc
from app.helpers import utils

from config import view

def module_must_exist(meth):
    def new(self, module_id):
        if not modules.get_module(module_id):
            return render.layout('')
        else:
            return meth(self, module_id)
    return new

class show:
    @module_must_exist
    def GET(self, module_id):
        module = modules.get_module(module_id)
        _tags = tags.get_tags(module_id)
        _comments = comments.get_comments(module_id)
        related_module = modules.get_related(module_id)
    
        return render.layout(view.show_module(module, _tags, _comments, related_module, misc.get_pub_id()), 
            title=module.title + ' - Google Modules')

class comment:
    def POST(self, module_id):
        i = web.input(comment='', author='')
        success, err_msg = comments.add(module_id, i.author, i.comment)
        
        return render.layout(view.submitted_form(success, module_id, 'comment', err_msg=err_msg), 
            title='Submit Comment - Google Modules')

class vote:
    def POST(self, module_id):
        i = web.input(vote='').vote
        success = votes.add(module_id, web.intget(i, 0), utils.get_user_ip())
        
        return render.layout(view.submitted_form(success, module_id, 'vote'), 
            title='Submit Vote - Google Modules')
