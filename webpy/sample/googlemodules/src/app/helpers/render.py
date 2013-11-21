# Author: Alex Ksikes 

import web

from app.models import modules
from app.models import comments

from config import view

import random

def layout(page, **kwargs):
    popular = modules.get_popular()
    _random = modules.get_random()
    latest_comments = comments.get_latest()
    by = random.sample(['Ksikes', 'Lenssen'], 2)
    return view.layout(page, popular, _random, latest_comments, by, **kwargs)