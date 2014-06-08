# OpenJDK 源码阅读之 Collection

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 定义 

```java
public interface Collection<E>
extends Iterable<E>
```

* 要点

`Collection` 接口是整个 `collection 系列` 类的根接口。


## 实现

这是一个接口，没有任何实现，只定义了一系列函数：


```java
int size();
boolean isEmpty();
boolean contains(Object o);
Iterator<E> iterator();
Object[] toArray();
<T> T[] toArray(T[] a);
boolean add(E e);
boolean remove(Object o);
boolean containsAll(Collection<?> c);
boolean addAll(Collection<? extends E> c);
boolean removeAll(Collection<?> c);
boolean retainAll(Collection<?> c);
void clear();
boolean equals(Object o);
int hashCode();
```
