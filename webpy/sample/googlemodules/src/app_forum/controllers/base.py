# Author: Alex Ksikes 

import web
import config

from app_forum.models import threads
from app.helpers import render

view = web.template.render('app_forum/views', cache=config.cache, globals=config.globals)

class index:
    def GET(self):
        latest_posts, has_next = threads.get_latest()
        return render.layout(
            view.list_threads(latest_posts, next_page_url='page/1/', sub_title='Share your thoughts'),
            title = 'Discuss - Google Modules', mode = 'modeForum')

class list:
    def GET(self, page_number):
        page_number = int(page_number)

        latest_posts, has_next = threads.get_latest(offset=page_number*20)
        
        next_page_url = ''
        if has_next:
            next_page_url = 'page/%s/' % (page_number + 1)
        
        sub_title = 'Share your thoughts'
        if page_number:
             sub_title += ' - Page %s' % (page_number + 1)
        
        return render.layout(
            view.list_threads(latest_posts, next_page_url=next_page_url, sub_title=sub_title),
            title = 'Discuss - Google Modules', mode = 'modeForum')

class show:
    def GET(self, thread_id):
        thread = threads.get_thread(thread_id)
        conversation = threads.get_conversation(thread_id)
        
        return render.layout(view.show_thread(thread, conversation), 
            title=thread.title + ' - Forum - Google Modules', mode = 'modeForum')

class new:
    def POST(self):
        i = web.input(author='', title='', content='')
        success = threads.add(i)
        
        return render.layout(view.submitted_form(success),
            title='Saving Post - Google Modules', mode = 'modeForum')

class reply:
    def POST(self, thread_id):
        i = web.input(reply_to='', author='', content='')
        success = threads.reply(i)
        
        return render.layout(view.submitted_form(success),
            title='Saving Post - Google Modules', mode = 'modeForum')
