# Author: Alex Ksikes

import web

from app.helpers import utils
from app.helpers import formatting

# connect to database
db = web.database(dbn='mysql', db='dbname', user='user', passwd='passwd', charset=None)

# in development debug error messages and reloader
web.config.debug = True

# in develpment template caching is set to false
cache = False

# template global functions
globals = utils.get_all_functions(formatting)

# set global base template
view = web.template.render('app/views', cache=cache, globals=globals)

# in production the internal errors are emailed to us
web.config.email_errors = ''