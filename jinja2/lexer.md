# JinJa2 词法分析器

上一节讲过，JinJa2 中词法分析器的作用是，将 html 模板转化成 token 流，每个 token  由 (值，类型) 构成。
例如：

html 模板
```
<html>
    Hello {{ user }}
</html>
```

token 流
```
('<html>\n    Hello ', 'data'), 

('{{', 'variable_begin'), 

(' ', 'whitespace'),

('user', 'name'), 

(' ', 'whitespace'), 

('}}', 'variable_end'), 

('\n</html>', 'data')
```

我看 JinJa2 的词法分析器实现起来还挺复杂的，就想着从小例子开始，自己实现一下。起初我想，就是一个文本流， 直接用 split 分割成单词，
然后给单词分类就行了。后来一想不行。例如下面这个例子。
```
<html>
    user is {{ user }}
</html>
```

这个例子中有两个 user，很显然他们的类别是不同的，但是 split 成单词后，我们是不能知道他们的类别有什么不同的。 
这两个 user 的不同之处在于，所处的上下文环境不同，后一个 user 在 `{{ }}` 中。另一方面，我们如果直接 split ，可能把空格过滤掉了。
而上面 JinJa2 得到的 token 流中，第一个 token 是 `('<html>\n    Hello ', 'data')`， 我们使用 split 是得不到这个结果的。
从 token 流得到的结果可以看出，token 不是按照空格划分的，而是按照当前状态的类型。在上面的例子中，遇到 '{{' 之前是状态 A，遇
到 '{{' 之后是状态 B，遇到 '{{' 再遇到 '}}'，又回到状态 A。所以，我尝试用有限状态机来解决这个问题。
