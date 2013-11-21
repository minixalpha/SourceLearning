import web
from config import db

# Does not work with unicode because of webpy bug!
# http://groups.google.com/group/webpy/browse_thread/thread/baa5b603ec9c692c#
def search(query, offset=0, limit=10):
    query = get_nice_query(query)
    
    if not query:
        return [], False
    
    def sqlands(left, lst):
        return left + (' and %s ' % left).join(lst)

    q = [str(web.sqlquote(w)) for w in query.split()]
    tag_query = web.sqlors('tag = ', q)

    q = [str(web.sqlquote('%%' + w + '%%')) for w in query.split()]
    where = []
    for c in ['title', 'url', 'description', 'author']:
        where.append(sqlands('%s like ' % c, q))
    text_query = ' or '.join(where)
    
    params = {'tag_query':tag_query, 'text_query':text_query, 
              'offset':offset, 'limit':limit+1, 'size':len(query)}
    
    m = list(db.query('\
    (select distinct m.id, title, url, description, author, screenshot, \
        calculated_vote as votes, m.datetime_created as dates \
        from modules as m left join tags as t on m.id = t.module_id \
        where %(tag_query)s \
        group by t.module_id \
        having count(t.module_id) >= %(size)d) \
    union \
    (select distinct m.id, title, url, description, author, screenshot, \
        calculated_vote as votes, m.datetime_created as dates \
        from modules as m \
        where %(text_query)s \
        order by calculated_vote desc, datetime_created desc) \
    order by votes desc, dates desc limit %(limit)d offset %(offset)d' \
    % params))
    
    has_next = len(m) > limit
    
    return m[:limit], has_next

def get_nice_query(query):
    return query.strip()

# Old SQL search which does not work with tags.
#def search(query='', table='modules', columns='title', where='', group='', order='', offset=0, limit=9):  
#    columns = 'title, url, description, author, screenshot, tag'
#    
#    for word in get_nice_query(query):
#        word = str(web.sqlquote('%%' + str(word) + '%%'))
#        where.append('( ' + (' like %s or ' % word).join(columns) + ' like %s )' % word)
#    where = ' and '.join(where)
#    
#    m = db.select(
#        'modules as m, tags as t',
#        what   = 'm.id, title, url, description, author, screenshot', 
#        where  = 'm.id = module_id and ( ' + where + ' )',
#        group  = 'module_id',
#        order  = 'calculated_vote desc',
#        offset = offset,
#        limit  = limit + 1)
#    
#    has_next = False
#    if len(m) > limit:
#        has_next = True
#    
#    return m, has_next
#
#def get_nice_query(query):
#    return query.encode('utf-8').split()