# OpenJDK 源码阅读之 BufferedInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.FilterInputStream
            java.io.BufferedInputStream
```

* 定义 

```java
public class BufferedInputStream
extends FilterInputStream
```

* 要点 

从定义看出 `BufferedInputStream` 是作为 `FilterInputStream` 子类出现的，`FilterInputStream` 保存了一个输入流作为数据来源，`BufferedInputStream` 在此基础上添加缓冲功能。


## 实现

* buf

```java
protected volatile byte buf[];
```

缓冲区由一个 `volatile byte` 数组实现，大多线程环境下，一个线程向 `volatile` 数据类型中写入的数据，会立即被其它线程看到。

* 初始化 

```java
public BufferedInputStream(InputStream in, int size) {
    super(in);
    if (size <= 0) {
        throw new IllegalArgumentException("Buffer size <= 0");
    }
    buf = new byte[size];
}
```

初始化的过程会 `new` 一个 `byte` 数组。

如果没有提供 `size`，会给一个默认值。

```java
public BufferedInputStream(InputStream in) {
    this(in, defaultBufferSize);
}
private static int defaultBufferSize = 8192;
```

* read

```java
private byte[] getBufIfOpen() throws IOException {
    byte[] buffer = buf;
    if (buffer == null)
        throw new IOException("Stream closed");
    return buffer;
}
public synchronized int read() throws IOException {
    if (pos >= count) {
        fill();
        if (pos >= count)
            return -1;
    }
    return getBufIfOpen()[pos++] & 0xff;
}
```

`pos` 表示当前读取的字符在缓冲区的位置，`count` 表示缓冲区大小，如果 `read` 时，缓冲区的数据已经读完了，需要调用 `fill` 一次填充好缓冲区，然后通过 `getBufIfOpen` 得到 `buf`，并返回当前字节内容。

* fill

```java
private void fill() throws IOException {
    byte[] buffer = getBufIfOpen();
    if (markpos < 0)
        pos = 0;            /* no mark: throw away the buffer */
    else if (pos >= buffer.length)  /* no room left in buffer */
        if (markpos > 0) {  /* can throw away early part of the buffer */
            int sz = pos - markpos;
            System.arraycopy(buffer, markpos, buffer, 0, sz);
            pos = sz;
            markpos = 0;
        } else if (buffer.length >= marklimit) {
            markpos = -1;   /* buffer got too big, invalidate mark */
            pos = 0;        /* drop buffer contents */
        } else {            /* grow buffer */
            int nsz = pos * 2;
            if (nsz > marklimit)
                nsz = marklimit;
            byte nbuf[] = new byte[nsz];
            System.arraycopy(buffer, 0, nbuf, 0, pos);
            if (!bufUpdater.compareAndSet(this, buffer, nbuf)) {
                // Can't replace buf if there was an async close.
                // Note: This would need to be changed if fill()
                // is ever made accessible to multiple threads.
                // But for now, the only way CAS can fail is via close.
                // assert buf == null;
                throw new IOException("Stream closed");
            }
            buffer = nbuf;
        }
    count = pos;
    int n = getInIfOpen().read(buffer, pos, buffer.length - pos);
    if (n > 0)
        count = n + pos;
}
```

fill 主要处理这几件事，一是处理 `markpos`。


先解析一下 `markpos` 的工作方式。当我们调用 `mark` 方法时，`markpos` 会记录下当前读入字节的位置  `pos`，然后继续读入时，`pos` 会增加，如果我们想回到 `markpos`，从那儿开始读起，可以调用 `reset`，将 `pos` 恢复为 `markpos`，以下两个函数表达了这个意思。

* mark&reset

```java
public synchronized void mark(int readlimit) {
    marklimit = readlimit;
    markpos = pos;
}
public synchronized void reset() throws IOException {
    getBufIfOpen(); // Cause exception if closed
    if (markpos < 0)
        throw new IOException("Resetting to invalid mark");
    pos = markpos;
}
```

`mark` 中的 `marklimit` 表示，在 `mark` 位置失效前最多可以读入的字节数目。

有了这个 `markpos` 后，我们会发现，`fill` 的时候，不能简单地把原来缓冲区的内容填充新的内容，从 `markpos` 开始到最后的内容都要保留。

注意 `fill` 中的：

```java
if (markpos > 0) {  /* can throw away early part of the buffer */
    int sz = pos - markpos;
    System.arraycopy(buffer, markpos, buffer, 0, sz);
    pos = sz;
    markpos = 0;
}
```

就是把 `buffer` 中 `markpos` 到 `pos` 的内容，复制到 `0` 到 `pos-markpos` 中去。

另外，在 `markpos` 为0时，需要比较 `buffer.length` 和 `marklimit` 的大小，如果 `marklimit` 小，那么一切恢复原状，否则，就要扩大 `buffer` 的大小，不然 `marklimt` 就是非法的值。

扩充策略还是翻位，但是不能太大，最大也就是 `marklimit`。随后是新建一个缓冲区，复制内容，并将 `buffer` 设置为新缓冲区。这里使用了原子操作 `compareAndSet`，但是后面为什么又使用了一次 `buffer = nbuf` 呢？

    