# JinJa2 源代码学习

## 学习方式
~~从第一次提交时的项目开始学习，观察每次提交的修改，学习整个过程~~

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

* __init__.py: 主模块说明，内部功能导出
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

### 模板引擎
核心问题是，给出静态的 HTML 文件，以及变量值，生成最终返回给客户端的 HTML 文件。

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

1. 顶层模块的 `__init__.py` 中说明整个模块的用途，版权，开源协议；导出内部模块的数据结构，使得引用模块时呈现扁平化的效果。

2. 每个模块的开始处说明当前模块的用途，版权，开源协议

### 源代码

1. 多继承

```python
class Node(object):
	pass

class Expression(list, Node):
	pass
```

2. slots

限制类属性

```python
class Comment(Node):
	__slots__ = ('pos', 'comment',)
    
    def __init__(self, pos, comment):
        self.pos = pos
        self.comment = comment
```

3. 创建未定义类型

处理数据中 None 这种情况，创建一种空类型，使得数据处理上有一致性

4. 定义自己的异常系统

5. 如何实现简单的词法分析器和语法分析器