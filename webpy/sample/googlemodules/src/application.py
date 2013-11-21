#!/usr/bin/env python
# Author: Alex Ksikes 

# TODO: 
# - setup SPF for sendmail and 
# - emailerrors should be sent from same domain
# - clean up schema.sql
# - because of a bug in webpy unicode search fails (see models/sql_search.py)

import web
import config
import app.controllers

from app.helpers import custom_error

import forum

urls = (        
    # front page
    '/',                                    'app.controllers.base.index',
    '/page/([0-9]+)/',                      'app.controllers.base.list',
    
    # view, add a comment, vote
    '/module/([0-9]+)/',                    'app.controllers.module.show',
    '/module/([0-9]+)/comment/',            'app.controllers.module.comment',
    '/module/([0-9]+)/vote/',               'app.controllers.module.vote',
    
    # submit a module
    '/submit/',                             'app.controllers.submit.submit',
    
    # view author page
    '/author/(.*?)/',                       'app.controllers.author.show',                      
    
    # search browse by tag name
    '/search/',                             'app.controllers.search.search',                             
    '/tag/(.*?)/',                          'app.controllers.search.list_by_tag',
    
    # view tag clouds
    '/tags/',                               'app.controllers.cloud.tag_cloud',
    '/authors/',                            'app.controllers.cloud.author_cloud',
    
    # table modules
    '/modules/(?:by-(.*?)/)?([0-9]+)?/?',   'app.controllers.all_modules.list_by',
    
    # static pages
    '/feedback/',                           'app.controllers.feedback.send',
    '/about/',                              'app.controllers.base.about',
    '/help/',                               'app.controllers.base.help',
    
    # let lighttpd handle in production
    '/(?:css|img|js|rss)/.+',               'app.controllers.public.public',
    
    # canonicalize /urls to /urls/
    '/(.*[^/])',                            'app.controllers.public.redirect',

    # mini forum app
    '/forum',                               forum.app,    

    '/hello/(.*)',                            'hello',
    
    # site admin app
#    '/admin',                              admin.app,    
)

app = web.application(urls, globals())
custom_error.add(app)

if __name__ == "__main__":
    app.run()
