# OpenJDK 源码阅读之 PipedInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.PipedInputStream
```

* 定义 

```java
public class PipedInputStream
extends InputStream
```

* 要点 

管道输入流，可以和一个管道输出流相关联，输入的数据会写入输出流中，最好一个线程负责输入数据，另一个线程负责输出，否则，如果输入和输出在一个线程内，可能会引起死锁。


## 实现

* 初始化 

```java
public PipedInputStream(PipedOutputStream src, int pipeSize)
        throws IOException {
     initPipe(pipeSize);
     connect(src);
}
```

构造器中可以指定，与管道输入流相关联的管道输出流，以及内部缓冲区的大小。

```java
private void initPipe(int pipeSize) {
     if (pipeSize <= 0) {
        throw new IllegalArgumentException("Pipe Size <= 0");
     }
     buffer = new byte[pipeSize];
}
```

缓冲区是一个字节数组。`connect` 的过程，其实是调用 `PipedOutputStream` 的 `connect`：

```java
public void connect(PipedOutputStream src) throws IOException {
    src.connect(this);
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
    int ret = buffer[out++] & 0xFF;
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

`read` 的过程，比我们之前看到的都要复杂点，先检查有没有连接管道输出流，然后检查输出端的线程是否还没处于死亡状态。

然后会设置  `readSide`，即读取端的线程。跳过 `while` 循环部分，直接看读取数据的部分。是从 `buffer` 中读取的数据，既然是这样，那么管道流的输出端一定是将数据写入了这个 `buffer`。

我们看一下 `PipedOutputStream.write`  函数：

```java
public void write(int b)  throws IOException {
    if (sink == null) {
        throw new IOException("Pipe not connected");
    }
    sink.receive(b);
}
```

可以看出，调用了相关联的管道输入流的 `receive` 函数。


```java
protected synchronized void receive(int b) throws IOException {
    checkStateForReceive();
    writeSide = Thread.currentThread();
    if (in == out)
        awaitSpace();
    if (in < 0) {
        in = 0;
        out = 0;
    }
    buffer[in++] = (byte)(b & 0xFF);
    if (in >= buffer.length) {
        in = 0;
    }
}
```

`receive` 的主要功能，就是把写入的数据放入缓冲区内。