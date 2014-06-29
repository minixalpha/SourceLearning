# OpenJDK 源码阅读之 FilterOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.FilterOutputStream
```

* 定义 

```java
public class FilterOutputStream
extends OutputStream
```

* 要点

所有有过滤功能的类的基类，例如，对输出流进行转化，或者添加新的功能。初始化时，需要提供一个底层的流，用于写入数据，`FilterOUtputStream` 类的所有方法都是通过调用这个底层流的方法实现的。


## 实现

* 构造器

```java
protected OutputStream out;
public FilterOutputStream(OutputStream out) {
    this.out = out;
}
```

* write

```java
public void write(int b) throws IOException {
    out.write(b);
}
```

可以看出，此类的 `write` 方法就是调用底层流的相应方法实现的，其它方法也类似。这个类的关键在于其子类，他们才真正实现了新功能，或者提供数据转化功能。