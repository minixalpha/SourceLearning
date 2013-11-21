# Author: Alex Ksikes 

import web

import random
        
def get_pub_id():
    pub_ids = dict(alex = 'pub-1431948349807205', philipp = 'pub-4135663670627621')
    return pub_ids.values()[random.randint(0,1)]

def get_credits():
    credits = (web.storage(name='Philipp Lenssen', homepage='http://blogoscoped.com'), 
               web.storage(name='Alex Ksikes', homepage='http://alex.ksikes.net'))
    return random.sample(credits, 2)