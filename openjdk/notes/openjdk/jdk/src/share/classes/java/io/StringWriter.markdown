# OpenJDK 源码阅读之 StringWriter

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
        java.io.StringWriter
```

* 定义 

```java
public class StringWriter
extends Writer
```

* 要点

将数据写入一个 string 缓冲区内，当需要时，会转化成 string，听起来很像 CharArrayWriter 啊，不知道有什么不同。


## 实现

* 内部缓冲 

```java
private StringBuffer buf;
```

内部是使用 `StringBuffer` 保存写入的数据的。


* 构造器 

```java
public StringWriter() {
    buf = new StringBuffer();
    lock = buf;
}
```

初始化时，会生成  `StringBuffer` 对象，并设置锁，由于多个线程共同操作此对象时，会共享 buf ，所以锁就在 buf 上。


* write

```java
    public void write(int c) {
        buf.append((char) c);
    }
```

`write` 就是调用了 `StringBuffer` 的 `append` 函数，不过从这里看，也没有使用锁啊。。不过，`append` 函数本身就是带有 `synchronized` 关键字的。

另外，这个类还提供了写入 string 功能。

```java
    public void write(String str) {
        buf.append(str);
    }
```

似乎是在类中，为 `StringBuffer` 的一些方法提供了相应的接口。