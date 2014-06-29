# OpenJDK 源码阅读之 ByteArrayOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.ByteArrayOutputStream
```

* 定义 

```java
public class ByteArrayOutputStream
extends OutputStream
```

* 要点

这个类将数据写入字节数组中, 可以通过 `toByteArray,toString` 得到这些数据。


##  实现

* 字节数组 

```java
protected byte buf[];
```

写入的数据保存在一个 byte 数组中。


* 构造器

```java
public ByteArrayOutputStream(int size) {
    if (size < 0) {
        throw new IllegalArgumentException("Negative initial size: "
                                           + size);
    }
    buf = new byte[size];
}
```

构造器可以在初始化时，指定字节数组的大小。当然，这只是初始化大小，如果写入过程中发现不够用，还会扩充数组的大小。


* write

```java
public synchronized void write(int b) {
    ensureCapacity(count + 1);
    buf[count] = (byte) b;
    count += 1;
}
```

数组写入时，先保证字节数组大小，再写入。`ensureCapacity` 会在数组写满时，对其进行扩充。


* ensureCapacity

```java
private void ensureCapacity(int minCapacity) {
    // overflow-conscious code
    if (minCapacity - buf.length > 0)
        grow(minCapacity);
}
```

下面，我们看看扩充的策略。


* grow

```java
private void grow(int minCapacity) {
    // overflow-conscious code
    int oldCapacity = buf.length;
    int newCapacity = oldCapacity << 1;
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity < 0) {
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError();
        newCapacity = Integer.MAX_VALUE;
    }
    buf = Arrays.copyOf(buf, newCapacity);
}
```

新大小，是通过将原来的大小右移一位得到的，如果右移后不够，就直接设定为参数指定的大小。注意这里要检查新的大小是不是小于0,以防止溢出。

