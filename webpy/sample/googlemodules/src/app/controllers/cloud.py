# Author: Alex Ksikes 

import web

from app.models import tags

from app.helpers import render
from config import view

class tag_cloud:
    def GET(self):
        cloud = tags.get_tag_cloud()
        return render.layout(view.tag_cloud(cloud), title = 'All Tags')

class author_cloud:
    def GET(self):
        cloud = tags.get_author_cloud()
        return render.layout(view.tag_cloud_author(cloud), title = 'All Authors')
