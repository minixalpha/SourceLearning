# OpenJDK 源码阅读之 PipedOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.PipedOutputStream
```

* 类定义 

```java
public class PipedOutputStream
extends OutputStream
```

* 要点 

管道输出流可以与一个管道输入流相关联，输出流提供数据，输入流读取数据，二者应该处于不同线程，否则可能出现死锁。


## 实现 

* 初始化

```java
public PipedOutputStream(PipedInputStream snk)  throws IOException {
    connect(snk);
}

public synchronized void connect(PipedInputStream snk) throws IOException {
    if (snk == null) {
        throw new NullPointerException();
    } else if (sink != null || snk.connected) {
        throw new IOException("Already connected");
    }
    sink = snk;
    snk.in = -1;
    snk.out = 0;
    snk.connected = true;
}
```

初始化的过程就是连接管道输入流，用成员变量记录下来。


* write

```java
public void write(int b)  throws IOException {
    if (sink == null) {
        throw new IOException("Pipe not connected");
    }
    sink.receive(b);
}
```

`write` 的过程很简单，就是调用管道输入流的 `receive` 函数，这个函数会将写入的数据放在管道输入流的缓冲区内，管道输入流在读入时，从这个缓冲区内读取数据。