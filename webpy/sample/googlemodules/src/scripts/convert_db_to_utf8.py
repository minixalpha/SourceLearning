# Author: Alex Ksikes

# For GoogleModules run as:
# python convert_db_to_utf8.py googlemodules user passwd modules tags comments forum_treads

import web, sys

def run(db_name, user, passwd, tables):
    db = web.database(dbn='mysql', db=db_name, user=user, passwd=passwd, charset=None)
    db_utf8 = web.database(dbn='mysql', db=db_name, user=user, passwd=passwd)
    db.printing = db_utf8.printing = False

    for table in tables:
        print '#' * 20 + table + '#' * 20
        db.query('alter table %s convert to character set utf8' % table)

        for i, m in enumerate(db.select(table)):
            if i % 100 == 0: print i
        
            for k, v in m.items():
                db_utf8.update(table, where='id=%s' % m.id, **m)
            
            
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python convert_db_to_utf8.py db_name user passwd tables"
    else:
        run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])