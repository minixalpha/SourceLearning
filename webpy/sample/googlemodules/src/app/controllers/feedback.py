# Author: Alex Ksikes 

import web

from app.models import modules

from app.helpers import render
from config import view
        
class send:
    def GET(self):
        return render.layout(
            view.feedback(), title='Feedback - Google Modules')
    
    def POST(self):
        i = web.input()
        success = send_feedback(i.author_email, i.subject, i.comment)
        
        return render.layout(
            view.submitted_form(success, type='feedback'), 
            title='Feedback - Google Modules')

def send_feedback(_from, subject, message):
    to = ['alex.ksikes@gmail.com', 'philipp.lenssen@gmail.com']
    
    success = False
    if _from and message:
        web.sendmail(_from, ','.join(to), '[Google Modules] ' + subject, message)
        success = True
    return success