# OpenJDK 源码阅读之 FilterWriter

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
        java.io.FilterWriter
```

* 定义 

```java
public abstract class FilterWriter
extends Writer
```

* 要点 

`FilterWriter` 具有 `FilterXXX` 的共同特点，所有的读写操作都通过底层流完成，
自己只负责添加功能，修改功能。这个类是个抽象类，具有类似功能的类，会去实现这个抽象类。


### 实现 

* 构造器 

```java
protected FilterWriter(Writer out) {
    super(out);
    this.out = out;
}
```

构造器中记下了底层流，以后的操作就靠你了！ 所以这个类中其它方法，都是直接调用底层流的相应方法。

* 方法

```java
public void write(int c) throws IOException {
    out.write(c);
}

public void write(char cbuf[], int off, int len) throws IOException {
    out.write(cbuf, off, len);
}

public void flush() throws IOException {
    out.flush();
}

public void close() throws IOException {
    out.close();
}
    
```