import web

db = web.database(dbn='mysql', db='todo', user='root', pw="7102155")

def get_todos():
    return db.select('todo', order='id')

def new_todo(text):
    db.insert('todo', title=text)

def del_todo(id):
    db.delete('todo', where="id=$id", vars=locals())
