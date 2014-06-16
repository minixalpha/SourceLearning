# OpenJDK 源码阅读之 FilterInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.FilterInputStream
```

* 定义  

```java
public class FilterInputStream
extends InputStream
```

* 要点

这个类会可以将其它输入流作为数据来源，其子类可以在它的基础上，对数据流添加新的功能。


## 实现


* 数据流 

```java
    protected volatile InputStream in;
```

用于保存数据来源。


* 初始化

```java
protected FilterInputStream(InputStream in) {
    this.in = in;
}
```

初始化需要指定数据流，以后读取数据就从这个数据流里读了。

* read

```java
public int read() throws IOException {
    return in.read();
}
```

可以看到，`read` 方法直接调用了其它数据流中的 `read`。