# OpenJDK 源码阅读之 CharArrayWrite

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
        java.io.CharArrayWriter
```

* 定义 

```java
public class CharArrayWriter
extends Writer
```

* 要点

将数据写入字符数组中，可以通过 `toCharArray`，`toString` 得到这个数组，数组大小会自动扩充。


## 实现

* 数组 

```java
protected char buf[];
```

字符会被写入到这样一个数组内。


* 构造器 

默认情况下，这个数组大小为 32


```java
public CharArrayWriter() {
    this(32);
}

public CharArrayWriter(int initialSize) {
    if (initialSize < 0) {
        throw new IllegalArgumentException("Negative initial size: "
                                           + initialSize);
    }
    buf = new char[initialSize];
}
```

* write

```java
public void write(int c) {
    synchronized (lock) {
        int newcount = count + 1;
        if (newcount > buf.length) {
            buf = Arrays.copyOf(buf, Math.max(buf.length << 1, newcount));
        }
        buf[count] = (char)c;
        count = newcount;
    }
}
```

`write` 时，会将数据写入 `buf` 数组里，如果数组满了，会调用 `Arrays.copyOf` 扩充，并复制数据，生成新的数组。 扩充策略是现有大小翻倍。

* toCharArray

```java
public char toCharArray()[] {
    synchronized (lock) {
        return Arrays.copyOf(buf, count);
    }
}
```

`toCharArray` 会把内部数组复制一份，而不是直接返回内部的数组。


