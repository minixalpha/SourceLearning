# Author: Alex Ksikes 

import web
from config import db

def add(module_id, vote, user_ip):
    if already_voted(module_id, user_ip):
        success = True
    else:
        success = False
        if module_id and -5 <= vote <= 5:
            db.insert('votes',
                module_id=module_id, vote=vote, ip=user_ip,
                datetime_created=web.SQLLiteral('now()'))
            success = True
        update_calculated_vote(module_id)
    return success

def update_calculated_vote(module_id):
    min_votes = 5
    r = web.listget(
        db.select('votes',
            vars = dict(id=module_id),
            what = 'sum(vote) / count(module_id) as calculated_vote', 
            where = 'module_id = $id',
            group = 'module_id having count(module_id) > %s' % min_votes), 0, False)
    
    if r:
        db.update('modules', 
            vars = dict(id=module_id),
            where='id = $id',    
            calculated_vote=r.calculated_vote)

def already_voted(module_id, user_ip):
    return web.listget(
        db.select('votes',
            vars = dict(ip=user_ip, id=module_id),
            what = 'count(vote)', 
            where = 'ip = $ip and module_id = $id',
            group = 'module_id having count(module_id) > 0'), 0, False)