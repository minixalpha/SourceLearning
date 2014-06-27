# OpenJDK 源码阅读之 FilterReader 

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.FilterReader
```

* 定义 

```java
public abstract class FilterReader
extends Reader
```

* 要点 

这是个抽象类，构造函数参数中包含一个字符流，然后利用此流的基本功能，实现一些新的功能，例如 `PushbackReader`。


## 实现 

* 构造器 

```java
protected Reader in;

protected FilterReader(Reader in) {
    super(in);
    this.in = in;
}
```

构造器会保留一个字符流。

* read

```java
public int read() throws IOException {
    return in.read();
}
```

`read` 就是直接调用保存的字符流的 `read`，其它函数也类似。