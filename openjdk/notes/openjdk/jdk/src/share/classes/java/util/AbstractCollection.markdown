# OpenJDK 源码阅读之 AbstractCollection

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系

```java
java.lang.Object
    java.util.AbstractCollection<E>
```

* 定义 

```java
public abstract class AbstractCollection<E>
extends Object
implements Collection<E>
```

* 要点

此类的目的在于为 `Collection` 提供一个基本的实现，以减少继承时的工作。


## 实现


* contains

```java
/**
 * {@inheritDoc}
 *
 * <p>This implementation iterates over the elements in the collection,
 * checking each element in turn for equality with the specified element.
 *
 * @throws ClassCastException   {@inheritDoc}
 * @throws NullPointerException {@inheritDoc}
 */
public boolean contains(Object o) {
    Iterator<E> it = iterator();
    if (o==null) {
        while (it.hasNext())
            if (it.next()==null)
                return true;
    } else {
        while (it.hasNext())
            if (o.equals(it.next()))
                return true;
    }
    return false;
}
```

注意这里为什么要对 `o` 是否为空进行判断。因为如果 `o` 为 `null`，无法调用 `equals` 方法。

* toArray

```java
    /**
     * {@inheritDoc}
     *
     * <p>This implementation returns an array containing all the elements
     * returned by this collection's iterator, in the same order, stored in
     * consecutive elements of the array, starting with index {@code 0}.
     * The length of the returned array is equal to the number of elements
     * returned by the iterator, even if the size of this collection changes
     * during iteration, as might happen if the collection permits
     * concurrent modification during iteration.  The {@code size} method is
     * called only as an optimization hint; the correct result is returned
     * even if the iterator returns a different number of elements.
     *
     * <p>This method is equivalent to:
     *
     *  <pre> {@code
     * List<E> list = new ArrayList<E>(size());
     * for (E e : this)
     *     list.add(e);
     * return list.toArray();
     * }</pre>
     */
    public Object[] toArray() {
        // Estimate size of array; be prepared to see more or fewer elements
        Object[] r = new Object[size()];
        Iterator<E> it = iterator();
        for (int i = 0; i < r.length; i++) {
            if (! it.hasNext()) // fewer elements than expected
                return Arrays.copyOf(r, i);
            r[i] = it.next();
        }
        return it.hasNext() ? finishToArray(r, it) : r;
    }
```

体会一下如何把一个 `Collection` 转化成一个 `Array`，需要注意的是 `size()` 的值与 `iterator` 可以迭代的次数，可能不相等，可能多，也可能少。如果多的话，在 `for` 内部就要结束执行，并用 `Arrays.copyOf` 调整大小。如果少，还需要用 `finishToArray` 再继续生成数组。

* finishToArray

```java
/**
 * Reallocates the array being used within toArray when the iterator
 * returned more elements than expected, and finishes filling it from
 * the iterator.
 *
 * @param r the array, replete with previously stored elements
 * @param it the in-progress iterator over this collection
 * @return array containing the elements in the given array, plus any
 *         further elements returned by the iterator, trimmed to size
 */
private static <T> T[] finishToArray(T[] r, Iterator<?> it) {
    int i = r.length;
    while (it.hasNext()) {
        int cap = r.length;
        if (i == cap) {
            int newCap = cap + (cap >> 1) + 1;
            // overflow-conscious code
            if (newCap - MAX_ARRAY_SIZE > 0)
                newCap = hugeCapacity(cap + 1);
            r = Arrays.copyOf(r, newCap);
        }
        r[i++] = (T)it.next();
    }
    // trim if overallocated
    return (i == r.length) ? r : Arrays.copyOf(r, i);
}
```

可以看出，这里的思路是，每当数组的大小不够用时，就对它进行扩充。由于扩充的大小是每次加原来的一半加1,所以最后的时候，数组的大小还是和 `iterator` 可迭代的次数不同，所以，需要根据当前大小 `i` ，调整数组的大小，让他刚好装下数据。

* clear

```java
/**
 * {@inheritDoc}
 *
 * <p>This implementation iterates over this collection, removing each
 * element using the <tt>Iterator.remove</tt> operation.  Most
 * implementations will probably choose to override this method for
 * efficiency.
 *
 * <p>Note that this implementation will throw an
 * <tt>UnsupportedOperationException</tt> if the iterator returned by this
 * collection's <tt>iterator</tt> method does not implement the
 * <tt>remove</tt> method and this collection is non-empty.
 *
 * @throws UnsupportedOperationException {@inheritDoc}
 */
public void clear() {
    Iterator<E> it = iterator();
    while (it.hasNext()) {
        it.next();
        it.remove();
    }
}
```
 
注意，使用 `iterator`，一边迭代， 一边删除。

* toString

```java
/**
 * Returns a string representation of this collection.  The string
 * representation consists of a list of the collection's elements in the
 * order they are returned by its iterator, enclosed in square brackets
 * (<tt>"[]"</tt>).  Adjacent elements are separated by the characters
 * <tt>", "</tt> (comma and space).  Elements are converted to strings as
 * by {@link String#valueOf(Object)}.
 *
 * @return a string representation of this collection
 */
public String toString() {
    Iterator<E> it = iterator();
    if (! it.hasNext())
        return "[]";

    StringBuilder sb = new StringBuilder();
    sb.append('[');
    for (;;) {
        E e = it.next();
        sb.append(e == this ? "(this Collection)" : e);
        if (! it.hasNext())
            return sb.append(']').toString();
        sb.append(',').append(' ');
    }
}
```

唯一需要注意的就是，使用 `StringBuilder`，而不是 `String`。


可以看出，凡是需要迭代的地方，都在用 `iterator`。所以，继承类正确实现 `iterator` 很重要。