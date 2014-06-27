# OpenJDK 源码阅读之 OutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系

```java
java.lang.Object
    java.io.OutputStream
```

* 定义 

```java
public abstract class OutputStream
extends Object
implements Closeable, Flushable
```

* 要点 

所有以输出字节流类的超类

## 实现


这是个抽象类，需要实现其中定义的 `write` 函数，才能有实用的功能。

```java
    public abstract void write(int b) throws IOException;
```

其它方法都是在 `write` 的基础上实现的。

* write

```java
public void write(byte b[], int off, int len) throws IOException {
    if (b == null) {
        throw new NullPointerException();
    } else if ((off < 0) || (off > b.length) || (len < 0) ||
               ((off + len) > b.length) || ((off + len) < 0)) {
        throw new IndexOutOfBoundsException();
    } else if (len == 0) {
        return;
    }
    for (int i = 0 ; i < len ; i++) {
        write(b[off + i]);
    }
}
```

先检查了一通参数，再循环调用 `write(b)` 。

另外，`flush` 和 `close` 都没有给出实现。


```java
public void flush() throws IOException {
}
public void close() throws IOException {
}
```

`flush` 会将缓冲区中的内容写回，`close` 关闭输出流。