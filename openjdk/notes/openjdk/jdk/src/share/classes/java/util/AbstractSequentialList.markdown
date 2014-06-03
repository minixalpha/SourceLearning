# OpenJDK 源码阅读之 AbstractSequentialList

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.util.AbstractCollection<E>
        java.util.AbstractList<E>
            java.util.AbstractSequentialList<E>
```

* 定义 

```java
public abstract class AbstractSequentialList<E>
extends AbstractList<E>
```

* 要点

`AbstractSequentialList` 是对 `List` 接口的一个简易实现，提供对“顺序访问”形式的 `List` 的支持。为了实现一个真正的 `List`，需要提供 `listIterator` 及 `size` 方法。如果实现不可变 `List`，需要实现 `listIterator` 的 `hasNext, next, hasPrevious, previous, index`，如果实现可变 `List`，还需要实现 `set`。

## 实现


* get

```java
public E get(int index) {
    try {
        return listIterator(index).next();
    } catch (NoSuchElementException exc) {
        throw new IndexOutOfBoundsException("Index: "+index);
    }
}
```

* set

```java
public E set(int index, E element) {
    try {
        ListIterator<E> e = listIterator(index);
        E oldVal = e.next();
        e.set(element);
        return oldVal;
    } catch (NoSuchElementException exc) {
        throw new IndexOutOfBoundsException("Index: "+index);
    }
}
```

从 `get,set`  的实现可以看出，它们都是在 `listIteraotr` 的基础上实现的。

* iterator

```java
public Iterator<E> iterator() {
    return listIterator();
}
```

* listIterator

```java
public abstract ListIterator<E> listIterator(int index);
```

上面的两点，是此类中和 `iterator` 相关的内容，可以看出，关键还是 `listIterator` 的实现。