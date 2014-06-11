# OpenJDK 源码阅读之 TimSort

标签（空格分隔）： 源代码阅读 Java 封神之路


## 概要

这个类在 Oracle 的官方文档里是查不到的，但是确实在 `OpenJDK` 的源代码里出现了，`Arrays` 中的 `sort` 函数用到了这个用于排序的类。它是归并排序(merge sort) 与插入排序(insertion sort) ，对于已经部分排序的数组，时间复杂度远低于 `O(n log(n))`，最好可达 `O(n)`，对于随机排序的数组，时间复杂度为 `O(nlog(n))`，平均时间复杂度 `O(nlog(n))`。强烈建议在看此文前观看 Youtube 上的 [可视化Timsort](http://www.youtube.com/watch?v=NVIjHj-lrT4)，看完后马上就会对算法的执行过程有一个感性的了解。然后，可以阅读 Wikipeida 词条：[Timsort](http://en.wikipedia.org/wiki/Timsort)。 这个排序算法在 Java SE 7, Android, GNU Octave 中都得到了应用。

此类是对 `Python` 中，由 `Tim Peters` 实现的排序算法的改写。实现来自：[listobject.c](http://svn.python.org/projects/python/trunk/Objects/listobject.c).

原始论文来自：

```
"Optimistic Sorting and Information Theoretic Complexity" Peter 
McIlroy SODA (Fourth Annual ACM-SIAM Symposium on Discrete 
Algorithms), pp 467-474, Austin, Texas, 25-27 January 1993.
```


## 实现

* sort


```java
static <T> void sort(T[] a, int lo, int hi, Comparator<? super T> c) {
    if (c == null) {
        Arrays.sort(a, lo, hi);
        return;
    }

    rangeCheck(a.length, lo, hi);
    int nRemaining  = hi - lo;
    if (nRemaining < 2)
        return;  // Arrays of size 0 and 1 are always sorted

    // If array is small, do a "mini-TimSort" with no merges
    if (nRemaining < MIN_MERGE) {
        int initRunLen = countRunAndMakeAscending(a, lo, hi, c);
        binarySort(a, lo, hi, lo + initRunLen, c);
        return;
    }

    /**
     * March over the array once, left to right, finding natural runs,
     * extending short natural runs to minRun elements, and merging runs
     * to maintain stack invariant.
     */
    TimSort<T> ts = new TimSort<>(a, c);
    int minRun = minRunLength(nRemaining);
    do {
        // Identify next run
        int runLen = countRunAndMakeAscending(a, lo, hi, c);

        // If run is short, extend to min(minRun, nRemaining)
        if (runLen < minRun) {
            int force = nRemaining <= minRun ? nRemaining : minRun;
            binarySort(a, lo, lo + force, lo + runLen, c);
            runLen = force;
        }

        // Push run onto pending-run stack, and maybe merge
        ts.pushRun(lo, runLen);
        ts.mergeCollapse();

        // Advance to find next run
        lo += runLen;
        nRemaining -= runLen;
    } while (nRemaining != 0);

    // Merge all remaining runs to complete sort
    assert lo == hi;
    ts.mergeForceCollapse();
    assert ts.stackSize == 1;
}
```

下面分段解释：

```java
if (c == null) {
    Arrays.sort(a, lo, hi);
    return;
}
```

如果没有提供 `Comparaotr` 的话，会调用 `Arrays.sort` 中的函数，背后其实又会调用  `ComparableTimSort`，它是对没有提供 `Comparator` ，但是实现了 `Comparable` 的元素进行排序，算法和这里的是一样的，就是元素比较方法不一样。

后面是算法的主体：

```java
    if (nRemaining < 2)
        return;  // Arrays of size 0 and 1 are always sorted

    // If array is small, do a "mini-TimSort" with no merges
    if (nRemaining < MIN_MERGE) {
        int initRunLen = countRunAndMakeAscending(a, lo, hi, c);
        binarySort(a, lo, hi, lo + initRunLen, c);
        return;
    }

```

1. 如果元素个数小于2,直接返回，因为这两个元素已经排序了
2. 如果元素个数小于一个阈值（默认为)，调用 `binarySort`，这是一个不包含合并操作的 `mini-TimSort`。
3. 在关键的 `do-while` 循环中，不断地进行排序，合并，排序，合并，一直到所有数据都处理完。  

```java
    TimSort<T> ts = new TimSort<>(a, c);
    int minRun = minRunLength(nRemaining);
    do {
    
        ...
        
    } while (nRemaining != 0);
```


* minRunLength

这个函数会找出 `run` 的最小长度，少于这个长度就需要对其进行扩展。

```java
static int minRunLength(int n) {
        assert n >= 0;
        int r = 0;      // Becomes 1 if any 1 bits are shifted off
        while (n >= MIN_MERGE) {
            r |= (n & 1);
            n >>= 1;
        }
        return n + r;
    }
```

先看看 n 与 minRunLength(n) 对应关系 

```
0 0
1 1
2 2
3 3
4 4
5 5
6 6
7 7
8 8
9 9
10 10
11 11
12 12
13 13
14 14
15 15
16 16
17 17
18 18
19 19
20 20
21 21
22 22
23 23
24 24
25 25
26 26
27 27
28 28
29 29
30 30
31 31
32 16
33 17
34 17
35 18
36 18
37 19
38 19
39 20
40 20
41 21
42 21
43 22
44 22
45 23
46 23
47 24
48 24
49 25
50 25
51 26
52 26
53 27
54 27
55 28
56 28
57 29
58 29
59 30
60 30
61 31
62 31
63 32
64 16
65 17
66 17
67 17
68 17
69 18
70 18
71 18
72 18
73 19
74 19
75 19
76 19
77 20
78 20
79 20
80 20
81 21
82 21
83 21
84 21
85 22
86 22
87 22
88 22
89 23
90 23
91 23
92 23
93 24
94 24
95 24
96 24
97 25
98 25
99 25

...
```

看这个估计可以猜出来函数的功能了，下面解释一下。

这个函数根据 n 计算出对应的 `natural run` 的最小长度。`MIN_MERGE` 默认为 `32`，如果n小于此值，那么返回 `n` 本身。否则会将 `n` 不断地右移，直到少于 `MIN_MERGE`，同时记录一个 `r` 值，r 代表最后一次移位n时，n最低位是0还是1。 最后返回 `n + r`，这也意味着只保留最高的 5 位，再加上第六位。

* do-while

我们再看看 `do-while` 中发生了什么。

```java
   TimSort<T> ts = new TimSort<>(a, c);
    int minRun = minRunLength(nRemaining);
    do {
        // Identify next run
        int runLen = countRunAndMakeAscending(a, lo, hi, c);

        // If run is short, extend to min(minRun, nRemaining)
        if (runLen < minRun) {
            int force = nRemaining <= minRun ? nRemaining : minRun;
            binarySort(a, lo, lo + force, lo + runLen, c);
            runLen = force;
        }

        // Push run onto pending-run stack, and maybe merge
        ts.pushRun(lo, runLen);
        ts.mergeCollapse();

        // Advance to find next run
        lo += runLen;
        nRemaining -= runLen;
    } while (nRemaining != 0);
```

`countRunAndMakeAscending` 会找到一个 `run` ，这个 `run` 必须是已经排序的，并且函数会保证它为升序，也就是说，如果找到的是一个降序的，会对其进行翻转。

简单看一眼这个函数：

* countRunAndMakeAscending

```java
private static <T> int countRunAndMakeAscending(T[] a, int lo, int hi,
                                                Comparator<? super T> c) {
    assert lo < hi;
    int runHi = lo + 1;
    if (runHi == hi)
        return 1;

    // Find end of run, and reverse range if descending
    if (c.compare(a[runHi++], a[lo]) < 0) { // Descending
        while (runHi < hi && c.compare(a[runHi], a[runHi - 1]) < 0)
            runHi++;
        reverseRange(a, lo, runHi);
    } else {                              // Ascending
        while (runHi < hi && c.compare(a[runHi], a[runHi - 1]) >= 0)
            runHi++;
    }

    return runHi - lo;
}
```

注意其中的 `reverseRange` 就是我们说的翻转。

现在，有必要看一下 `binarySort` 了。


```java
private static <T> void binarySort(T[] a, int lo, int hi, int start,
                                   Comparator<? super T> c) {
    assert lo <= start && start <= hi;
    if (start == lo)
        start++;
    for ( ; start < hi; start++) {
        T pivot = a[start];

        // Set left (and right) to the index where a[start] (pivot) belongs
        int left = lo;
        int right = start;
        assert left <= right;
        /*
         * Invariants:
         *   pivot >= all in [lo, left).
         *   pivot <  all in [right, start).
         */
        while (left < right) {
            int mid = (left + right) >>> 1;
            if (c.compare(pivot, a[mid]) < 0)
                right = mid;
            else
                left = mid + 1;
        }
        assert left == right;

        /*
         * The invariants still hold: pivot >= all in [lo, left) and
         * pivot < all in [left, start), so pivot belongs at left.  Note
         * that if there are elements equal to pivot, left points to the
         * first slot after them -- that's why this sort is stable.
         * Slide elements over to make room for pivot.
         */
        int n = start - left;  // The number of elements to move
        // Switch is just an optimization for arraycopy in default case
        switch (n) {
            case 2:  a[left + 2] = a[left + 1];
            case 1:  a[left + 1] = a[left];
                     break;
            default: System.arraycopy(a, left, a, left + 1, n);
        }
        a[left] = pivot;
    }
}
```

我们都听说过 `binarySearch` ，但是这个  `binarySort` 又是什么呢？ `binarySort` 对数组 `a[lo:hi]` 进行排序，并且 `a[lo:start]` 是已经排好序的。算法的思路是对 `a[start:hi]` 中的元素，每次使用 `binarySearch` 为它在 `a[lo:start]` 中找到相应位置，并插入。

回到 `do-while` 循环中，看看 `binarySearch` 的作用：

```java
  // If run is short, extend to min(minRun, nRemaining)
    if (runLen < minRun) {
        int force = nRemaining <= minRun ? nRemaining : minRun;
        binarySort(a, lo, lo + force, lo + runLen, c);
        runLen = force;
    }
```

所以，我们明白了，`binarySort` 对 `run` 进行了扩展，并且扩展后，`run` 仍然是有序的。

随后：

```java
   // Push run onto pending-run stack, and maybe merge
    ts.pushRun(lo, runLen);
    ts.mergeCollapse();

    // Advance to find next run
    lo += runLen;
    nRemaining -= runLen;
```

当前的 `run` 位于 `a[lo:runLen]` ，将其入栈，然后将栈中的 `run` 合并。

* pushRun

```java
private void pushRun(int runBase, int runLen) {
    this.runBase[stackSize] = runBase;
    this.runLen[stackSize] = runLen;
    stackSize++;
}
```

入栈过程简单明了，不解释。

再看另一个关键函数，合并操作。如果你看过文章开头提到的对 `Timsort` 进行可视化的视频，一定会对合并操作印象深刻。它会把已经排序的 `run` 合并成一个大 `run`，此大 `run` 也会排好序。

```java
/**
 * Examines the stack of runs waiting to be merged and merges adjacent runs
 * until the stack invariants are reestablished:
 *
 *     1. runLen[i - 3] > runLen[i - 2] + runLen[i - 1]
 *     2. runLen[i - 2] > runLen[i - 1]
 *
 * This method is called each time a new run is pushed onto the stack,
 * so the invariants are guaranteed to hold for i < stackSize upon
 * entry to the method.
 */
private void mergeCollapse() {
    while (stackSize > 1) {
        int n = stackSize - 2;
        if (n > 0 && runLen[n-1] <= runLen[n] + runLen[n+1]) {
            if (runLen[n - 1] < runLen[n + 1])
                n--;
            mergeAt(n);
        } else if (runLen[n] <= runLen[n + 1]) {
            mergeAt(n);
        } else {
            break; // Invariant is established
        }
    }
}
```

合并的过程会一直循环下去，一直到注释里提到的循环不变式得到满足。

* mergeAt

`mergeAt` 会把栈顶的两个 `run` 合并起来：


```java
   /**
     * Merges the two runs at stack indices i and i+1.  Run i must be
     * the penultimate or antepenultimate run on the stack.  In other words,
     * i must be equal to stackSize-2 or stackSize-3.
     *
     * @param i stack index of the first of the two runs to merge
 */
private void mergeAt(int i) {
    assert stackSize >= 2;
    assert i >= 0;
    assert i == stackSize - 2 || i == stackSize - 3;

    int base1 = runBase[i];
    int len1 = runLen[i];
    int base2 = runBase[i + 1];
    int len2 = runLen[i + 1];
    assert len1 > 0 && len2 > 0;
    assert base1 + len1 == base2;

    /*
     * Record the length of the combined runs; if i is the 3rd-last
     * run now, also slide over the last run (which isn't involved
     * in this merge).  The current run (i+1) goes away in any case.
     */
    runLen[i] = len1 + len2;
    if (i == stackSize - 3) {
        runBase[i + 1] = runBase[i + 2];
        runLen[i + 1] = runLen[i + 2];
    }
    stackSize--;

    /*
     * Find where the first element of run2 goes in run1. Prior elements
     * in run1 can be ignored (because they're already in place).
     */
    int k = gallopRight(a[base2], a, base1, len1, 0, c);
    assert k >= 0;
    base1 += k;
    len1 -= k;
    if (len1 == 0)
        return;

    /*
     * Find where the last element of run1 goes in run2. Subsequent elements
     * in run2 can be ignored (because they're already in place).
     */
    len2 = gallopLeft(a[base1 + len1 - 1], a, base2, len2, len2 - 1, c);
    assert len2 >= 0;
    if (len2 == 0)
        return;

    // Merge remaining runs, using tmp array with min(len1, len2) elements
    if (len1 <= len2)
        mergeLo(base1, len1, base2, len2);
    else
        mergeHi(base1, len1, base2, len2);
}
```

由于要合并的两个 `run` 是已经排序的，所以合并的时候，有会特别的技巧。假设两个 `run` 是 `run1,run2` ，先用 `gallopRight` 在 `run1` 里使用 `binarySearch` 查找  `run2 首元素` 的位置 `k`, 那么 `run1` 中 `k` 前面的元素就是合并后最小的那些元素。然后，在 `run2` 中查找 `run1 尾元素` 的位置 `len2` ，那么 `run2` 中 `len2` 后面的那些元素就是合并后最大的那些元素。最后，根据 `len1` 与 `len2` 大小，调用  `mergeLo` 或者 `mergeHi` 将剩余元素合并。

`gallop` 和 `merge` 就不展开了。

另外，强烈推荐阅读文后的两篇文章，第一篇可以看到 JDK7 中更换排序算法后可能引发的问题，另外，也会介绍源代码，并给出具体的例子。第二篇会告诉你如何对一个 `MergeSort` 进行优化，介绍了 `TimSort` 背后的思想。

## 推荐阅读

* [TimSort in Java 7](http://www.lifebackup.cn/timsort-java7.html)
* [理解timsort](http://blog.kongfy.com/2012/10/%E8%AF%91%E7%90%86%E8%A7%A3timsort-%E7%AC%AC%E4%B8%80%E9%83%A8%E5%88%86%EF%BC%9A%E9%80%82%E5%BA%94%E6%80%A7%E5%BD%92%E5%B9%B6%E6%8E%92%E5%BA%8Fadaptive-mergesort/)