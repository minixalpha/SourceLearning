#!/usr/bin/env python
#coding: utf-8

# Demo of WSGI Server


def run(application):
    # environ must be a Python dict object
    environ = {}
    cur_response_headers = []

    # set environ
    def write(data):
        pass

    def _response_headers_legal(response_headers):
        return True

    def start_response(status, response_headers, exc_info=None):
        if _response_headers_legal(response_headers):
            pass

        cur_response_headers = response_headers

        return write

    try:
        result = application(environ, start_response)
    finally:
        if hasattr(result, 'close'):
            result.close()

    if hasattr(result, '__len__'):
        # result must be accumulated
        pass


    for data in result:
        write(data)
