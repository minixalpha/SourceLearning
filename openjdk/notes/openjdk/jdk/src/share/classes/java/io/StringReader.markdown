# OpenJDK 源码阅读之 StringReader 

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.StringReader
```

* 定义 

```java
public class StringReader
extends Reader
```

* 要点 

数据来源为一个 `String` 对象。


## 实现

* 构造器

```java
public StringReader(String s) {
    this.str = s;
    this.length = s.length();
}
```

指明了数据来源，和 `length`。


* read

```java
public int read() throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (next >= length)
            return -1;
        return str.charAt(next++);
    }
}
```

线程安全；检查是否已经读完；调用 `String` 的 `charAt` 函数，实现 `read`。


* read2

```java
public int read(char cbuf[], int off, int len) throws IOException {
    synchronized (lock) {
        ensureOpen();
        if ((off < 0) || (off > cbuf.length) || (len < 0) ||
            ((off + len) > cbuf.length) || ((off + len) < 0)) {
            throw new IndexOutOfBoundsException();
        } else if (len == 0) {
            return 0;
        }
        if (next >= length)
            return -1;
        int n = Math.min(length - next, len);
        str.getChars(next, next + n, cbuf, off);
        next += n;
        return n;
    }
}
```

线程安全；检查参数；调用 `String` 的 `getChars` 函数将数据复制到字符数组中。

