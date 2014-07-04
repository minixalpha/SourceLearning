# OpenJDK 源码阅读之 PipedWriter

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.PipedWriter
```

* 类定义

```java
public class PipedWriter
extends Reader
```

* 要点 

管道字节输出流，写入的数据会被与其相连接的管道字节输入流读取。


## 实现


* 初始化

```java
public PipedWriter(PipedReader snk)  throws IOException {
    connect(snk);
}
```

connect 是把与其相连接的输入流存储起来, 并初始化一些变量。

```java
    public synchronized void connect(PipedReader snk) throws IOException {
        if (snk == null) {
            throw new NullPointerException();
        } else if (sink != null || snk.connected) {
            throw new IOException("Already connected");
        } else if (snk.closedByReader || closed) {
            throw new IOException("Pipe closed");
        }

        sink = snk;
        snk.in = -1;
        snk.out = 0;
        snk.connected = true;
    }
```

* write

```java
    public void write(int c)  throws IOException {
        if (sink == null) {
            throw new IOException("Pipe not connected");
        }
        sink.receive(c);
    }
```

写入的过程就是调用与其相连接的输入流的 `receive` 方法。