# OpenJDK 源码阅读之 Arrays

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
java.util.Arrays
```

* 定义 

```java
public class Arrays
extends Object
```

* 要点

此类主要是提供了一些操作数组的方法，比如排序啊，搜索啊。也提供一个工厂，用于将数组当成一个 `List`。

## 实现

* quick sort

```java
public static void sort(int[] a) {
    DualPivotQuicksort.sort(a);
}
```

`sort` 使用了 `util` 中的另一个类中的方法，`DualPivotQuicksort.sort` ，比一般的快排要快。时间复杂度 `O(n log(n))`。

这里并没有使用泛型，而是针对具体类型，调用 `sort`，例如：

```java
public static void sort(float[] a) {
    DualPivotQuicksort.sort(a);
}
```

`DualPivotQuicksort` 的实现细节会在以后具体讲述这个类的源代码时讲。现在只讲这个类中的内容。

* merge sort

```java
private static void mergeSort(Object[] src,
                              Object[] dest,
                              int low, int high, int off,
                              Comparator c) {
    int length = high - low;

    // Insertion sort on smallest arrays
    if (length < INSERTIONSORT_THRESHOLD) {
        for (int i=low; i<high; i++)
            for (int j=i; j>low && c.compare(dest[j-1], dest[j])>0; j--)
                swap(dest, j, j-1);
        return;
    }

    // Recursively sort halves of dest into src
    int destLow  = low;
    int destHigh = high;
    low  += off;
    high += off;
    int mid = (low + high) >>> 1;
    mergeSort(dest, src, low, mid, -off, c);
    mergeSort(dest, src, mid, high, -off, c);

    // If list is already sorted, just copy from src to dest.  This is an
    // optimization that results in faster sorts for nearly ordered lists.
    if (c.compare(src[mid-1], src[mid]) <= 0) {
       System.arraycopy(src, low, dest, destLow, length);
       return;
    }

    // Merge sorted halves (now in src) into dest
    for(int i = destLow, p = low, q = mid; i < destHigh; i++) {
        if (q >= high || p < mid && c.compare(src[p], src[q]) <= 0)
            dest[i] = src[p++];
        else
            dest[i] = src[q++];
    }
}
```

当数组元素个数少时，用插入排序，插入排序的原理是，在一个已经排序的列表中插入一个元素，使得插入后，列表仍然是排序的。具体到代码，每一次，内层循环开始前，[low,i-1] 的所有元素是已经排序的，内层循环执行后，[low, i] 的所有元素是已经排序的。i最终会等于 high-1，所有最后一层内层循环后，[low, high-1]中所有元素都是已经排序的。

合并排序 `merge sort` 的原理是，通过递归，先使得前一半元素，和后一半元素使用合并排序排好，然后将他们合并，合并后，整个列表是有序的。合并时，两部分元素上面各有一个指针指向当前元素，每次将两个指针指向的元素进行比较，并选择其中一个，复制到目标数组，然后将其指针前移。如此循环。

注意代码中有一个优化，如果两半元素排序后，前一半的最大元素小于后一半的最小元素，那么不用比较，直接合并。

不过这个函数已经要废弃了，现在用的是 `sort` ，即使用快排。

* TimSort

```java
public static <T> void sort(T[] a, Comparator<? super T> c) {
    if (LegacyMergeSort.userRequested)
        legacyMergeSort(a, c);
    else
        TimSort.sort(a, c);
}
```

对提供了 `Comparator` 的排序调用，这里使用了 `TimSort`，根据注释中的解释，这是采用 `Tim Peters` 在 `Python` 的 `list` 中的排序，原始论文参见：`Peter McIlroy's "Optimistic Sorting and Information Theoretic Complexity", in Proceedings of the Fourth Annual ACM-SIAM Symposium on Discrete Algorithms, pp 467-474, January 1993`。这个算法对已经大致排好序的列表，花费的时间比 `O(n log(n))` 少很多，对随机的数据，退化为 `merge sort`。

* binarySearch

```java
// Like public version, but without range checks.
private static int binarySearch0(long[] a, int fromIndex, int toIndex,
                                 long key) {
    int low = fromIndex;
    int high = toIndex - 1;

    while (low <= high) {
        int mid = (low + high) >>> 1;
        long midVal = a[mid];

        if (midVal < key)
            low = mid + 1;
        else if (midVal > key)
            high = mid - 1;
        else
            return mid; // key found
    }
    return -(low + 1);  // key not found.
}
```

对已经排序的元素，可以使用二分搜索，一次可以排除一半元素，复杂度 `O(log(n))`。

可以注意到，这也是针对具体类型编写的。如果使用泛型，那么需要告诉算法如何比较元素。这样，基本类型就需要使用对应的类来表示，而对数组而言，基本类型无法自动转化成对应的类。真是。。。哎。。。。Java 为什么要保留基本类型呢？


* equals

```java
public static boolean equals(long[] a, long[] a2) {
    if (a==a2)
        return true;
    if (a==null || a2==null)
        return false;

    int length = a.length;
    if (a2.length != length)
        return false;

    for (int i=0; i<length; i++)
        if (a[i] != a2[i])
            return false;

    return true;
}
```

遍历比较，毫无疑问，又是每种类型，一个函数。保留基本类型真是正确的选择吗？

* fill

```java
public static void fill(long[] a, long val) {
    for (int i = 0, len = a.length; i < len; i++)
        a[i] = val;
}
```

使用一个元素，去填充数组的所有元素。

* copyOf

```java
    public static short[] copyOf(short[] original, int newLength) {
        short[] copy = new short[newLength];
        System.arraycopy(original, 0, copy, 0,
                         Math.min(original.length, newLength));
        return copy;
    }
```

使用 `System.arraycopy` 复制，方便，省心，不自己循环！

* asList

```java
public static <T> List<T> asList(T... a) {
    return new ArrayList<>(a);
}
```

就是直接生成一个 `ArrayList`，只不过这个 `ArrayList` 是 `Arrays` 中的私有类。


* ArrayList

```java
private static class ArrayList<E> extends AbstractList<E>
    implements RandomAccess, java.io.Serializable
{
    private static final long serialVersionUID = -2764017481108945198L;
    private final E[] a;

    ArrayList(E[] array) {
        if (array==null)
            throw new NullPointerException();
        a = array;
    }

    public int size() {
        return a.length;
    }

    public Object[] toArray() {
        return a.clone();
    }

    public <T> T[] toArray(T[] a) {
        int size = size();
        if (a.length < size)
            return Arrays.copyOf(this.a, size,
                                 (Class<? extends T[]>) a.getClass());
        System.arraycopy(this.a, 0, a, 0, size);
        if (a.length > size)
            a[size] = null;
        return a;
    }

    public E get(int index) {
        return a[index];
    }

    public E set(int index, E element) {
        E oldValue = a[index];
        a[index] = element;
        return oldValue;
    }

    public int indexOf(Object o) {
        if (o==null) {
            for (int i=0; i<a.length; i++)
                if (a[i]==null)
                    return i;
        } else {
            for (int i=0; i<a.length; i++)
                if (o.equals(a[i]))
                    return i;
        }
        return -1;
    }

    public boolean contains(Object o) {
        return indexOf(o) != -1;
    }
}
```

因为之前分析过 `ArrayList` ，这个是个针对数组的简单版本，就不具体分析了。


* hashCode

```java
public static int hashCode(long a[]) {
    if (a == null)
        return 0;

    int result = 1;
    for (long element : a) {
        int elementHash = (int)(element ^ (element >>> 32));
        result = 31 * result + elementHash;
    }

    return result;
}
```

又看到了常见的 `hashcode` 模式： 

```
result = 31 * result + elementHash;
```

不过那个  `element ^ (element >>> 32)` 是嘛意思，注意这里的 `element` 是 `long`  类型，64位，这里是将高 32 位与低 32 位作了 `^` 运算，再转型成 `int` 。这是因为  `hashCode` 是 32 位的。再看看 `int` 数组的 `hashCode` 就正常多了。

```java
public static int hashCode(int a[]) {
    if (a == null)
        return 0;

    int result = 1;
    for (int element : a)
        result = 31 * result + element;

    return result;
}
```

另外， `boolean` 类型的数组猜一猜  `hashCode` 如何确定？

```java
public static int hashCode(boolean a[]) {
    if (a == null)
        return 0;

    int result = 1;
    for (boolean element : a)
        result = 31 * result + (element ? 1231 : 1237);

    return result;
}
```

这是将 `true` 和 `false` 变成了两个数字，`1231`, `1237`。为什么要换成这两个数字呢？还不太清楚，不过总的原因就是减少碰撞，看来有必要研究一下哈希函数的设计了。


* deepXXX

先看看 `deepHashCode`:


```java
public static int deepHashCode(Object a[]) {
    if (a == null)
        return 0;

    int result = 1;

    for (Object element : a) {
        int elementHash = 0;
        if (element instanceof Object[])
            elementHash = deepHashCode((Object[]) element);
        else if (element instanceof byte[])
            elementHash = hashCode((byte[]) element);
        else if (element instanceof short[])
            elementHash = hashCode((short[]) element);
        else if (element instanceof int[])
            elementHash = hashCode((int[]) element);
        else if (element instanceof long[])
            elementHash = hashCode((long[]) element);
        else if (element instanceof char[])
            elementHash = hashCode((char[]) element);
        else if (element instanceof float[])
            elementHash = hashCode((float[]) element);
        else if (element instanceof double[])
            elementHash = hashCode((double[]) element);
        else if (element instanceof boolean[])
            elementHash = hashCode((boolean[]) element);
        else if (element != null)
            elementHash = element.hashCode();

        result = 31 * result + elementHash;
    }

    return result;
}
```

这是需要根据 `Object` 数组中的每一个的具体类型，来决定当前元素的哈希值。

同理，可以看看 `deepEquals`:

```java
public static boolean deepEquals(Object[] a1, Object[] a2) {
    if (a1 == a2)
        return true;
    if (a1 == null || a2==null)
        return false;
    int length = a1.length;
    if (a2.length != length)
        return false;

    for (int i = 0; i < length; i++) {
        Object e1 = a1[i];
        Object e2 = a2[i];

        if (e1 == e2)
            continue;
        if (e1 == null)
            return false;

        // Figure out whether the two elements are equal
        boolean eq = deepEquals0(e1, e2);

        if (!eq)
            return false;
    }
    return true;
}

static boolean deepEquals0(Object e1, Object e2) {
    assert e1 != null;
    boolean eq;
    if (e1 instanceof Object[] && e2 instanceof Object[])
        eq = deepEquals ((Object[]) e1, (Object[]) e2);
    else if (e1 instanceof byte[] && e2 instanceof byte[])
        eq = equals((byte[]) e1, (byte[]) e2);
    else if (e1 instanceof short[] && e2 instanceof short[])
        eq = equals((short[]) e1, (short[]) e2);
    else if (e1 instanceof int[] && e2 instanceof int[])
        eq = equals((int[]) e1, (int[]) e2);
    else if (e1 instanceof long[] && e2 instanceof long[])
        eq = equals((long[]) e1, (long[]) e2);
    else if (e1 instanceof char[] && e2 instanceof char[])
        eq = equals((char[]) e1, (char[]) e2);
    else if (e1 instanceof float[] && e2 instanceof float[])
        eq = equals((float[]) e1, (float[]) e2);
    else if (e1 instanceof double[] && e2 instanceof double[])
        eq = equals((double[]) e1, (double[]) e2);
    else if (e1 instanceof boolean[] && e2 instanceof boolean[])
        eq = equals((boolean[]) e1, (boolean[]) e2);
    else
        eq = e1.equals(e2);
    return eq;
}
```

同样需要根据类型来比较每个元素是否相等。

* toString

```java
public static String toString(long[] a) {
    if (a == null)
        return "null";
    int iMax = a.length - 1;
    if (iMax == -1)
        return "[]";

    StringBuilder b = new StringBuilder();
    b.append('[');
    for (int i = 0; ; i++) {
        b.append(a[i]);
        if (i == iMax)
            return b.append(']').toString();
        b.append(", ");
    }
}
```

同样，每个基本类型都有相应的函数，使用 `StringBuilder`，具体如何将 `long` 转化成 `String` ，由 `StringBuilder` 来确定。