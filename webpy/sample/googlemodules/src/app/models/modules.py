# Author: Alex Ksikes

# TODO:
# - nicer way of implementing the blacklist
# - remove __get_stars and use in templates calculated_vote
# - we may want to have a get_latest_rss

import web
from config import db

from app.models import tags
from app.models import sql_search

from app.helpers import utils

def get_latest(offset=0, limit=10):
    """Get the latest modules."""
    has_next = False
    m = list(db.select('modules', 
        what   = 'id, title, url, description, author, screenshot, datetime_created',
        where  = 'calculated_vote >= -1 and not %s' % get_blacklisted_authors_sql(),
        order  = 'datetime_created desc',
        offset = offset, 
        limit  = limit + 1))
    
    if len(m) > limit:
        has_next = True
    
    return m[:limit], has_next

def get_popular():
    """Get the most popular modules."""
    return db.select('modules', 
        what  = 'id, title',
        where = 'calculated_vote >= -1',
        order = 'calculated_vote desc, datetime_created desc', 
        limit = 10)
    
def get_random():
    """Get random modules."""
    return db.select('modules', 
        what  = 'id, title',
        where = 'calculated_vote >= -1',
        order = 'rand()', 
        limit = 3)

def get_related(module_id): 
    """Get a similar module."""
    module_tags = [t.tag for t in tags.get_tags(module_id)]
    
    m = web.listget(
        db.select('tags', 
            vars  = dict(id=module_id, tags=module_tags),
            what  = 'module_id',
            where = 'module_id != $id and %s' % web.sqlors("tag = ", module_tags),
            group = 'module_id having count(module_id) > 1',
            order = 'rand()'), 0, False)
    
    return m and get_module(m.module_id)
    
def get_module(id):
    """Get a specific module by its id."""
    return web.listget(
        db.select('modules', 
            vars = dict(id=id), 
            what = 'id, title, description, author, author_affiliation, title_url, \
                    author_email, render_inline, screenshot, calculated_vote, url',
            where='id = $id'), 0, False)

def get_count():
    """Get a count of all modules."""
    return int(db.query(
        'select count(*) as c from modules where not %s' % get_blacklisted_authors_sql())[0].c)
 
def search(query, offset=0, limit=10):
    return sql_search.search(query, offset, limit)
    
def filter_by_tag(tag):
    return db.select('modules as m, tags as t', 
        vars  = dict(tag=tag, _tag=tag+'s'),
        what  = 'distinct m.id, title, url, description, author, screenshot',
        where = 'm.id = module_id and (tag = $tag or tag = $_tag) and calculated_vote >= -1',
        order = 'calculated_vote desc, datetime_created desc', 
        limit = 20)

def get_from_author(author):
    return db.select('modules', 
        vars  = dict(author=author),
        what  = 'id, title, url, description, author, screenshot',
        where = 'author = $author and calculated_vote >= -1',
        order = 'calculated_vote desc, datetime_created desc')

def get_all_modules(order_by='title', offset=0, limit=50):
    order_by = dict(title='title', author='author', 
        date='datetime_created', votes='calculated_vote desc').get(order_by, 'title')
    
    has_next = False
    m = list(db.select('modules', 
        what   = 'id, title, author, calculated_vote, datetime_created',
        where  = 'calculated_vote >= -1 and not %s' % get_blacklisted_authors_sql(),
        order  = order_by, 
        offset = offset, 
        limit  = limit + 1))
    
    if len(m) > limit:
        has_next = True
    
    return m[:limit], has_next

def already_exists(url):
    return web.listget(
        db.select('modules', vars = dict(url=url), where='url = $url'), 0, False)
    
def add(module, _tags=''):
    del(module.directory_title)
    
    t = db.transaction()
    try:
        id = db.insert('modules', **module)
        tags.add(id, _tags)
    except:
        t.rollback()
        raise
    else:
        t.commit()

def is_banned_site(module_url):
    utils.is_blacklisted(module_url, open('data/banned-sites.dat'))
    
def get_blacklisted_authors_sql():
    return web.sqlors('author=', [w.strip() for w in open('data/blacklist-authors.dat', 'U')])