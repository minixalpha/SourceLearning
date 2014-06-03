# OpenJDK 源码阅读之 AbstractQueue

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系

```
java.lang.Object
    java.util.AbstractCollection<E>
        java.util.AbstractQueue<E>
```

* 定义 

```java
public abstract class AbstractQueue<E>
extends AbstractCollection<E>
implements Queue<E>
```

* 要点 

`AbstractQueue` 是对 `Queue` 接口的一个基本实现，其中的 `add,remove,element` 是基于 `offer,poll,peek`，其实并没有实现多少东西 。


## 实现

```java
public boolean add(E e) {
    if (offer(e))
        return true;
    else
        throw new IllegalStateException("Queue full");
}
```

```java
public E remove() {
    E x = poll();
    if (x != null)
        return x;
    else
        throw new NoSuchElementException();
}
```

```java
public E element() {
    E x = peek();
    if (x != null)
        return x;
    else
        throw new NoSuchElementException();
}
```

上面三个函数可以看出一个共通的地方，就是把原来会返回空的函数包装一下，使得如果返回空的话，就抛出异常。

```java
public void clear() {
    while (poll() != null)
        ;
}
```

`clear` 是一个一个删除的，是一个 `O(n)` 时间复杂度的函数。