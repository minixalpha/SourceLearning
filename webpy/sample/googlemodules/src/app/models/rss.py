# Author: Alex Ksikes

from app.models import modules

from config import view

def update_rss():
    latest_modules, has_next = modules.get_latest(limit=20)
    open('public/rss/latest.xml', 'w').write(unicode(view.rss(latest_modules)).encode('utf-8'))
