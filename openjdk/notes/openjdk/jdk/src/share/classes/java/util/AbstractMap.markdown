# OpenJDK 源码阅读之 AbstractMap

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系

```java
java.lang.Object
    java.util.AbstractMap<K,V>
```

* 定义 

```java
public abstract class AbstractMap<K,V>
extends Object
implements Map<K,V>
```

* 要点 

1. 为 `Map` 接口提供了基本实现


## 实现

* entrySet

大部分实现都要依赖于 `entrySet` 的实现，例如:

```java
public int size() {
    return entrySet().size();
}
```

```java
public boolean containsKey(Object key) {
    Iterator<Map.Entry<K,V>> i = entrySet().iterator();
    if (key==null) {
        while (i.hasNext()) {
            Entry<K,V> e = i.next();
            if (e.getKey()==null)
                return true;
        }
    } else {
        while (i.hasNext()) {
            Entry<K,V> e = i.next();
            if (key.equals(e.getKey()))
                return true;
        }
    }
    return false;
}
```

```java
public V get(Object key) {
    Iterator<Entry<K,V>> i = entrySet().iterator();
    if (key==null) {
        while (i.hasNext()) {
            Entry<K,V> e = i.next();
            if (e.getKey()==null)
                return e.getValue();
        }
    } else {
        while (i.hasNext()) {
            Entry<K,V> e = i.next();
            if (key.equals(e.getKey()))
                return e.getValue();
        }
    }
    return null;
}
```

另外，如果你要继承这个类，实现一个实用的 `Map`，需要自己实现 `put` 和 `entrySet`

```java
public V put(K key, V value) {
    throw new UnsupportedOperationException();
}
```

* keySet

```java
public Set<K> keySet() {
    if (keySet == null) {
        keySet = new AbstractSet<K>() {
            public Iterator<K> iterator() {
                return new Iterator<K>() {
                    private Iterator<Entry<K,V>> i = entrySet().iterator();

                    public boolean hasNext() {
                        return i.hasNext();
                    }

                    public K next() {
                        return i.next().getKey();
                    }

                    public void remove() {
                        i.remove();
                    }
                };
            }

            public int size() {
                return AbstractMap.this.size();
            }

            public boolean isEmpty() {
                return AbstractMap.this.isEmpty();
            }

            public void clear() {
                AbstractMap.this.clear();
            }

            public boolean contains(Object k) {
                return AbstractMap.this.containsKey(k);
            }
        };
    }
    return keySet;
}
```

`keySet` 并不是新生成了一个集合，把当前 `key` 值放进去，而是通过一个匿名类来实现的，在此类内部新生成一个 `entrySet` 的迭代器，然后在迭代器上面进行迭代。

* equals

```java
public boolean equals(Object o) {
    if (o == this)
        return true;

    if (!(o instanceof Map))
        return false;
    Map<K,V> m = (Map<K,V>) o;
    if (m.size() != size())
        return false;

    try {
        Iterator<Entry<K,V>> i = entrySet().iterator();
        while (i.hasNext()) {
            Entry<K,V> e = i.next();
            K key = e.getKey();
            V value = e.getValue();
            if (value == null) {
                if (!(m.get(key)==null && m.containsKey(key)))
                    return false;
            } else {
                if (!value.equals(m.get(key)))
                    return false;
            }
        }
    } catch (ClassCastException unused) {
        return false;
    } catch (NullPointerException unused) {
        return false;
    }

    return true;
}
```

`equals` 展示了如何检查两个 `Map` 是否相等，这是通过迭代一个 `Map`，然后在另一个 `Map` 中查找并比较的方式实现的。

* hashCode

```java
public int hashCode() {
    int h = 0;
    Iterator<Entry<K,V>> i = entrySet().iterator();
    while (i.hasNext())
        h += i.next().hashCode();
    return h;
}
```

从之前的源代码分析中，可以感觉到，`List` 中的 hashCode 都是通过类似这种 

```
hashCode = 31 * hashCode + curNode.hashCode()
```

的方式实现的，而到了 `Map` 里， `hashCode` 却是通过累加的方式实现的，这是为什么呢？和 `Map` 里的 `hashCode` 要求严格以避免冲突有关吗？

* toString

```java
public String toString() {
    Iterator<Entry<K,V>> i = entrySet().iterator();
    if (! i.hasNext())
        return "{}";

    StringBuilder sb = new StringBuilder();
    sb.append('{');
    for (;;) {
        Entry<K,V> e = i.next();
        K key = e.getKey();
        V value = e.getValue();
        sb.append(key   == this ? "(this Map)" : key);
        sb.append('=');
        sb.append(value == this ? "(this Map)" : value);
        if (! i.hasNext())
            return sb.append('}').toString();
        sb.append(',').append(' ');
    }
}
```

这个 `toString` 很有意思，注意需要检查 `key` 是不是等于当前的对象，这是为了应对将自身当作 `key` 加入自身的行为。否则会出现无限循环。最终的 `Map` 类型就是类似:

```
{k1=v1, k2=v2}
```

这样的。


```