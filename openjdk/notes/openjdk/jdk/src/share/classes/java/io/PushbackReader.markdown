# OpenJDK 源码阅读之 PushbackReader 

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.FilterReader
            java.io.PushbackReader
```

* 定义 

```java
public class PushbackReader
extends FilterReader
```

* 要点

这个类允许将字符放回输入流中。


## 实现 

其实之前在字节流中已经介绍过相似的实现 `PushbackInputStream` ，只不过是以字节形式出现的。类的内部保存着一个缓冲区，被放回的字符都保存在这里，读取时，先在缓冲区里读，读完了，再从原始的流中读入数据。


* 缓冲区 

```java
/** Pushback buffer */
private char[] buf;

/** Current position in buffer */
private int pos;
```

类内部的缓冲区，及指示当前读取位置的 `pos` 。

* 构造器 

```java
public PushbackReader(Reader in, int size) {
    super(in);
    if (size <= 0) {
        throw new IllegalArgumentException("size <= 0");
    }
    this.buf = new char[size];
    this.pos = size;
}
```

初始化时，可以指定缓冲区的大小，如果不指定，默认为 1: 

```java
public PushbackReader(Reader in) {
    this(in, 1);
}
```

* read

```java
public int read() throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (pos < buf.length)
            return buf[pos++];
        else
            return super.read();
    }
}
```

简单明了，buf 中还有没读取的数据时，先从 `buf` 里读，否则就从原始流中 `read`，原始流在构造器中指定。


* unread

```java
public void unread(int c) throws IOException {
    synchronized (lock) {
        ensureOpen();
        if (pos == 0)
            throw new IOException("Pushback buffer overflow");
        buf[--pos] = (char) c;
    }
}
```

unread 时，先检查 `buf` 是不是满了，没满的话就放进去。注意 `pos` 是从大到小逐步减少的，也就是说，退回的字符先放在 buf 的最后，然后依次向前放。而读取时，则是从前向后，就像一个栈一样，后进先出。

* read2

```java
public int read(char cbuf[], int off, int len) throws IOException {
    synchronized (lock) {
        ensureOpen();
        try {
            if (len <= 0) {
                if (len < 0) {
                    throw new IndexOutOfBoundsException();
                } else if ((off < 0) || (off > cbuf.length)) {
                    throw new IndexOutOfBoundsException();
                }
                return 0;
            }
            int avail = buf.length - pos;
            if (avail > 0) {
                if (len < avail)
                    avail = len;
                System.arraycopy(buf, pos, cbuf, off, avail);
                pos += avail;
                off += avail;
                len -= avail;
            }
            if (len > 0) {
                len = super.read(cbuf, off, len);
                if (len == -1) {
                    return (avail == 0) ? -1 : avail;
                }
                return avail + len;
            }
            return avail;
        } catch (ArrayIndexOutOfBoundsException e) {
            throw new IndexOutOfBoundsException();
        }
    }
}
```

如果是将从个字符读取到一个字符数组中，需要计算好，从缓冲区读多少，从原始流中读取多少，才能满足读取的字符数目要求。