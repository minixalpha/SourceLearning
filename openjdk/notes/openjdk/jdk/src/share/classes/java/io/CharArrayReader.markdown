# OpenJDK 源码阅读之 CharArrayReader 

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.CharArrayReader
```

* 定义 

```java
public class CharArrayReader
extends Reader
```

* 要点

可以以一个字符数组作为输入，产生一个字符流。


## 实现

* 构造器

```java
public CharArrayReader(char buf[]) {
    this.buf = buf;
    this.pos = 0;
    this.count = buf.length;
}
```

使用一个字符数组作为输入来源，并初始化读取位置，和 buf 大小。

* read

```java
public int read() throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (pos >= count)
            return -1;
        else
            return buf[pos++];
    }
}
```

`read` 首先是线程安全的，被  `synchronized` 保护，其次，保证此时流处于打开状态。然后还需要看 `buf` 是不是已经被读取完了。正常状态会返回当前的字符  `buf[pos]`。

* read2

```java
public int read(char b[], int off, int len) throws IOException {
    synchronized (lock) {
        ensureOpen();
        if ((off < 0) || (off > b.length) || (len < 0) ||
            ((off + len) > b.length) || ((off + len) < 0)) {
            throw new IndexOutOfBoundsException();
        } else if (len == 0) {
            return 0;
        }

        if (pos >= count) {
            return -1;
        }
        if (pos + len > count) {
            len = count - pos;
        }
        if (len <= 0) {
            return 0;
        }
        System.arraycopy(buf, pos, b, off, len);
        pos += len;
        return len;
    }
}
```

将内容读取到字符数组中时，首先是一系列的范围检查，确保输入的 `off,len` 是合法的。然后看当前的状态是不是可以读取到内容。如果可以的话再修正 `len` 的值，原因在于 `len` 可能过大，超过了 `buf` 中剩余的字符数目。最后，调用  `System.arraycopy` 将 `buf` 中相应数目的字符复制到 `b` 中。