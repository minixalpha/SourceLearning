# Author: Alex Ksikes

from config import db
from app.helpers import tag_cloud

import re, sets

def get_tags(module_id):
    return db.select('tags', 
        vars  = dict(id=module_id),
        what  = 'tag',
        where = 'module_id=$id')

def get_tag_cloud():
    """Return a tag cloud of most popular modules."""
    tags = db.select('tags', 
        what  = 'tag, count(tag) as count',
        where = 'length(tag) >= 2',
        group = 'tag having count >= 4',
        limit = 10000)
    
    return tag_cloud.make_cloud(tags, min_tag_length=2, min_count=4, 
        max_count=12, plurial=True)

def get_author_cloud():
    """Return a tag cloud of most popular authors."""
    tags = db.select('modules', 
        what  = 'author as tag, count(author) as count',
        where = 'length(author) >= 3',
        group = 'author',
        limit = 10000)
    
    return tag_cloud.make_cloud(tags, min_tag_length=3, min_count=2, 
        max_count=17, plurial=False, randomize=True)

def add(module_id, tags):
    tags = get_nice_tags(tags)
    tags = sets.Set(tags.split())
    for tag in tags:
        db.insert('tags', module_id=module_id, tag=tag)
    
def get_nice_tags(tags):
    tags = tags.lower().strip()
    tags = re.sub('[,;\"]', ' ', tags)
    return re.sub('\s{2,}', ' ', tags)
