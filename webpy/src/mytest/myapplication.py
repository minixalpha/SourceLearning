#!/usr/bin/env python
#coding: utf-8

# My Test Case of web.application
# mywebtest module should import before myweb to set path

import unittest
import mywebtest
import web

urls = ('/hello', 'hello')
app = web.application(urls, locals())
str = ''

class hello:
    def GET(self):
        web.ctx.str += 'x'
        return web.ctx.str

def before():
    web.ctx.str = 'y'

def after():
    web.ctx.str += 'z'
    global str
    str = web.ctx.str


class TestApplication(unittest.TestCase):
    def test_init_mapping(self):
        app = web.application()
        urls = (
                '/hello', 'hello',
                '/world', 'world')
        app.init_mapping(urls)
        self.assertEqual(
                app.mapping,
                [['/hello', 'hello'], ['/world', 'world']]
                )

    def test_hook(self):
        app.add_processor(web.loadhook(before))
        app.add_processor(web.unloadhook(after))
       
        self.assertEqual(app.request('/hello').data, 'yx')
        global str
        self.assertEqual(str, 'yxz')

if __name__ == '__main__':
    mywebtest.main()
