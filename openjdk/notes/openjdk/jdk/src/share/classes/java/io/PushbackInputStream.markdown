# OpenJDK 源码阅读之 PushbackInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.FilterInputStream
            java.io.PushbackInputStream
```

* 定义 

```java
public class PushbackInputStream
extends FilterInputStream
```

* 要点 

`PushbackInputStream` 是 `FilterInputStream` 的子类，它 的特点是，可以把一个已经读取的字节放回输入流中，这样下次再读取的时候，还可以读取到这个字节。


## 实现

* 缓冲区 

```java
protected byte[] buf;
```

这是一个缓冲区，我们“放回”输入流中的字节，实际上不是退还给了输入流，而是放在这个缓冲区里，每次读取时，先看下这个缓冲区里有没有退回来的字节，如果有，就返回相应字节，如果没有，再从“输入流”中读取。

* 初始化

```java
public PushbackInputStream(InputStream in, int size) {
    super(in);
    if (size <= 0) {
        throw new IllegalArgumentException("size <= 0");
    }
    this.buf = new byte[size];
    this.pos = size;
}
```

需要一个 `pos` 记录缓冲区中读取字节的位置。

* read

```java
public int read() throws IOException {
    ensureOpen();
    if (pos < buf.length) {
        return buf[pos++] & 0xff;
    }
    return super.read();
}
```

`read` 会用 `ensureOpen` 检查输入流是否打开了。然后会比较当前读取的位置与 `buf.length` 的关系，如果 `pos` 小，说明缓冲区里还有没有读取到的数据，所以需要从这里读取。否则就正常读取。

* unread

```java
public void unread(int b) throws IOException {
    ensureOpen();
    if (pos == 0) {
        throw new IOException("Push back buffer is full");
    }
    buf[--pos] = (byte)b;
}
```

`unread` 即是传说中的 "退回" 操作，我们会把一个字节放入缓冲区 `buf`，注意 `pos` 需要减一。看 `buf` 这操作就是个栈操作啊。这也和“退回”的思想相近，最后一次退回的，最先读取到。

好了，这就是 `PushbackInputstream` 的基本思路。