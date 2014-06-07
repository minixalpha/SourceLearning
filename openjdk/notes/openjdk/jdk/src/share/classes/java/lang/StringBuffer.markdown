# OpenJDK 源码阅读之 StringBuffer

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.lang.StringBuilder
```

* 定义 

```java
public final class StringBuilder
extends Object
implements Serializable, CharSequence
```

* 要点

`StringBuffer` 是可变字符序列，与 `StringBuffer` 区别是前者是针对单线程的，也就是说，非线程安全。最重要的方法是 `append` 和 `insert`，用于在字符串末尾或者指定位置插入字符串。


## 实现

* 数据 

```java
abstract class AbstractStringBuilder implements Appendable, CharSequence {
    /**
     * The value is used for character storage.
     */
    char[] value;
    
    ...
}
```

数据存储方式在其基类中定义，就是一个 `char` 数组。

对比一下之前分析过的 `String` 类的数据存储方式：

```java
private final char value[];
```

不同之处，显而易见。

* append

```java
public StringBuilder append(String str) {
    super.append(str);
    return this;
}
```

`append` 方法还是调用其基类中的 `append`：

```java
public AbstractStringBuilder append(String str) {
    if (str == null) str = "null";
    int len = str.length();
    ensureCapacityInternal(count + len);
    str.getChars(0, len, value, count);
    count += len;
    return this;
}
```

先对现有数组进行扩容，然后再调用 `String` 的 `getChars` 方法，

提到扩容，就需要讲讲 `StringBuilder` 是如何扩容的。

首先初始化，

```java
AbstractStringBuilder(int capacity) {
    value = new char[capacity];
}
```

扩容：

```java
    private void ensureCapacityInternal(int minimumCapacity) {
        // overflow-conscious code
        if (minimumCapacity - value.length > 0)
            expandCapacity(minimumCapacity);
    }
```

先比较一下，看需要不需要扩容，如果需要的话，


```java
void expandCapacity(int minimumCapacity) {
    int newCapacity = value.length * 2 + 2;
    if (newCapacity - minimumCapacity < 0)
        newCapacity = minimumCapacity;
    if (newCapacity < 0) {
        if (minimumCapacity < 0) // overflow
            throw new OutOfMemoryError();
        newCapacity = Integer.MAX_VALUE;
    }
    value = Arrays.copyOf(value, newCapacity);
}
```

扩容策略还和以前差不多，就是把当前容量翻倍，但是 `为什么还要加2` 呢？如果这样还不够，那就按需要的 `minimumCapacity` 指定。然后还要检查下是不是小于0啊什么的。最后调用喜闻乐见的 `Arrays.copyOf` 对数组进行扩容。

```java
public static char[] copyOf(char[] original, int newLength) {
    char[] copy = new char[newLength];
    System.arraycopy(original, 0, copy, 0,
                     Math.min(original.length, newLength));
    return copy;
}
```

`Arrays.copyOf` 会调用 `System.arraycopy`, 这是个 `native` 的方法。

* insert

`insert` 方法其实和 `append` 差不多，最终也会调用 `System.arraycopy` ，

```java
public AbstractStringBuilder insert(int offset, String str) {
    if ((offset < 0) || (offset > length()))
        throw new StringIndexOutOfBoundsException(offset);
    if (str == null)
        str = "null";
    int len = str.length();
    ensureCapacityInternal(count + len);
    System.arraycopy(value, offset, value, offset + len, count - offset);
    str.getChars(value, offset);
    count += len;
    return this;
}
```

扩容就不说了，插入过程是先通过 `System.arraycopy` 把 `offset` 到末尾的内容向后移动 `offset+len` ，然后再把要插入的内容放在空出的位置上。

只介绍这两个核心函数。