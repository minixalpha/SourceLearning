# OpenJDK 源码阅读之 ArrayDeque

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.util.AbstractCollection<E>
        java.util.ArrayDeque<E>
```

* 定义

```java
public class ArrayDeque<E>
extends AbstractCollection<E>
implements Deque<E>, Cloneable, Serializable
```

* 要点

1. 对 `Deque` 接口的实现
2. 可调整大小 
3. 非线程安全
4. 作为栈比 `Stack` 快，作为队列比 `LinkedList` 快。
5. 除了 `remove` 相关的几个操作是线性时间，其它大部分操作均摊时间都是常数级。

## 实现

* 基本数据结构 

```java
private transient E[] elements;
private transient int head;
private transient int tail;
```

数据用数组保存，`head,tail` 指向队列头尾。


* allocateElements

```java
static int allocateElements(int numElements) {
	int initialCapacity = 8;
	// Find the best power of two to hold elements.
	// Tests "<=" because arrays aren't kept full.
	if (numElements >= initialCapacity) {
		initialCapacity = numElements;
		initialCapacity |= (initialCapacity >>> 1);
		initialCapacity |= (initialCapacity >>> 2);
		initialCapacity |= (initialCapacity >>> 4);
		initialCapacity |= (initialCapacity >>> 8);
		initialCapacity |= (initialCapacity >>> 16);
		initialCapacity++;

		if (initialCapacity < 0) // Too many elements, must back off
			initialCapacity >>>= 1;// Good luck allocating 2 ^ 30 elements
	}
	return initialCapacity;
}
```

就像注释里说的那样，这个函数的目的是找到一个刚好大于 `numbElements` 的数，它是2的n次幂。这是通过移位及或运算的方式实现。
例如这个数为二进制的 `abcdefg`，`a` 是最高的不为0的位，即 `a` 为 `1`，那么第一次运算后，`b` 所在位一定为 `1`，第二次运算后，`cd` 所在位一定为 `1`，依此类推。最后全为1,再加1进位。


* doubleCapacity

```java
private void doubleCapacity() {
    assert head == tail;
    int p = head;
    int n = elements.length;
    int r = n - p; // number of elements to the right of p
    int newCapacity = n << 1;
    if (newCapacity < 0)
        throw new IllegalStateException("Sorry, deque too big");
    Object[] a = new Object[newCapacity];
    System.arraycopy(elements, p, a, 0, r);
    System.arraycopy(elements, 0, a, r, p);
    elements = (E[])a;
    head = 0;
    tail = n;
}
```

展示了如何对数组进行扩充，由于这是一个双端队列，`head` 可能在队列中间，队列现在呈现环状。队列容量增加后，不能简单地直接复制过去，而应该把 `head` 指向的元素放在新队列数组的 `0` 号位置，其它元素依次向后排列。注意两次 `System.arraycopy` 分别复制了后一半，和前一半的元素。

* addFirst

```java
public void addFirst(E e) {
    if (e == null)
        throw new NullPointerException();
    elements[head = (head - 1) & (elements.length - 1)] = e;
    if (head == tail)
        doubleCapacity();
}
```

首先，参数不能为空，其次，
注意  `addFirst` 如何巧妙地把 `head` 的位置后退一位，如果 `head` 为0的话，`&` 会使得 `head` 变成数组最后一个位置。与循环队列概念一致。


* addLast

```java
public void addLast(E e) {
    if (e == null)
        throw new NullPointerException();
    elements[tail] = e;
    if ( (tail = (tail + 1) & (elements.length - 1)) == head)
        doubleCapacity();
}
```

注意新 `tail` 是如何计算的。通过位运算，比通过 `%` 显得高大上多了。


* removeFirstOccurrence

```java
public boolean removeFirstOccurrence(Object o) {
    if (o == null)
        return false;
    int mask = elements.length - 1;
    int i = head;
    E x;
    while ( (x = elements[i]) != null) {
        if (o.equals(x)) {
            delete(i);
            return true;
        }
        i = (i + 1) & mask;
    }
    return false;
}
```

初看起来，当队列满时，并且找不到元素时，似乎会永远循环下去，但是实际上，队列永远不会满，所以一定会遇到  `null` 元素。不会满的原因可以看下之前的 `addFirst`，当队列将要满的时候，就会自动扩充。任何一个操作之后，`tail` 指向的位置都为空。


* delete

```java
private void checkInvariants() {
    assert elements[tail] == null;
    assert head == tail ? elements[head] == null :
        (elements[head] != null &&
         elements[(tail - 1) & (elements.length - 1)] != null);
    assert elements[(head - 1) & (elements.length - 1)] == null;
}
```

```java
    private boolean delete(int i) {
    checkInvariants();
    final E[] elements = this.elements;
    final int mask = elements.length - 1;
    final int h = head;
    final int t = tail;
    final int front = (i - h) & mask;
    final int back  = (t - i) & mask;

    // Invariant: head <= i < tail mod circularity
    if (front >= ((t - h) & mask))
        throw new ConcurrentModificationException();

    // Optimize for least element motion
    if (front < back) {
        if (h <= i) {
            System.arraycopy(elements, h, elements, h + 1, front);
        } else { // Wrap around
            System.arraycopy(elements, 0, elements, 1, i);
            elements[0] = elements[mask];
            System.arraycopy(elements, h, elements, h + 1, mask - h);
        }
        elements[h] = null;
        head = (h + 1) & mask;
        return false;
    } else {
        if (i < t) { // Copy the null tail as well
            System.arraycopy(elements, i + 1, elements, i, back);
            tail = t - 1;
        } else { // Wrap around
            System.arraycopy(elements, i + 1, elements, i, mask - i);
            elements[mask] = elements[0];
            System.arraycopy(elements, 1, elements, 0, t);
            tail = (t - 1) & mask;
        }
        return true;
    }
}
```

首先注意 `checkInvariants` 的使用，它保证了执行函数前应该满足的条件，这里是一个前断言。`front` 和 `back` 分别代表了要删除的结点距离双端队列头和尾的距离。通过比较 `front` 和 `back` 的大小，决定如何移动元素，使得移动次数最少。 如果 `front<back`，还需要区分 `h <= i`，决定移动哪一部分。注意这是一个成环的双端队列，画一下位置就明白这些操作了。主要是保证数据是连续的，`head/tail` 仍然保证其语义。


* iterator

`Deque` 有两个 `iterator`，分别从队列头向后遍历，从队列尾向前遍历。

```java
private class DeqIterator implements Iterator<E> {
    /**
     * Index of element to be returned by subsequent call to next.
     */
    private int cursor = head;

    /**
     * Tail recorded at construction (also in remove), to stop
     * iterator and also to check for comodification.
     */
    private int fence = tail;

    /**
     * Index of element returned by most recent call to next.
     * Reset to -1 if element is deleted by a call to remove.
     */
    private int lastRet = -1;

    public boolean hasNext() {
        return cursor != fence;
    }

    public E next() {
        if (cursor == fence)
            throw new NoSuchElementException();
        E result = elements[cursor];
        // This check doesn't catch all possible comodifications,
        // but does catch the ones that corrupt traversal
        if (tail != fence || result == null)
            throw new ConcurrentModificationException();
        lastRet = cursor;
        cursor = (cursor + 1) & (elements.length - 1);
        return result;
    }

    public void remove() {
        if (lastRet < 0)
            throw new IllegalStateException();
        if (delete(lastRet)) { // if left-shifted, undo increment in next()
            cursor = (cursor - 1) & (elements.length - 1);
            fence = tail;
        }
        lastRet = -1;
    }
}
```

这里没有什么特殊的地方，就是通过 `cursor` 不断指向下一个位置，一直到达尾部。

```java
private class DescendingIterator implements Iterator<E> {
    /*
     * This class is nearly a mirror-image of DeqIterator, using
     * tail instead of head for initial cursor, and head instead of
     * tail for fence.
     */
    private int cursor = tail;
    private int fence = head;
    private int lastRet = -1;

    public boolean hasNext() {
        return cursor != fence;
    }

    public E next() {
        if (cursor == fence)
            throw new NoSuchElementException();
        cursor = (cursor - 1) & (elements.length - 1);
        E result = elements[cursor];
        if (head != fence || result == null)
            throw new ConcurrentModificationException();
        lastRet = cursor;
        return result;
    }

    public void remove() {
        if (lastRet < 0)
            throw new IllegalStateException();
        if (!delete(lastRet)) {
            cursor = (cursor + 1) & (elements.length - 1);
            fence = head;
        }
        lastRet = -1;
    }
}
```

这是从后向前的版本。

* clear

```java
public void clear() {
    int h = head;
    int t = tail;
    if (h != t) { // clear all cells
        head = tail = 0;
        int i = h;
        int mask = elements.length - 1;
        do {
            elements[i] = null;
            i = (i + 1) & mask;
        } while (i != t);
    }
}
```

`clear` 操作并不是直接将 `head/tail` 置0就好了，还需要把每个元素置为 `null`。

* toArray

```java
public <T> T[] toArray(T[] a) {
    int size = size();
    if (a.length < size)
        a = (T[])java.lang.reflect.Array.newInstance(
                a.getClass().getComponentType(), size);
    copyElements(a);
    if (a.length > size)
        a[size] = null;
    return a;
}
```

使用反射机制，生成与泛型一致的数组，再把现有元素复制过去。