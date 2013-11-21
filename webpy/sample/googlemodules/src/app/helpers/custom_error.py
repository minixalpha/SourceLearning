# Author : Alex Ksikes

import web

from app.helpers import render
from config import view

def notfound():
    return web.notfound(
        render.layout(view.not_found(), title='File not found', mode='modeShow404'))

def internalerror():
    return web.internalerror(
        render.layout(view.internal_error(), title='Some error occured', mode='modeShow404'))

def add(app):
    app.notfound = notfound
    app.internalerror = web.config.debug and web.debugerror or internalerror
    if web.config.email_errors:
        app.internalerror = web.emailerrors(web.config.email_errors, app.internalerror)
