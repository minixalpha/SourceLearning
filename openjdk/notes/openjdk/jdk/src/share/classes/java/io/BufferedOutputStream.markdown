# OpenJDK 源码阅读之 BufferedOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.FilterOutputStream
            java.io.BufferedOutputStream
```

* 定义 

```java
public class BufferedOutputStream
extends FilterOutputStream
```

* 要点

顾名思义，这个类就是为输出提供缓冲功能，所以，你不用每写入一个字节都要调用操作系统的 `write` 方法，而是积累到缓冲区，然后一起写入。


## 实现

* 缓冲区 

```java
protected byte buf[];

public BufferedOutputStream(OutputStream out) {
    this(out, 8192);
}

public BufferedOutputStream(OutputStream out, int size) {
    super(out);
    if (size <= 0) {
        throw new IllegalArgumentException("Buffer size <= 0");
    }
    buf = new byte[size];
}
```

缓冲区就是一个字节数组，在构造器中被初始化。

* write

```java
public synchronized void write(int b) throws IOException {
    if (count >= buf.length) {
        flushBuffer();
    }
    buf[count++] = (byte)b;
}
```

当调用 `write(b)` 时，并不真正写入，而是将要写入的数据存放在缓冲区内，等缓冲区满后，一次性写入数据。

* flushBuffer

```java
private void flushBuffer() throws IOException {
    if (count > 0) {
        out.write(buf, 0, count);
        count = 0;
    }
}
```

写入多个字节时，调用另一个 `write` 方法，注意，这个 `write` 是底层流的 `write` 方法，例如，如果底层流是 `FileOutputStream`，会这样调用：


```java
public void write(byte b[], int off, int len) throws IOException {
    writeBytes(b, off, len, append);
}
private native void writeBytes(byte b[], int off, int len, boolean append)
    throws IOException;
```

可以看出，最终是调用了操作系统提供的 `native` 函数，一次写入多个字节。