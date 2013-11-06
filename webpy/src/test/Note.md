# 目录文件说明

## README

如何运行测试文件，包含全部测试及分模块测试

调用

    $ python test/alltests.py

运行全部测试

调用

    $ python test/db.py

运行db模块测试

## alltest.py

运行全部测试入口，调用 `webtest` 模块完成测试

```python
# alltest.py

if __name__ == "__main__":
    webtest.main()
```

## webtest.py

我们发现 webtest.py 中并没有 main 函数，而是从 `web.test` 中导入，

```python
# webtest.py
from web.test import *
```

也就是说，如果 `web.test`中有main函数的话，`webtest.main()`
其实是调用 `web.test` 中的main函数。

感觉～ 好神奇

## web.test

看web目录下的test.py文件，果然发现了main函数，终于找到入口啦~

```python
def main(suite=None):
    if not suite:
        main_module = __import__('__main__')
        # allow command line switches
        args = [a for a in sys.argv[1:] if not a.startswith('-')]
        suite = module_suite(main_module, args or None)

    result = runTests(suite)
    sys.exit(not result.wasSuccessful())
```

把这个main函数改掉，再运行一下：

    $ python test/alltests.py

果然是运行修改后的函数，所以这里确定是入口。

在进入下一步之前，我们需要学习一下Python自动单元测试框架，即`unittest`模块。关于 `unittest` ，可以参考这篇文章：
[Python自动单元测试框架](http://www.ibm.com/developerworks/cn/linux/l-pyunit/)


现在，进入 `web.test.main`，
当我们如果我们打印 `main_module`，会得到

    <module '__main__' from 'test/alltests.py'>

这说明调用时，`import` 得到的 `main` 与命令行调用指定的
调用的模块一致。

之后会调用 `module_suite` 得到需要测试的模块,

我们看一下 `module_suite` 的代码，

```python
def module_suite(module, classnames=None):
    """Makes a suite from a module."""
    if classnames:
        return unittest.TestLoader().loadTestsFromNames(classnames, module)
    elif hasattr(module, 'suite'):
        return module.suite()
    else:
        return unittest.TestLoader().loadTestsFromModule(module)
```

可以看出，module_suite分三部分，如果定义了 `classnames`，
会测试具体的类，否则，如果 `module` 中含有 `suite` 函数，
就返回此 `module.suite()` 的调用结果。

此时我们的 `module` 是之前得到的 

    <module '__main__' from 'test/alltests.py'>

而 `alltests.py` 中刚好就有 `suite` 函数：

```python
def suite():
    modules = ["doctests", "db", "application", "session"]
    return webtest.suite(modules)
```

`modules` 是全部模块的列表，随后以此为参数，返回
调用 `webtest.suite` 的结果。

这时候，同样的情况又出现了，`webtest.py` 中没有 `suite` 函数，
但是 `webtest.py` 中含有

```python
from web.test import *
```

所以 `webtest.suite` 调用的还是 `web.test.suite`，

从这里我们可以看出，

> webtest.py 这个模块就是目录 `test` 下的模块与 `web.test` 模块
> 之间的一个过渡层，`test` 目录下的模块调用 `webtest.XXX`，而实际
> 的实现代码都是调用 `web.test.XXX`，所以，我们再次回到 `web.test`。

看看 `web.test.suite`的实现：

```python
def suite(module_names):
    """Creates a suite from multiple modules."""
    suite = TestSuite()
    for mod in load_modules(module_names):
        suite.addTest(module_suite(mod))
    return suite
```

首先调用 `TestSuite()`，即 `unittest.TestSuite()`，得到一个
`suite`。然后，向 `suite` 中添加测试用例。

参数 `module_names` 就是刚刚的列表modules：

    modules = ["doctests", "db", "application", "session"]

调用 `load_modules` 把模块名变为模块本身，
例如 "application":

    >>> __import__("application", None, None, "x")
    <module 'application' from 'application.pyc'>

然后，再调用 `module_suite`，这时候你会发现，我们递归回来了，

```python
def module_suite(module, classnames=None):
    """Makes a suite from a module."""
    if classnames:
        return unittest.TestLoader().loadTestsFromNames(classnames, module)
    elif hasattr(module, 'suite'):
        return module.suite()
    else:
        return unittest.TestLoader().loadTestsFromModule(module)
```

此时, `module`为:

    <module 'application' from 'application.pyc'>

我们再看看这时候，`application.py`中是否有 `suite`函数。
经过查看，发现没有，所以此时就会调用 `if`语句第三个分支：

```python
        return unittest.TestLoader().loadTestsFromModule(module)
```

[TestLoader](http://docs.python.org/2/library/unittest.html#unittest.TestLoader) 中的 `loadTestsFromModule` 从模块中导入
测试用例。 这个函数会搜索模块中 `TestCase`类的子类，再创建一个
子类的实例，以便调用子类中的测试函数。
例如 `test/application.py`中的 `ApplicationTest` 类：

```python
class ApplicationTest(webtest.TestCase):
    def test_reloader(self):
        write('foo.py', data % dict(classname='a', output='a'))
        import foo
        app = foo.app
        
        self.assertEquals(app.request('/').data, 'a')
        
        # test class change
        time.sleep(1)
        write('foo.py', data % dict(classname='a', output='b'))
        self.assertEquals(app.request('/').data, 'b')

        # test urls change
        time.sleep(1)
        write('foo.py', data % dict(classname='c', output='c'))
        self.assertEquals(app.request('/').data, 'c')
        
    def testUppercaseMethods(self):
        urls = ("/", "hello")
        app = web.application(urls, locals())
        class hello:
            def GET(self): return "hello"
            def internal(self): return "secret"
            
        response = app.request('/', method='internal')
        self.assertEquals(response.status, '405 Method Not Allowed')

     ...
```

返回的这些函数会经过 `web.test.suite` 中的 `suite.addTest` 加入到
`suite`中。 这样经过循环，所有模块中的测试用例就加入 `suite`中。

之后，我们回到 `web.test.main` 中，调用

```python
result = runTests(suite)
```

完成最终的测试。 `runTests` 在 `web.test`模块中：

```python
def runTests(suite):
    runner = unittest.TextTestRunner()
    return runner.run(suite)
```

`runner`功能同样由 `unittest`模块提供。

到这里，我们应该明白了测试的整个过程的全部细节。

这里，我们对 `alltests.py` 完成的功能做一个总结。
从总体上看，`alltests.py`对所有模块完成测试,包括：

```
    modules = ["doctests", "db", "application", "session"]
```

我们绕来绕去，其实不过下列过程：

* 通过 `suite=TestSuite()` 得到 `suite`
* 把所有模块中的 test 函数  通过 `suite.addTest()` 加入 `suite`
* 通过 `runner=unittest.TextTestRunner()` 得到 `runner`
* 运行 `runner.run(suite)` 调用所有测试用例。

之所以感觉绕，是因为 层次关系，及`alltests.py` 需要递归调用 `module_suite`:

* `alltests.py` 调用 `webtest.main`
* `webtest.main` 指向 `web.test.main` 
* 由`web.test.main` 进入 `web.test.module_suite`，进入 `if` 第二分支
* 再进入 `alltest.py`，调用 `suite()`
* 再进入 `web.test.suite` , 对每个模块调用 `web.test.module_suite`
* 再进入 `web.test.module_suite`，进入 `if` 第三分支,得到每个模块中的 测试用例
* 将所有测试用例加入 `suite()` 中的 `suite`


## requirements.txt

requirements.txt 文件可由 pip 生成：

    $pip freeze -l > requirements.txt

同时，pip 可以使用 requirements.txt 文件安装依赖包

    $pip install -r requirements.txt

这就为打包与安装包提供了方便

## 分模块测试

### application.py

对 web.py 应用的一个测试，会生成一个 foo.py 文件

```python
import web

urls = ("/", "c")
app = web.application(urls, globals(), autoreload=True)

class c:
    def GET(self):
        return "c"

```

程序入口依然会调用 `webtest.main()`

```python
if __name__ == '__main__':
    webtest.main()
```

再仔细观察 `webtest.main` 调用的 `web.test` 中的 `main`函数

```python
def main(suite=None):
    if not suite:
        main_module = __import__('__main__')
        # allow command line switches
        args = [a for a in sys.argv[1:] if not a.startswith('-')]
        suite = module_suite(main_module, args or None)

    result = runTests(suite)
    sys.exit(not result.wasSuccessful())
```

回顾一下 `module_suite`函数，

```python
def module_suite(module, classnames=None):
    """Makes a suite from a module."""
    if classnames:
        return unittest.TestLoader().loadTestsFromNames(classnames, module)
    elif hasattr(module, 'suite'):
        return module.suite()
    else:
        return unittest.TestLoader().loadTestsFromModule(module)
```

与 `alltests.py` 不同，`application.py`中并没有 `suite`，
所以直接进入第三分支。后面的流程就和之前讲的后半部分一致了。

这里，我们主要集中于 `application.py`中的具体内容。

* 1. test_reloader(self)

```python
def test_reloader(self):
    write('foo.py', data % dict(classname='a', output='a'))
    import foo
    app = foo.app
    
    self.assertEquals(app.request('/').data, 'a')
    
    # test class change
    time.sleep(1)
    write('foo.py', data % dict(classname='a', output='b'))
    self.assertEquals(app.request('/').data, 'b')

    # test urls change
    time.sleep(1)
    write('foo.py', data % dict(classname='c', output='c'))
    self.assertEquals(app.request('/').data, 'c')
```

首先使用 `write` 生成了一个 `foo.py` 程序:

```python
        write('foo.py', data % dict(classname='a', output='a'))
```

write 源代码:

```python
def write(filename, data):
    f = open(filename, 'w')
    f.write(data)
    f.close()
```

data 定义:
```python
data = """
import web

urls = ("/", "%(classname)s")
app = web.application(urls, globals(), autoreload=True)

class %(classname)s:
    def GET(self):
        return "%(output)s"

"""
```

`data` 相当于一个小型 web 程序的模板，类名和返回值由
一个 `dict` 指定，生成一个字符串，由 `write` 生成文件。 

下面是类别和返回值为 `a` 时的 `foo.py`

```python
import web

urls = ("/", "a")
app = web.application(urls, globals(), autoreload=True)

class a:
    def GET(self):
        return "a"
```

测试的方式采用 `TestCase` 中的 `assertEquals` 函数，比较
实际值与预测值。

```python
import foo
app = foo.app
self.assertEquals(app.request('/').data, 'a')
```

`app.request('/')` 会得到一个Storage类型的值：

    <Storage {'status': '200 OK', 'headers': {}, 'header_items': [], 'data': 'a'}>

其中的 `data` 就是 `foo.py` 中 `GET` 返回的值。 

我对这个 `app.request('/')` 是比较困惑的。以 `foo.py` 为例，
之前写程序时，一般是有一个这样的程序：

```python
import web

urls = ("/", "a")
app = web.application(urls, globals(), autoreload=True)

class a:
    def GET(self):
        return "a"

if __name__ == "__main__":
    app.run()
```

然后在浏览器中请求 `0.0.0.0:8080/` 。
而在 `request` 之前，也没看到 `run` 啊，怎么就能 `request` 回
数据呢，而且通过上述代码运行后，程序会一直运行直到手动关闭，
而 `request` 的方式则是测试完后，整个程序也结束了。

所以，下一部，想比较一下 `application.run` 和 `application.request` 的不同。

我们只看关键部分，即返回的值是如何被设值的。

在 `web.application.request` 中:

```python
def request(self, localpart='/', method='GET', data=None,
            host="0.0.0.0:8080", headers=None, https=False, **kw):

    ...

response = web.storage()
def start_response(status, headers):
    response.status = status
    response.headers = dict(headers)
    response.header_items = headers
response.data = "".join(self.wsgifunc()(env, start_response))
return response
```

上述代码中 `self.wsgifunc()(env, start_response)` 比较另人困惑，
我还以为是调用函数的新方式呢，然后看了一下 `wsgifunc` 的代码，
它会返回一个函数`wsgi`，`wsgi`以 `(env, start_response)` 为参数。
在 `wsgi` 内部，又会调用 `handle_with_processors`, `handle_with_processors` 会再调用 `handle`

```python
    def handle(self):
        fn, args = self._match(self.mapping, web.ctx.path)
        return self._delegate(fn, self.fvars, args)
```

测试了一下，`self._match()` 会得到类名, `self._delegate` 会
得到返回的字符串，即 `GET`的返回值。

进入 `self._delegate`, 会最终调用一个关键函数 `handle_class`:

```python
def handle_class(cls):
    meth = web.ctx.method
    if meth == 'HEAD' and not hasattr(cls, meth):
        meth = 'GET'
    if not hasattr(cls, meth):
        raise web.nomethod(cls)
    tocall = getattr(cls(), meth)
    return tocall(\*args)
```

参数`cls`值为`foo.a`, `meth` 会得到方法名 `GET`, 然后
`tocall` 会得到函数 `a.GET`, 至此，我们终于得以调用，
`GET`函数，得到了返回的字符串。

从整个过程可以看出，没有启动服务器的代码，只是不断地调用
函数，最终来到 `GET` 函数。


再看看 `web.application.run`:

```python
def run(self, *middleware):
    return wsgi.runwsgi(self.wsgifunc(*middleware))
```

接着，我们来到 `wsgi.runwsgi`:

```python
def runwsgi(func):
    """
    Runs a WSGI-compatible `func` using FCGI, SCGI, or a simple web server,
    as appropriate based on context and `sys.argv`.
    """
    
    if os.environ.has_key('SERVER_SOFTWARE'): # cgi
        os.environ['FCGI_FORCE_CGI'] = 'Y'

    if (os.environ.has_key('PHP_FCGI_CHILDREN') #lighttpd fastcgi
      or os.environ.has_key('SERVER_SOFTWARE')):
        return runfcgi(func, None)
    
    if 'fcgi' in sys.argv or 'fastcgi' in sys.argv:
        args = sys.argv[1:]
        if 'fastcgi' in args: args.remove('fastcgi')
        elif 'fcgi' in args: args.remove('fcgi')
        if args:
            return runfcgi(func, validaddr(args[0]))
        else:
            return runfcgi(func, None)
    
    if 'scgi' in sys.argv:
        args = sys.argv[1:]
        args.remove('scgi')
        if args:
            return runscgi(func, validaddr(args[0]))
        else:
            return runscgi(func)
    
    
    server_addr = validip(listget(sys.argv, 1, ''))
    if os.environ.has_key('PORT'): # e.g. Heroku
        server_addr = ('0.0.0.0', intget(os.environ['PORT']))
    
    return httpserver.runsimple(func, server_addr)
```

前面是对参数 `sys.argv` 分析，根据参数指定，启动相应服务，
我们的简单web程序没有参数，所以直接来到最后几行。

关键在于最后的 `return`

```python
return httpserver.runsimple(func, server_addr)
```

可以看出，这里启动了一个服务器。

再看看 `httpserver.runsimple`的代码：

```python
def runsimple(func, server_address=("0.0.0.0", 8080)):
    """
    Runs [CherryPy][cp] WSGI server hosting WSGI app `func`. 
    The directory `static/` is hosted statically.

    [cp]: http://www.cherrypy.org
    """
    global server
    func = StaticMiddleware(func)
    func = LogMiddleware(func)
    
    server = WSGIServer(server_address, func)

    if server.ssl_adapter:
        print "https://%s:%d/" % server_address
    else:
        print "http://%s:%d/" % server_address

    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        server.stop()
        server = None
```

从注释中可以看出，这里使用了 `CherryPy`中的 `WSGI server`,
启动了服务器。

```python
        server.start()
```

我们不再继续深入下去。只是直观地了解一下， `application.run`
和 `application.request` 的不同之处。

从这里我们看出了相当重要的概念 `WSGI`，以及重要的包 `CherryPy`。


### browser.py

### db.py

### doctests.py

### session.py

