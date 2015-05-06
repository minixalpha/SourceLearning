# JinJa2 源代码学习

## 学习方式
从 JinJa 2.0 版本开始学习，之前的版本里有不少编译错误，测试用例也不全，可以先看比较完整的 2.0 版本，
弄清楚主要思路，再看之前的提交过程。

[JinJa 2.0](https://github.com/mitsuhiko/jinja2/releases/tag/2.0)

## 概要
### 目录概要

* artwork: logo 文件
* docs: 文档, Sphinx 写成
* examples: 示例，基本使用及性能测试及基准测试
* ext: 扩展，对 Vim, Django, InlineGettext 的支持
* jinja2: 源代码
* scripts: pylint 的代码检查配置文件 pylintrc
* tests: 测试用例
* other files
	- AUTHORS: 作者列表
	- CHANGES: 版本主要变化
	- LICENCE: 开源协议
	- THANKS: 致谢
	- TODO: 未来工作

### 源代码概要

* `__init__.py`: 主模块说明，内部功能导出
* _speedups.c: C 语言加速模块
* compiler.py: Python 代码中的编译结点，生成 Python 代码
* constants.py: 常量
* debug.py: 调试接口，定位出错的位置，内容
* defaults.py: 默认过滤器和标签
* environment.py: 保存运行时信息及解析时间选项
* exceptions: 自定义异常
* ext.py: 自定义标签，i18n扩展，缓存扩展
* filters.py: 过滤器
* lexer.py: 词法分析器
* loaders.py: 类载入器
* nodes.py: 语法解析器扩展结点
* optimizer.py：优化 AST 求值过程
* parser.py: 模板语法分析器
* runtime.py: 运行时相关
* sandbox.py: 添加沙箱层
* tests.py: 测试中要使用的函数
* utils.py: 工具函数
* visitor.py: AST 节点访问器

## 核心问题
首先是模样引擎如何解决核心问题，然后是如何支持核心特性

### 模板引擎工作原理

核心问题是，给出静态的 HTML 模板，以及变量值，生成最终返回给客户端的 HTML 文件。

html 模板
```
<html>
    Hello {{ user }}
</html>
```

变量
```
user = 'jack'
```

最终html文件

```
<html>
    Hello jack
</html>
```

如何通过 Jinja2 实现上面的效果

```
from jinja2 import Environment


print Template("""\
<html>
    Hello {{ user }}
</html>
""").render(user="jack")
```

通过上面的例子，基本上可以明白模板引擎是在做什么，下面我们看看具体是怎么完成这一功能的。

Jinja 会把 html 模板的代码编译成一段 Python 代码

```python
from __future__ import division
from jinja2.runtime import LoopContext, Context, TemplateReference, Macro, Markup, TemplateRuntimeError, missing, concat, escape, markup_join, unicode_join
name = None

def root(context, environment=environment):
    l_user = context.resolve('user')
    if 0: yield None
    yield u'<html>\n    Hello %s\n</html>' % (
        l_user, 
    )

blocks = {}
debug_info = '1=8&2=9'
```

然后调用这段 Python 代码中的 `root` 函数，其中 `context` 变量中存储着变量的值，即上面的例子中
`user="jack"` 部分。

### 模板引擎核心问题实现细节

从上面的过程我们也可以看出，问题的关键就是怎么把那段 html 模板的代码转换为 Python 代码。JinJa 使用 environment.Environment.compile 函数，将 html 代码编译成 Python  代码， 其中当然涉及编译原理的词法分析， 语法分析。我们从最简单的例子开始，逐步体会一下 JinJa 如何将包含各种语法特性的 html 模板转化成 python 代码。

html 模板源代码会依次经过 environment, parser, lexer 模块，最终的词法分析在 lexer.Lexer.tokeniter 函数中完成，它的功能就是将 html 模板源代码转化成 token 流，token 有不同的类型。

最简单的只包含一个变量的模板开始。

```html
<html>
    Hello {{ user }}
</html>
```

这段 html 模板构成的 token 流即为：

```
('<html>\n    Hello ', 'data'), 

('{{', 'variable_begin'), 

(' ', 'whitespace'),

('user', 'name'), 

(' ', 'whitespace'), 

('}}', 'variable_end'), 

('\n</html>', 'data')
```

每个 token 都由 (值，类型) 构成。

而 parser 模块会使用 lexer 模块得到的 token 流，进行语法分析，生成抽象语法树(AST)，并返回。语法分析部分最终在 parser.Parser.subparse 函数中完成。语法分析的最终结果得到了：

```python
[Output(nodes=[
                TemplateData(data=u'<html>\n    Hello '), 
                Name(name='user', ctx='load'), 
                TemplateData(data=u'\n</html>')
              ]
        )
]
```

然后environment.Environment.compile 函数再使用 compiler.generate 函数将 AST 转化为 Python 代码。转化为 Python 代码的最终函数为 compiler.CodeGenerator.visit_Template 函数。生成的 Python 代码即为：

```python
from __future__ import division
from jinja2.runtime import LoopContext, Context, TemplateReference, Macro, Markup, TemplateRuntimeError, missing, concat, escape, markup_join, unicode_join
name = None

def root(context, environment=environment):
    l_user = context.resolve('user')
    if 0: yield None
    yield u'<html>\n    Hello %s\n</html>' % (
        l_user, 
    )

blocks = {}
debug_info = '1=8&2=9'
```

前面几行是共用的，直接输出即可。

下面这行 

```python
l_user = context.resolve('user')
```

通过 compiler.CodeGenerator.pull_locals 函数生成，如果发现 nodes 中有未定义的变量，就会使用 context 
来解析，context 中就包含有 Template.render(user='jack') 中的 {'user': 'jack'} 信息。

后面使用 `yield` 的那几行，在 `compiler.CodeGenerator.visit_Output` 中生成。它会依次访问 nodes 中的结点，生成相应的 python 代码。nodes 就是刚才语法分析生成的Output 中的 nodes：

```python
[Output(nodes=[
                TemplateData(data=u'<html>\n    Hello '), 
                Name(name='user', ctx='load'), 
                TemplateData(data=u'\n</html>')
              ]
        )
]
```

TemplateData 类型的数据会直接进行拼接，Name 类型的会转化成类似 ` ' %s ' % (luser) ` 的形式。

上面的例子只包含变量，下面我们看一下添加语法特性后的例子。

这个例子中包含了变量及 if 语句。

完整示例:

```python
from jinja2 import Template


print Template("""\
<html>
    {% if foo %}
        is foo
    {% else %}
        bar
    {% endif %}
</html>
""").render(foo = True)
```

运行这个 python 程序，会输出：

```
<html>
    
        is foo
    
</html>
```

在这个例子中， html 模板是：

```html
<html>
    {% if foo %}
        is foo
    {% else %}
        bar
    {% endif %}
</html>
```

生成的 python 代码是：

```python
from __future__ import division
from jinja2.runtime import LoopContext, Context, TemplateReference, Macro, Markup, TemplateRuntimeError, missing, concat, escape, markup_join, unicode_join
name = None

def root(context, environment=environment):
    l_foo = context.resolve('foo')
    if 0: yield None
    yield u'<html>\n    '
    if l_foo:
        if 0: yield None
        yield u'\n        is foo\n    '
    else:
        if 0: yield None
        yield u'\n        bar\n    '
    yield u'\n</html>'

blocks = {}
debug_info = '1=8&2=9&4=14&6=15'
```

我们可以清楚的看出，模板中的 if 语句就是被转化成了 python 中的 if 语句。对 html 的词法分析得到的 token 流为：

```
('<html>\n ', 'data'),

('{%', 'block_begin'),

(' ', 'whitespace'),

('if', 'name'),

(' ', 'whitespace'),

('foo', 'name'),

(' ', 'whitespace'),

('%}', 'block_end'),

('\n        is foo\n    ', 'data'),

...

```

注意词法分析和语法分析并非独立进行，而是边语法分析，边词法分析，语法分析分析需要 token 时，就从 token 流中获取一个，如何获取是词法分析的事，获取之后用来做什么则由语法分析决定。语法分析最终得到：

```
[
    Output(nodes=[TemplateData(data=u'<html>\n    ')]), 
    
    If(test=Name(name='foo', ctx='load'), 
        body= [Output(nodes=[TemplateData(data=u'\n        is foo\n    ')])], 
        else_=[Output(nodes=[TemplateData(data=u'\n        bar\n    ')])]
      ), 

    Output(nodes=[TemplateData(data=u'\n</html>')])
]
```

从这里，应该可以看出抽象语法树中“树”的影子了。生成 AST 后，就是如何将这个 AST 转换成 Python 代码了。

我们不再继续展开，但是已经足够明白 JinJa 的核心部分在做什么：

* 词法分析: HTML 模板 -> token 流
* 语法分析: token 流 -> 抽象语法树
* 代码生成: 抽象语法树 -> Python 代码


### 核心特性
* 变量
* 函数
* 包含
* 条件包含
* 循环
* 求值
* 赋值
* 错误及异常
* i18n
* 自然模板
* 继承


## 学习要点

### 文档

1.顶层模块的 `__init__.py` 中说明整个模块的用途，版权，开源协议；导出内部模块的数据结构，使得引用模块时呈现扁平化的效果。

2.每个模块的开始处说明当前模块的用途，版权，开源协议


### 源代码

1.多继承
```python
class Node(object):
	pass

class Expression(list, Node):
	pass
```

2.slots
限制类属性

```python
class Comment(Node):
	__slots__ = ('pos', 'comment',)
    
    def __init__(self, pos, comment):
        self.pos = pos
        self.comment = comment
```

3.创建未定义类型

处理数据中 None 这种情况，创建一种空类型，使得数据处理上有一致性

4.定义自己的异常系统

5.如何实现简单的词法分析器和语法分析器

6.token流中使用 yield 实现一个迭代器