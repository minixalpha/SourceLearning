import config

def listing(**k):
    return config.DB.select('items', **k)
