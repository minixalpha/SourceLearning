#!/usr/bin/env python
#coding: utf-8

# Demo of application in WSGI

HELLO_WORLD = b"Hello world!\n"


# callable function
def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    return [HELLO_WORLD]


# callable class
class Application:
    def __init__(self, environ, start_response):
        pass

    def __iter__(self):
        yield HELLO_WORLD


# callable object
class ApplicationObj:
    def __call__(self, environ, start_response):
        return [HELLO_WORLD]
