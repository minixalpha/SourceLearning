#!/usr/bin/env python
#coding: utf-8

# Demo of middleware in WSGI


# URL Routing middleware
def urlrouting(url_app_mapping):
    def midware_app(environ, start_response):
        url = environ['PATH_INFO']
        app = url_app_mapping[url]

        result = app(environ, start_response)
        return result

    return midware_app
