# OpenJDK 源码阅读之 DataOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.FilterOutputStream
            java.io.DataOutputStream
```

* 定义 

```java
public class DataOutputStream
extends FilterOutputStream
implements DataOutput
```

* 要点

可以按 Java 的基本类型写入数据。


## 实现

* 构造器

这个类是 `FileterOutputStream` 的子类，当然也需要一个底层流来初始化：


```java
public DataOutputStream(OutputStream out) {
    super(out);
}
```

* write

```java
public synchronized void write(int b) throws IOException {
    out.write(b);
    incCount(1);
}
```

除了调用底层流写入外，还调用了一个 incCount 函数，记录已经写入的字节的数目：


* incCount

```java
protected int written;

private void incCount(int value) {
    int temp = written + value;
    if (temp < 0) {
        temp = Integer.MAX_VALUE;
    }
    written = temp;
}
```

下面看看如何写入基本数据类型


* writeBoolean

```java
public final void writeBoolean(boolean v) throws IOException {
    out.write(v ? 1 : 0);
    incCount(1);
}
```

boolean 类型就是按照 `0/1` 的方式写入的。


* writeByte

```java
public final void writeByte(int v) throws IOException {
    out.write(v);
    incCount(1);
}
```

按字节写入时，参数是什么就写入什么。


* writeShort

```java
public final void writeShort(int v) throws IOException {
    out.write((v >>> 8) & 0xFF);
    out.write((v >>> 0) & 0xFF);
    incCount(2);
}
```

short 是两个字节，需要将其中的两个字节分离出来，分别写入，`incCount` 加了2. `writeChar` 同理，因为它也是写入两个字节。


* writeInt

```java
public final void writeInt(int v) throws IOException {
    out.write((v >>> 24) & 0xFF);
    out.write((v >>> 16) & 0xFF);
    out.write((v >>>  8) & 0xFF);
    out.write((v >>>  0) & 0xFF);
    incCount(4);
}
```

int 是四个字节，需要把它们都分离出来，然后写入。


* writeFloat

```java
    public final void writeFloat(float v) throws IOException {
        writeInt(Float.floatToIntBits(v));
    }
```

浮点数比较特殊，没法直接分离出各个字节，要调用 `Float` 的一个静态方法，把浮点数转化成四个字节，再通过 `writeInt` 写入。`floatToInitBits` 会调用一个 `native` 方法, 按照 IEEE 754 标准，完成其主要功能。