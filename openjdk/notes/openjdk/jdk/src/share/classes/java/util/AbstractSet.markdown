# OpenJDK 源码阅读之 AbstractSet

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.util.AbstractCollection<E>
        java.util.AbstractSet<E>
```

* 定义 

```java
public abstract class AbstractSet<E>
extends AbstractCollection<E>
implements Set<E>
```

* 要点

`AbstractSet` 是对 `Set` 接口的简易实现。


## 实现

* equals

```java
public boolean equals(Object o) {
    if (o == this)
        return true;

    if (!(o instanceof Set))
        return false;
    Collection c = (Collection) o;
    if (c.size() != size())
        return false;
    try {
        return containsAll(c);
    } catch (ClassCastException unused)   {
        return false;
    } catch (NullPointerException unused) {
        return false;
    }
}
```

检查点依次为 `this`，是否实现 `Set` 接口，大小。最后才通过 `containsAll` 检查。大小相同，又通过 `containsAll`，说明相等。


* hashCode

```java
public int hashCode() {
    int h = 0;
    Iterator<E> i = iterator();
    while (i.hasNext()) {
        E obj = i.next();
        if (obj != null)
            h += obj.hashCode();
    }
    return h;
}
```

通过各元素的 `hashCode` 叠加，得到整个 `Set` 的 `hashCode`。

* removeAll

```java
public boolean removeAll(Collection<?> c) {
    boolean modified = false;

    if (size() > c.size()) {
        for (Iterator<?> i = c.iterator(); i.hasNext(); )
            modified |= remove(i.next());
    } else {
        for (Iterator<?> i = iterator(); i.hasNext(); ) {
            if (c.contains(i.next())) {
                i.remove();
                modified = true;
            }
        }
    }
    return modified;
}
```

比较当前集合与参数中的 `Collection` 大小，在小的一方上迭代。