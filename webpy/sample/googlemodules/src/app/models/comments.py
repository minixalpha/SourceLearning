# Author: Alex Ksikes 

import web
from config import db

from app.helpers import utils

def get_latest():
    """Get latest comments on modules."""
    return db.select('comments', 
        what  = 'content, module_id',
        order = 'datetime_created desc', 
        limit = 4)

def get_comments(module_id):
    return db.select('comments', 
        vars  = dict(id=module_id),
        what  = 'datetime_created, author, content',
        where = 'module_id=$id')

def add(module_id, author, comment):
    success, err_msg = False, ''
    
    banned_word = is_banned_keyword(author + ' ' + comment)
    if banned_word:
        err_msg = 'Ooops! Please go back to remove "%s" if you can...' % banned_word
    
    elif module_id and author and comment:
        db.insert('comments',
            module_id=module_id, author=author, content=comment, 
            datetime_created=web.SQLLiteral('now()'))
        success = True
        
    return success, err_msg

def get_latest_for_author(author):
    return db.select('modules as m, comments as c', 
        vars = dict(author=author),
        what  = 'm.title as module_title, c.author, content, module_id',
        where = 'm.id = module_id and m.author = $author and calculated_vote >= -1',
        order = 'c.datetime_created desc',
        limit = 3)

def is_banned_keyword(text):
    return utils.is_blacklisted(text, open('data/blacklist.dat'))
