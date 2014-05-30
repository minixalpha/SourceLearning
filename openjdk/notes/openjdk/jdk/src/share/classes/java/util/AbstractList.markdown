# OpenJDK 源码阅读之 AbstractList

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系

```java
java.lang.Object
    java.util.AbstractCollection<E>
        java.util.AbstractList<E>
```

* 定义 

```java
public abstract class AbstractList<E>
extends AbstractCollection<E>
implements List<E>
```

* 要点 

`AbstractList` 是对 `List` 接口的最基本实现，目的是为了减少实现 List 接口时需要付出的努力。这个类是对“随机访问式”的列表的实现，另一个类，`AbstraceSequential` 类是对“顺序访问式”列表的基本实现。

## 实现

* lastIndexOf

```java
/**
 * {@inheritDoc}
 *
 * <p>This implementation first gets a list iterator that points to the end
 * of the list (with {@code listIterator(size())}).  Then, it iterates
 * backwards over the list until the specified element is found, or the
 * beginning of the list is reached.
 *
 * @throws ClassCastException   {@inheritDoc}
 * @throws NullPointerException {@inheritDoc}
 */
public int lastIndexOf(Object o) {
    ListIterator<E> it = listIterator(size());
    if (o==null) {
        while (it.hasPrevious())
            if (it.previous()==null)
                return it.nextIndex();
    } else {
        while (it.hasPrevious())
            if (o.equals(it.previous()))
                return it.nextIndex();
    }
    return -1;
}
```

注意对 `listIterator` 的使用，首先把迭代器设置到最后一个位置之后，再依次向前迭代，返回索引时，返回 `nextIndex`。

* Iterator

```java
private class Itr implements Iterator<E> {
    /**
     * Index of element to be returned by subsequent call to next.
     */
    int cursor = 0;

    /**
     * Index of element returned by most recent call to next or
     * previous.  Reset to -1 if this element is deleted by a call
     * to remove.
     */
    int lastRet = -1;

    /**
     * The modCount value that the iterator believes that the backing
     * List should have.  If this expectation is violated, the iterator
     * has detected concurrent modification.
     */
    int expectedModCount = modCount;

    public boolean hasNext() {
        return cursor != size();
    }

    public E next() {
        checkForComodification();
        try {
            int i = cursor;
            E next = get(i);
            lastRet = i;
            cursor = i + 1;
            return next;
        } catch (IndexOutOfBoundsException e) {
            checkForComodification();
            throw new NoSuchElementException();
        }
    }

    public void remove() {
        if (lastRet < 0)
            throw new IllegalStateException();
        checkForComodification();

        try {
            AbstractList.this.remove(lastRet);
            if (lastRet < cursor)
                cursor--;
            lastRet = -1;
            expectedModCount = modCount;
        } catch (IndexOutOfBoundsException e) {
            throw new ConcurrentModificationException();
        }
    }

    final void checkForComodification() {
        if (modCount != expectedModCount)
            throw new ConcurrentModificationException();
    }
}
```

`AbstractList` 已经实现好了 `Iterator`，可以看出这里的基本思路，每一个 `iterator`对象，都在内部维护两个指针，一个指向调用 `next` 时要返回的对象的位置:`cursor`，一个指向上一次的位置:`lastRet`。每次调用 `next`，`lastRet`保留当前位置，`cursor`向后移一个位置，并返回当前位置的值。`remove` 的时候，会调用当前 `list` 的 `remove` 方法，做实际的删除动作，然后调整 `cursor` 和 `lastRet` 的值。删除 `lastRet` 指向的位置后，`cursor` 指向的元素的索引会降低1。同时要把 `lastRet` 设置成 `-1`，表示无效状态。不然 `lastRet` 无法保持其语义，即 `lastRet` 指向最近一次 `next` 返回值的位置。所以，我们是无法连续调用 `remove` 的。看看的 `remove` 一开始时对 `lastRet` 的检查就知道了。

* listIterator

```java
    private class ListItr extends Itr implements ListIterator<E> {
        ListItr(int index) {
            cursor = index;
        }

        public boolean hasPrevious() {
            return cursor != 0;
        }

        public E previous() {
            checkForComodification();
            try {
                int i = cursor - 1;
                E previous = get(i);
                lastRet = cursor = i;
                return previous;
            } catch (IndexOutOfBoundsException e) {
                checkForComodification();
                throw new NoSuchElementException();
            }
        }

        public int nextIndex() {
            return cursor;
        }

        public int previousIndex() {
            return cursor-1;
        }

        public void set(E e) {
            if (lastRet < 0)
                throw new IllegalStateException();
            checkForComodification();

            try {
                AbstractList.this.set(lastRet, e);
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }

        public void add(E e) {
            checkForComodification();

            try {
                int i = cursor;
                AbstractList.this.add(i, e);
                lastRet = -1;
                cursor = i + 1;
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }
    }
```

注意它是对 `Iter` 的继承，也就是说 `Iter` 有的他也有，而且还添加了一些新功能。理解这些新功能的关键是，`cursor` 和 `lastRet` 要表达的含义不能改变。

`previous` 返回的是 `cursor` 的前一个位置的值，并且把 `cursor` 前移一个位置，`lastRec` 同时被设置为 `cursor` 前一位置，而不是减1。如果减1, 那么 `remove` 删除最近一次 `next` 或 `previous` 返回值的说法就不成立了。

另外，注意 `add` 会把 `lastRect` 设置为 `-1`，也就是说，`add` 调用后，不能立即调用 `remove`，`remove` 只能是调用 `next`, `previous` 后才能用。


```java
/**
 * Compares the specified object with this list for equality.  Returns
 * {@code true} if and only if the specified object is also a list, both
 * lists have the same size, and all corresponding pairs of elements in
 * the two lists are <i>equal</i>.  (Two elements {@code e1} and
 * {@code e2} are <i>equal</i> if {@code (e1==null ? e2==null :
 * e1.equals(e2))}.)  In other words, two lists are defined to be
 * equal if they contain the same elements in the same order.<p>
 *
 * This implementation first checks if the specified object is this
 * list. If so, it returns {@code true}; if not, it checks if the
 * specified object is a list. If not, it returns {@code false}; if so,
 * it iterates over both lists, comparing corresponding pairs of elements.
 * If any comparison returns {@code false}, this method returns
 * {@code false}.  If either iterator runs out of elements before the
 * other it returns {@code false} (as the lists are of unequal length);
 * otherwise it returns {@code true} when the iterations complete.
 *
 * @param o the object to be compared for equality with this list
 * @return {@code true} if the specified object is equal to this list
 */
public boolean equals(Object o) {
    if (o == this)
        return true;
    if (!(o instanceof List))
        return false;

    ListIterator<E> e1 = listIterator();
    ListIterator e2 = ((List) o).listIterator();
    while (e1.hasNext() && e2.hasNext()) {
        E o1 = e1.next();
        Object o2 = e2.next();
        if (!(o1==null ? o2==null : o1.equals(o2)))
            return false;
    }
    return !(e1.hasNext() || e2.hasNext());
}
```

`equals` 会用 `listIterator` 遍历比较两个链表，并调用链表中元素的 `equals` 方法。如果循环内的比较比不出来，最后 `return` 的时候再看看两个链表是不是有剩余元素，任何一个有都会返回 `false`。

* hashCode

```java
/**
 * Returns the hash code value for this list.
 *
 * <p>This implementation uses exactly the code that is used to define the
 * list hash function in the documentation for the {@link List#hashCode}
 * method.
 *
 * @return the hash code value for this list
 */
public int hashCode() {
    int hashCode = 1;
    for (E e : this)
        hashCode = 31*hashCode + (e==null ? 0 : e.hashCode());
    return hashCode;
}
```

遍历链表，如果表是 a[1:n]，hashCode 是：

```
31^n + a[1].hashCode() * 31^(n-1) + a[2].hashCode() * 31^(n-2) + ... + a[n] * 1 
```

* subList 

```java
class SubList<E> extends AbstractList<E> {
private final AbstractList<E> l;
private final int offset;
private int size;

SubList(AbstractList<E> list, int fromIndex, int toIndex) {
    if (fromIndex < 0)
        throw new IndexOutOfBoundsException("fromIndex = " + fromIndex);
    if (toIndex > list.size())
        throw new IndexOutOfBoundsException("toIndex = " + toIndex);
    if (fromIndex > toIndex)
        throw new IllegalArgumentException("fromIndex(" + fromIndex +
                                           ") > toIndex(" + toIndex + ")");
    l = list;
    offset = fromIndex;
    size = toIndex - fromIndex;
    this.modCount = l.modCount;
}

public E set(int index, E element) {
    rangeCheck(index);
    checkForComodification();
    return l.set(index+offset, element);
}

...
...
```

`SubList` 的设计，需要注意的地方是，它并没有生成新的链表，而是通过`offset` 来保持一个偏移值，此后的操作仍然是在原链表上，只不过所有操作都是都需要加上这个 `offset`，注意 `set` ，就是调用原来表的 `set` 操作，只是在 `index` 上加了 `offset`。