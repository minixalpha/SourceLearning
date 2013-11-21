# Author: Alex Ksikes

import web
from config import db

def get_latest(offset=0, limit=20):
    has_next = False
    t = list(db.select('forum_threads', 
        what = 'id, id as idd, title, author, content, datetime_created,\
        (select count(id) from forum_threads where reply_to = idd) as no_replies,\
        (select max(datetime_created) from forum_threads where reply_to = idd) as last_reply_datetime',
        where = 'reply_to = 0',
        order  = 'datetime_created desc', 
        offset = offset, 
        limit  = limit+1))
    
    if len(t) > limit:
        has_next = True
    
    return t[:limit], has_next

def get_thread(thread_id):
    return web.listget(
        db.select('forum_threads', 
        vars = dict(id=thread_id),
        what = 'id, title, author, content, datetime_created',
        where = 'id = $id'), 0, False)

def get_conversation(thread_id):
    t = [get_thread(thread_id)]
    t.extend(
        db.select('forum_threads', 
        vars = dict(id=thread_id),
        what = 'id, title, author, content, datetime_created',
        where = 'reply_to = $id'))
    
    return t
   
def add(thread):
    success = False
        
    if thread.author and thread.title and thread.content:
        db.insert('forum_threads', **thread)
        success = True

    return success

def reply(thread):
    success = False
        
    if thread.reply_to and thread.author and thread.content:
        db.insert('forum_threads', **thread)
        success = True

    return success
