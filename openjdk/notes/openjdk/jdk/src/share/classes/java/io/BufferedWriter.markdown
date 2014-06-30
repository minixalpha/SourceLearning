# OpenJDK 源码阅读之 BufferedWriter

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
        java.io.BufferedWriter
```

* 定义 

```java
public class BufferedWriter
extends Writer
```

* 要点

增加了缓冲功能，要写入的数据，不会立即写入，而会先放在缓冲区，待缓冲区满，或者调用 `flush` 时，一次写入，以提升效率。另外，还添加了 `newLine` 函数。


## 实现 


* 构造器 

```java
public BufferedWriter(Writer out) {
    this(out, defaultCharBufferSize);
}
```

需要一个底层的流，用于写入数据，还需要指定缓冲区大小，默认是 `8192`。


```java
public BufferedWriter(Writer out, int sz) {
    super(out);
    if (sz <= 0)
        throw new IllegalArgumentException("Buffer size <= 0");
    this.out = out;
    cb = new char[sz];
    nChars = sz;
    nextChar = 0;

    lineSeparator = java.security.AccessController.doPrivileged(
        new sun.security.action.GetPropertyAction("line.separator"));
}
```

初始化时，会保存好底层流，并生成缓冲区，指定好当前写入数据的位置，另外，还需要获取行分割符号，因为不同系统的行分割符号是不一样的。


* write

```java
public void write(int c) throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (nextChar >= nChars)
            flushBuffer();
        cb[nextChar++] = (char) c;
    }
}
```

需要写入的数据，放在缓冲区 `cb` 中，如果缓冲区满，就调用 `flushBuffer` 写入。

* flushBuffer

```java
void flushBuffer() throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (nextChar == 0)
            return;
        out.write(cb, 0, nextChar);
        nextChar = 0;
    }
}
```

刷新缓冲区时，会调用底层流的 `write` 函数，具体怎么写入，就要看底层流的 `write` 是如何实现的了。


