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

看web目录下的test.py文件，果然发现了main函数
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

果然是运行修改后的函数

## requirements.txt

requirements.txt 文件可由 pip 生成：

    $pip freeze -l > requirements.txt

同时，pip 可以使用 requirements.txt 文件安装依赖包

    $pip install -r requirements.txt

这就为打包与安装包提供了方便

## 分模块测试

### application.py

### browser.py

### db.py

### doctests.py

### session.py

