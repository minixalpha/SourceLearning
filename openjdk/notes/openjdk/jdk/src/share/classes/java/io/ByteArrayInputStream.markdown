# OpenJDK 源码阅读之 ByteArrayInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.ByteArrayInputStream
```

* 定义 

```java
public class ByteArrayInputStream
extends InputStream
```

* 概要

`ByteArrayInputStream` 有一个内部 `buffer` ，包含从流中读取的字节，还有一个内部 `counter`，跟踪下一个要读入的字节。


## 实现

* buf

```java
protected byte buf[];
```

这就是保存从流中读入字节的 `buffer`。

* pos

```java
protected int pos;
```

记录下一个要读入的字节的索引。

* count

```java
protected int count;
```

`buf` 中字节总数。

* 初始化

```java
public ByteArrayInputStream(byte buf[]) {
    this.buf = buf;
    this.pos = 0;
    this.count = buf.length;
}
```

`buf` 是在外部初始化，再传入构造函数中的。


* read

```java
public synchronized int read() {
    return (pos < count) ? (buf[pos++] & 0xff) : -1;
}
```

其实开始的时候，我以为 `read` 的实现会是一个函数调用，读入一个值，再放入 `buf` ，没想到 `buf` 本身是 `read` 的数据来源。。。

另外，注意这是一个线程安全的函数。

* read2

```java
public synchronized int read(byte b[], int off, int len) {
    if (b == null) {
        throw new NullPointerException();
    } else if (off < 0 || len < 0 || len > b.length - off) {
        throw new IndexOutOfBoundsException();
    }

    if (pos >= count) {
        return -1;
    }

    int avail = count - pos;
    if (len > avail) {
        len = avail;
    }
    if (len <= 0) {
        return 0;
    }
    System.arraycopy(buf, pos, b, off, len);
    pos += len;
    return len;
}
```

这个多态的 `read` ，是把 `buf` 中的数据放到 `b`中，用到的关键函数是 `System.arraycopy` ，另外，要需要参数检查。

* available

```java
public synchronized int available() {
    return count - pos;
}
```

原来 `available` 就是比较 `buf` 容量和当前要读入的字节的位置。

