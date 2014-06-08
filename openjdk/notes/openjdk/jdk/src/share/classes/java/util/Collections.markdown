# OpenJDK 源码阅读之 Collections

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.util.Collections
```

* 定义 

```java
public class Collections
extends Object
```

## 实现

* sort

```java
public static <T extends Comparable<? super T>> void sort(List<T> list) {
    Object[] a = list.toArray();
    Arrays.sort(a);
    ListIterator<T> i = list.listIterator();
    for (int j=0; j<a.length; j++) {
        i.next();
        i.set((T)a[j]);
    }
}
```

`sort` 的实现调用了 `Arrays` 中的 `sort` 方法，这个以前分析过，不多说了，调用完后，再通过 `iterator` 把结果复制到 `list` 中。

* search

```java
private static <T>
int indexedBinarySearch(List<? extends Comparable<? super T>> list, T key)
{
    int low = 0;
    int high = list.size()-1;

    while (low <= high) {
        int mid = (low + high) >>> 1;
        Comparable<? super T> midVal = list.get(mid);
        int cmp = midVal.compareTo(key);

        if (cmp < 0)
            low = mid + 1;
        else if (cmp > 0)
            high = mid - 1;
        else
            return mid; // key found
    }
    return -(low + 1);  // key not found
}
```

二分查找是自己实现的，每次排除一半。

* reverse

```java
public static void reverse(List<?> list) {
    int size = list.size();
    if (size < REVERSE_THRESHOLD || list instanceof RandomAccess) {
        for (int i=0, mid=size>>1, j=size-1; i<mid; i++, j--)
            swap(list, i, j);
    } else {
        ListIterator fwd = list.listIterator();
        ListIterator rev = list.listIterator(size);
        for (int i=0, mid=list.size()>>1; i<mid; i++) {
            Object tmp = fwd.next();
            fwd.set(rev.previous());
            rev.set(tmp);
        }
    }
}
```

如果可以随机访问，或者 `list` 中元素数量不大，就调用 `swap` 交换首尾对应元素，否则就使用两个 `iterator`，一个向后，一个向前，每次会交换元素。


* shuffle

shuffle 会把 `list` 中的元素打乱，我们看看是怎么打乱的。


```java
public static void shuffle(List<?> list, Random rnd) {
    int size = list.size();
    if (size < SHUFFLE_THRESHOLD || list instanceof RandomAccess) {
        for (int i=size; i>1; i--)
            swap(list, i-1, rnd.nextInt(i));
    } else {
        Object arr[] = list.toArray();

        // Shuffle array
        for (int i=size; i>1; i--)
            swap(arr, i-1, rnd.nextInt(i));

        // Dump array back into list
        ListIterator it = list.listIterator();
        for (int i=0; i<arr.length; i++) {
            it.next();
            it.set(arr[i]);
        }
    }
}
```

思路就是从头到尾遍历，每次把当前元素和一个随机选择的元素交换位置。由于元素是随机选择的，所以元素必须放在一个可以随机访问的数据结构中。


* rotate

```java
public static void rotate(List<?> list, int distance) {
    if (list instanceof RandomAccess || list.size() < ROTATE_THRESHOLD)
        rotate1(list, distance);
    else
        rotate2(list, distance);
}

private static <T> void rotate1(List<T> list, int distance) {
    int size = list.size();
    if (size == 0)
        return;
    distance = distance % size;
    if (distance < 0)
        distance += size;
    if (distance == 0)
        return;

    for (int cycleStart = 0, nMoved = 0; nMoved != size; cycleStart++) {
        T displaced = list.get(cycleStart);
        int i = cycleStart;
        do {
            i += distance;
            if (i >= size)
                i -= size;
            displaced = list.set(i, displaced);
            nMoved ++;
        } while (i != cycleStart);
    }
}
```

`rotate` 的作用是，元素的位置由 `i` 变为 `(i + distance) % size` 。从 `for` 循环可以看出，每次选择一个起始点，再将此点位置向后移动 `distance` 个位置，然后将 `i + distance` 位置的元素再向后移动 `distance` ，一直到回到起始点。然后再开始下一个起始点。


* subList

```java
public static int indexOfSubList(List<?> source, List<?> target) {
    int sourceSize = source.size();
    int targetSize = target.size();
    int maxCandidate = sourceSize - targetSize;

    if (sourceSize < INDEXOFSUBLIST_THRESHOLD ||
        (source instanceof RandomAccess&&target instanceof RandomAccess)) {
    nextCand:
        for (int candidate = 0; candidate <= maxCandidate; candidate++) {
            for (int i=0, j=candidate; i<targetSize; i++, j++)
                if (!eq(target.get(i), source.get(j)))
                    continue nextCand;  // Element mismatch, try next cand
            return candidate;  // All elements of candidate matched target
        }
    } else {  // Iterator version of above algorithm
        ListIterator<?> si = source.listIterator();
    nextCand:
        for (int candidate = 0; candidate <= maxCandidate; candidate++) {
            ListIterator<?> ti = target.listIterator();
            for (int i=0; i<targetSize; i++) {
                if (!eq(ti.next(), si.next())) {
                    // Back up source iterator to next candidate
                    for (int j=0; j<i; j++)
                        si.previous();
                    continue nextCand;
                }
            }
            return candidate;
        }
    }
    return -1;  // No candidate matched the target
}
```

查找子列表，思路就是用双重循环进行遍历。外层控制起始点，内层检查从当前起始点开始的元素是否与要检查的子列表中的元素完全一致。

* UnmodifiableCollection

```java
    static class UnmodifiableCollection<E> implements Collection<E>, Serializable {
        private static final long serialVersionUID = 1820017752578914078L;

        final Collection<? extends E> c;

        UnmodifiableCollection(Collection<? extends E> c) {
            if (c==null)
                throw new NullPointerException();
            this.c = c;
        }

        public int size()                   {return c.size();}
        public boolean isEmpty()            {return c.isEmpty();}
        public boolean contains(Object o)   {return c.contains(o);}
        public Object[] toArray()           {return c.toArray();}
        public <T> T[] toArray(T[] a)       {return c.toArray(a);}
        public String toString()            {return c.toString();}

        public Iterator<E> iterator() {
            return new Iterator<E>() {
                private final Iterator<? extends E> i = c.iterator();

                public boolean hasNext() {return i.hasNext();}
                public E next()          {return i.next();}
                public void remove() {
                    throw new UnsupportedOperationException();
                }
            };
        }

        public boolean add(E e) {
            throw new UnsupportedOperationException();
        }
        public boolean remove(Object o) {
            throw new UnsupportedOperationException();
        }

        public boolean containsAll(Collection<?> coll) {
            return c.containsAll(coll);
        }
        public boolean addAll(Collection<? extends E> coll) {
            throw new UnsupportedOperationException();
        }
        public boolean removeAll(Collection<?> coll) {
            throw new UnsupportedOperationException();
        }
        public boolean retainAll(Collection<?> coll) {
            throw new UnsupportedOperationException();
        }
        public void clear() {
            throw new UnsupportedOperationException();
        }
    }
```

这是实现不可变的 `collection`  的方式，通过将可能改变 `collection` 的方法重写为抛出 `UnsupoortedOperationException` 异常，其它可用操作调用原有 `collection` 相应方法的方式完成。    

* synchronizedCollection

```java
static <T> Collection<T> synchronizedCollection(Collection<T> c, Object mutex) {
    return new SynchronizedCollection<>(c, mutex);
}

/**
 * @serial include
 */
static class SynchronizedCollection<E> implements Collection<E>, Serializable {
    private static final long serialVersionUID = 3053995032091335093L;

    final Collection<E> c;  // Backing Collection
    final Object mutex;     // Object on which to synchronize

    SynchronizedCollection(Collection<E> c) {
        if (c==null)
            throw new NullPointerException();
        this.c = c;
        mutex = this;
    }
    SynchronizedCollection(Collection<E> c, Object mutex) {
        this.c = c;
        this.mutex = mutex;
    }

    public int size() {
        synchronized (mutex) {return c.size();}
    }
    public boolean isEmpty() {
        synchronized (mutex) {return c.isEmpty();}
    }
    public boolean contains(Object o) {
        synchronized (mutex) {return c.contains(o);}
    }
    public Object[] toArray() {
        synchronized (mutex) {return c.toArray();}
    }
    public <T> T[] toArray(T[] a) {
        synchronized (mutex) {return c.toArray(a);}
    }

    public Iterator<E> iterator() {
        return c.iterator(); // Must be manually synched by user!
    }

    public boolean add(E e) {
        synchronized (mutex) {return c.add(e);}
    }
    public boolean remove(Object o) {
        synchronized (mutex) {return c.remove(o);}
    }

    public boolean containsAll(Collection<?> coll) {
        synchronized (mutex) {return c.containsAll(coll);}
    }
    public boolean addAll(Collection<? extends E> coll) {
        synchronized (mutex) {return c.addAll(coll);}
    }
    public boolean removeAll(Collection<?> coll) {
        synchronized (mutex) {return c.removeAll(coll);}
    }
    public boolean retainAll(Collection<?> coll) {
        synchronized (mutex) {return c.retainAll(coll);}
    }
    public void clear() {
        synchronized (mutex) {c.clear();}
    }
    public String toString() {
        synchronized (mutex) {return c.toString();}
    }
    private void writeObject(ObjectOutputStream s) throws IOException {
        synchronized (mutex) {s.defaultWriteObject();}
    }
}
```

好吧，所谓的同步的，也就是线程安全的 `collection`，其实就是把每个方法放在了 `synchronized` 块中。

* checkedCollection

将一个普通的 `collection` 变成一个类型安全的 `collection`，也就是说，在你试图将一个类型不正确的元素插入 `collection` 时，会抛出异常。

```java
static class CheckedCollection<E> implements Collection<E>, Serializable {
    private static final long serialVersionUID = 1578914078182001775L;

    final Collection<E> c;
    final Class<E> type;
    
    void typeCheck(Object o) {
        if (o != null && !type.isInstance(o))
            throw new ClassCastException(badElementMsg(o));
    }
    
    CheckedCollection(Collection<E> c, Class<E> type) {
        if (c==null || type == null)
            throw new NullPointerException();
        this.c = c;
        this.type = type;
    }
    
    public int size()                 { return c.size(); }
    public boolean isEmpty()          { return c.isEmpty(); }
    
    ...
    
    public boolean add(E e) {
        typeCheck(e);
        return c.add(e);
    }
```

构造函数会要求传入一个 `type` 参数，然后，在使用 `add` 添加元素时，会进行类型检查。类型检查会调用  `type.isInstance` 进行检查，如果无法通过检查，抛出 `ClassCastException` 异常。


后继一系列 `CheckedXXX` 都是 `CheckedCollection` 的子类，例如：

```java
static class CheckedSet<E> extends CheckedCollection<E>
                             implements Set<E>, Serializable
{
    private static final long serialVersionUID = 4694047833775013803L;

    CheckedSet(Set<E> s, Class<E> elementType) { super(s, elementType); }

    public boolean equals(Object o) { return o == this || c.equals(o); }
    public int hashCode()           { return c.hashCode(); }
}
```

* emptyIterator

```java
public static <T> Iterator<T> emptyIterator() {
    return (Iterator<T>) EmptyIterator.EMPTY_ITERATOR;
}

private static class EmptyIterator<E> implements Iterator<E> {
    static final EmptyIterator<Object> EMPTY_ITERATOR
        = new EmptyIterator<>();

    public boolean hasNext() { return false; }
    public E next() { throw new NoSuchElementException(); }
    public void remove() { throw new IllegalStateException(); }
}
```

有一系列 `EmptyXXXIterator`，实现方式都很类型，定义一个 `static final` 类型的成员变量，再实现相应的方法。

*  singletonIterator

```java
public static <T> Set<T> singleton(T o) {
    return new SingletonSet<>(o);
}

static <E> Iterator<E> singletonIterator(final E e) {
    return new Iterator<E>() {
        private boolean hasNext = true;
        public boolean hasNext() {
            return hasNext;
        }
        public E next() {
            if (hasNext) {
                hasNext = false;
                return e;
            }
            throw new NoSuchElementException();
        }
        public void remove() {
            throw new UnsupportedOperationException();
        }
    };
}
```

除了 `EmptyIterator` 外，还有 `singletonIterator`，它们只包含一个元素。这是为了0个和1个元素的 `collection` 作的特殊处理么？为什么要实现这两个系列的类呢？

* CopiesList

```java
private static class CopiesList<E>
    extends AbstractList<E>
    implements RandomAccess, Serializable
{
    private static final long serialVersionUID = 2739099268398711800L;

    final int n;
    final E element;

    CopiesList(int n, E e) {
        assert n >= 0;
        this.n = n;
        element = e;
    }

    public int size() {
        return n;
    }

    public boolean contains(Object obj) {
        return n != 0 && eq(obj, element);
    }

    public int indexOf(Object o) {
        return contains(o) ? 0 : -1;
    }

    public int lastIndexOf(Object o) {
        return contains(o) ? n - 1 : -1;
    }

    public E get(int index) {
        if (index < 0 || index >= n)
            throw new IndexOutOfBoundsException("Index: "+index+
                                                ", Size: "+n);
        return element;
    }

    public Object[] toArray() {
        final Object[] a = new Object[n];
        if (element != null)
            Arrays.fill(a, 0, n, element);
        return a;
    }

    public <T> T[] toArray(T[] a) {
        final int n = this.n;
        if (a.length < n) {
            a = (T[])java.lang.reflect.Array
                .newInstance(a.getClass().getComponentType(), n);
            if (element != null)
                Arrays.fill(a, 0, n, element);
        } else {
            Arrays.fill(a, 0, n, element);
            if (a.length > n)
                a[n] = null;
        }
        return a;
    }

    public List<E> subList(int fromIndex, int toIndex) {
        if (fromIndex < 0)
            throw new IndexOutOfBoundsException("fromIndex = " + fromIndex);
        if (toIndex > n)
            throw new IndexOutOfBoundsException("toIndex = " + toIndex);
        if (fromIndex > toIndex)
            throw new IllegalArgumentException("fromIndex(" + fromIndex +
                                               ") > toIndex(" + toIndex + ")");
        return new CopiesList<>(toIndex - fromIndex, element);
    }
}
```

这个很有趣，名义上是 `n` 个相同元素的 `collection`，实际上只保存一个元素，再通过对方法的特殊实现，对外伪装成有 `n` 个元素。