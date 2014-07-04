# OpenJDK 源码阅读之 PipedReader

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.PipedReader
```

* 类定义

```java
public class PipedReader
extends Reader
```

* 要点 

管道字符输入流，与管道字符输出流配合使用，输出流写入，输入流读出。


## 实现

* 初始化

```java
public PipedReader(PipedWriter src, int pipeSize) throws IOException {
    initPipe(pipeSize);
    connect(src);
}
```

和管道字节输入流一样，初始化缓冲区，连接管道字节输出流。只不过，这里的缓冲区是字符数组，不是字节数组：


```java
private void initPipe(int pipeSize) {
    if (pipeSize <= 0) {
        throw new IllegalArgumentException("Pipe size <= 0");
    }
    buffer = new char[pipeSize];
}
```

* read

```java
    public synchronized int read()  throws IOException {
        if (!connected) {
            throw new IOException("Pipe not connected");
        } else if (closedByReader) {
            throw new IOException("Pipe closed");
        } else if (writeSide != null && !writeSide.isAlive()
                   && !closedByWriter && (in < 0)) {
            throw new IOException("Write end dead");
        }

        readSide = Thread.currentThread();
        int trials = 2;
        while (in < 0) {
            if (closedByWriter) {
                /* closed by writer, return EOF */
                return -1;
            }
            if ((writeSide != null) && (!writeSide.isAlive()) && (--trials < 0)) {
                throw new IOException("Pipe broken");
            }
            /* might be a writer waiting */
            notifyAll();
            try {
                wait(1000);
            } catch (InterruptedException ex) {
                throw new java.io.InterruptedIOException();
            }
        }
        int ret = buffer[out++];
        if (out >= buffer.length) {
            out = 0;
        }
        if (in == out) {
            /* now empty */
            in = -1;
        }
        return ret;
    }
```

read 同样是从缓冲区中读取数据，与其相连接的 `PipedWriter` 会在写入数据时，调用 `PipedReader` 的 `receive` 函数，这个函数向缓冲区内写入数据。


* receive

```java
synchronized void receive(int c) throws IOException {
    if (!connected) {
        throw new IOException("Pipe not connected");
    } else if (closedByWriter || closedByReader) {
        throw new IOException("Pipe closed");
    } else if (readSide != null && !readSide.isAlive()) {
        throw new IOException("Read end dead");
    }

    writeSide = Thread.currentThread();
    while (in == out) {
        if ((readSide != null) && !readSide.isAlive()) {
            throw new IOException("Pipe broken");
        }
        /* full: kick any waiting readers */
        notifyAll();
        try {
            wait(1000);
        } catch (InterruptedException ex) {
            throw new java.io.InterruptedIOException();
        }
    }
    if (in < 0) {
        in = 0;
        out = 0;
    }
    buffer[in++] = (char) c;
    if (in >= buffer.length) {
        in = 0;
    }
}
```

注意，`in` 与 `out` 指示了当前写入和读取的位置，`receive` 时，`buffer` 中，写入当前的 `in` 位置， `read` 时，读取当前的 `out`  位置。




