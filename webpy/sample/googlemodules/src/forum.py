#!/usr/bin/env python
# Author: Alex Ksikes 

import web
import config
import app_forum.controllers

from app.helpers import custom_error

urls = (
    '/',                             'app_forum.controllers.base.index',
    '/new/',                         'app_forum.controllers.base.new',
    '/page/([0-9]+)/',               'app_forum.controllers.base.list',
    '/thread/([0-9]+)/',             'app_forum.controllers.base.show',
    '/thread/([0-9]+)/reply/',       'app_forum.controllers.base.reply',
)

app = web.application(urls, globals())
custom_error.add(app)

if __name__ == "__main__":
    app.run()
