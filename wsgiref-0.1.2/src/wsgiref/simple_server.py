#coding: utf-8

"""BaseHTTPServer that implements the Python WSGI protocol (PEP 333, rev 1.21)

This is both an example of how WSGI can be implemented, and a basis for running
simple web applications on a local machine, such as might be done when testing
or debugging an application.  It has not been reviewed for security issues,
however, and we strongly recommend that you use a "real" web server for
production use.

For example usage, see the 'if __name__=="__main__"' block at the end of the
module.  See also the BaseHTTPServer module docs for other API information.
"""

# M:
# This module implements a simple HTTP server (based on BaseHTTPServer) 
# that serves WSGI applications

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib, sys
from wsgiref.handlers import SimpleHandler
# M:
#    BaseHTTPServer: defines two classes for implementing HTTP servers 
#    (Web servers). Usually, this module isn’t used directly, but is used 
#    as a basis for building functioning Web servers.
#
#    HTTPServer: a SocketServer.TCPServer subclass, and therefore implements the 
#    SocketServer.BaseServer interface. It creates and listens at the HTTP 
#    socket, dispatching the requests to a handler. 
#
#    BaseHTTPRequestHandler: is used to handle the HTTP requests that arrive at 
#    the server. By itself, it cannot respond to any actual HTTP requests; 
#    it must be subclassed to handle each request method (e.g. GET or POST).
#
#    ref: http://docs.python.org/2/library/basehttpserver.html
#
#    urllib: This module provides a high-level interface for fetching data
#    across the World Wide Web.
#
#    ref: http://docs.python.org/2/library/urllib.html
#
#    sys: This module provides access to some variables used or maintained by 
#    the interpreter and to functions that interact strongly with the 
#    interpreter.

# M:
# __double_leading_and_trailing_underscore__: 
#    "magic" objects or attributes that live in user-controlled namespaces
#
# __all__:
#    modules should explicitly declare the names in their public API using 
#    the __all__ attribute
__version__ = "0.1"
__all__ = ['WSGIServer', 'WSGIRequestHandler', 'demo_app', 'make_server']


# M:
# >>> sys.version
# '2.7.3 (default, Sep 26 2013, 20:08:41) \n[GCC 4.6.3]'
# >>> simple_server.software_version
# 'WSGIServer/0.1 Python/2.7.3'

server_version = "WSGIServer/" + __version__
sys_version = "Python/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version


# M:
#        +-------------+
#        | BaseHandler |   start_response(status, headers, exc_info)
#        +-------------+
#               |
#               V
#       +----------------+
#       | SimpleHandler  |
#       +----------------+
#               |
#               V
#       +---------------+
#       | ServerHandler |
#       +---------------+
# 
class ServerHandler(SimpleHandler):

    server_software = software_version

    def close(self):
        # M:
        # S.split([sep [,maxsplit]]) -> list of strings
        # >>> status
        # '200 OK'
        # >>> status.split(' ', 0)
        # ['200 OK']
        # >>> status.split(' ', 1)
        # ['200', 'OK']
        # >>> status.split(' ', 2)
        # ['200', 'OK']


        # In WSGIRequestHandler.handle
        # handler.request_handler = self

        # WSGIRequestHandler.log_request 
        # -> BaseHTTPRequestHandler.log_request
        # -> BaseHTTPRequestHandler.log_message
        # -> sys.stderr.write


        # SimpleHandler.close
        # -> BaseHandler.close

        try:
            self.request_handler.log_request(
                self.status.split(' ',1)[0], self.bytes_sent
            )
        finally:
            SimpleHandler.close(self)


# M:
#         +------------+
#         | BaseServer |
#         +------------+
#               |
#               V
#         +------------+
#         | TCPServer  |
#         +------------+
#               |
#               V
#         +------------+
#         | HTTPServer |
#         +------------+
#               |
#               V
#         +------------+
#         | WSGIServer |
#         +------------+
class WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""

    application = None

    def server_bind(self):
        """Override server_bind to store the server name."""

        # M: -> TCPServer.server_bind
        HTTPServer.server_bind(self)

        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        return self.application

    def set_app(self,application):
        self.application = application

# M:
#         +--------------------+
#         | BaseRequestHandler |
#         +--------------------+
#                   |
#                   V
#         +-----------------------+
#         | StreamRequestHandler  |
#         +-----------------------+
#                   |
#                   V
#         +------------------------+
#         | BaseHTTPRequestHandler |
#         +------------------------+
#                   |
#                   V
#         +--------------------+
#         | WSGIRequestHandler |
#         +--------------------+

class WSGIRequestHandler(BaseHTTPRequestHandler):

    server_version = "WSGIServer/" + __version__

    def get_environ(self):
        # M: self.server is instance of WSGIServer, init in 
        # BaseRequestHandler's __init__

        # M: copy return a shallow copy of base_environ, 
        # give each request handler a unique env

        # M: deepcopy return a deep copy
        env = self.server.base_environ.copy()

        # M: request_version is like 'HTTP/1.0' 
        env['SERVER_PROTOCOL'] = self.request_version
        
        # M: command is a (case-sensitive) keyword such as GET or POST
        env['REQUEST_METHOD'] = self.command

        # M: <path> is encoded using the URL encoding scheme 
        # (using %xx to signify the ASCII character with hex code xx).

        # M: if url is http://localhost:8080/xyz?abc
        # path is '/xyz', query is 'abc'
        if '?' in self.path:
            path, query = self.path.split('?', 1)
        else:
            path, query = self.path, ''

        # M: urllib.unquote('/%7Econnolly/') yields '/~connolly/'
        env['PATH_INFO'] = urllib.unquote(path)

        env['QUERY_STRING'] = query

        # M: address_string return client address
        # M: env['REMOTE_HOST'] is like 'localhost'
        # M: env['REMOTE_ADDR'] is like '127.0.0.1'
        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host

        # M: client_address is the client IP address in the form (host,port)
        env['REMOTE_ADDR'] = self.client_address[0]

        # M: env['CONTENT_TYPE'] may be 'text/plain'
        # M: self.headers is an instance of mimetools.Message,
        # which is a subclass of rfc822.Message
        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader

        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        # M:

        # self.headers:
        #     Host: localhost:8000
        #     Connection: keep-alive
        #     Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
        #     User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36
        #     Accept-Encoding: gzip,deflate,sdch
        #     Accept-Language: en-US,en;q=0.8,zh;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2

        # self.headers.headers:
        #     ['Host: localhost:8000\r\n', 
        #     'Connection: keep-alive\r\n', 
        #     'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n', 
        #     'User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36\r\n', 
        #     'Accept-Encoding: gzip,deflate,sdch\r\n', 
        #     'Accept-Language: en-US,en;q=0.8,zh;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2\r\n']

        # after loop, in env:
        #     env[HTTP_ACCEPT] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        #     env[HTTP_ACCEPT_ENCODING] = 'gzip,deflate,sdch'
        #     env[HTTP_ACCEPT_LANGUAGE] = 'en-US,en;q=0.8,zh;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2'
        #     env[HTTP_CONNECTION] = 'keep-alive'
        #     env[HTTP_HOST] = 'localhost:8000'
        #     env[HTTP_USER_AGENT] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'

        for h in self.headers.headers:
            k, v = h.split(':', 1)
            k = k.replace('-', '_').upper()
            v = v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        return env

    def get_stderr(self):
        # M:
        # usage:
        # print >> sys.stderr, 'error msg'

        # why:
        # The advantages of using sys.stderr for errors instead of sys.stdout are:
        #     * If the user redirected stdout to a file, she still sees errors on 
        #     the screen.
        #     * It's not buffered, so if sys.stderr is redirected to a log file 
        #     there are less chance that the program may crash before the error 
        #     was logged.

        return sys.stderr

    def handle(self):
        """Handle a single HTTP request"""

        # M: rfile is a file object open for reading positioned at the
        # start of the optional input data part;

        # M: request, client_address = socket.accept()
        # M: connection = request
        # M: rfile = connection.makefile('rb', self.rbufsize)

        self.raw_requestline = self.rfile.readline()

        
        # M: invoke BaseHTTPRequestHandler.parse_request(), parse raw_requestline
        if not self.parse_request(): # An error code has been sent, just exit
            return

        # M: invoke SimpleHandler.__init__
        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self      # backpointer for logging

        # M: invoke BaseHandler.run
        handler.run(self.server.get_app())


def demo_app(environ,start_response):
    # M: StringIO reads and writes a string buffer (also known as memory files).

    from StringIO import StringIO
    stdout = StringIO()
    print >> stdout, "Hello world!"
    print >> stdout

    h = environ.items()
    h.sort()
    for k,v in h:
        print >> stdout, k,'=',`v`

    start_response("200 OK", [('Content-Type','text/plain')])

    return [stdout.getvalue()]


def make_server(
    host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
):
    """Create a new WSGI server listening on `host` and `port` for `app`"""

    # M: -> HTTPServer.__init__
    #    -> TCPServer.__init__
    #       -> TCPServer.server_bind
    #           -> TCPServer.socket.bind
    #       -> TCPServer.server_activate
    #           -> TCPServer.socket.listen
    server = server_class((host, port), handler_class)

    # M: conresponding to WSGIRequestHandler.handle()
    #    -> handler.run(self.server.get_app())
    server.set_app(app)

    return server


if __name__ == '__main__':
    httpd = make_server('', 8000, demo_app)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."

    # M: webbrowser provides a high-level interface to allow displaying Web-based documents 
    # to users. Under most circumstances
    import webbrowser
    webbrowser.open('http://localhost:8000/xyz?abc')

    httpd.handle_request()  # serve one request, then exit
