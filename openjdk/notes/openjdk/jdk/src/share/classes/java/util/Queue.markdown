# OpenJDK 源码阅读之 Queue

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 定义

```java
public interface Queue<E>
extends Collection<E>
```

* 要点

`Queue` 提供了插入，删除，检查元素的方法，并分为两种形式，一种在操作失败时抛出异常，另一种返回 `null`。

* 插入：add/offer
* 删除：remove/poll
* 检查：element/peek

前者抛出异常，后者返回 `null`。

不要在 `Queue` 中插入 `null`，会和操作失败的返回值混淆的。

并发编程中常用的阻塞队列并不在此接口中定义，可以参考 ` BlockingQueue` 接口。

## 实现

可以浏览此一下需要实现什么

```java
boolean add(E e);
boolean offer(E e);
E remove();
E poll();
E element();
E peek();
```

就是之前提到的两类形式





