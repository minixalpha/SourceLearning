# OpenJDK 源码阅读之 BitSet

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.util.BitSet
```

* 定义 

```java
public class BitSet
extends Object
implements Cloneable, Serializable
```

*  要点

`BitSet` 类用来支持位操作，给它一个 `size` ，就会返回一个对象，代表 `size` 个位。可以完成“与或非”操作。


## 实现 

试想一下，`long` 最多也就 64 位，假如我们想对 1000 位进行一些运算，要如何实现呢？这个类就告诉我们怎么用一个数组，去实现位操作。

* 数据 

```java
private long[] words;
```

内部使用 `long` 类型的数组来存储数据。

* 初始化 

```java
public BitSet(int nbits) {
    // nbits can't be negative; size 0 is OK
    if (nbits < 0)
        throw new NegativeArraySizeException("nbits < 0: " + nbits);

    initWords(nbits);
    sizeIsSticky = true;
}

private void initWords(int nbits) {
    words = new long[wordIndex(nbits-1) + 1];
}

private static int wordIndex(int bitIndex) {
    return bitIndex >> ADDRESS_BITS_PER_WORD;
}
```

初始化会根据的位数决定要申请多大的数组，`long` 类型是 64 位，所以你如果 `nbits` 是 `1~64`，你只需要一个长度为1的数组就好。

* 扩充策略

要是数组不够用了，就要进行扩充，下面的函数会根据申请的 `long` 元素个数，经过与当前元素个数2倍的比较进行扩充。

```java
private void ensureCapacity(int wordsRequired) {
    if (words.length < wordsRequired) {
        // Allocate larger of doubled size or required size
        int request = Math.max(2 * words.length, wordsRequired);
        words = Arrays.copyOf(words, request);
        sizeIsSticky = false;
    }
}
```

* 位翻转

```java
public void flip(int bitIndex) {
    if (bitIndex < 0)
        throw new IndexOutOfBoundsException("bitIndex < 0: " + bitIndex);

    int wordIndex = wordIndex(bitIndex);
    expandTo(wordIndex);

    words[wordIndex] ^= (1L << bitIndex);

    recalculateWordsInUse();
    checkInvariants();
}
```

先根据索引位置 `bitIndex` 计算出相应的位在数组哪个元素里，然后再将 1 左移 `bitIndex`  位后与此元素作异或运算。注意 `bitIndex` 如果超过了 64 位，会又循环回来，比如  `1L << 69` 其实和 `1L << 5` 是一样的，只不过异或的时候，一个与 `words[1]` 异或，一个与 `words[0]`。

类中还有其它位操作，比如置1,清0,只是和 `flip` 的位操作符不同。

还有一类是区间内翻转，这需要首先临到一个相应区间全为1的数字，再与 `words` 相应元素作运算。

```java
public void flip(int fromIndex, int toIndex) {
    checkRange(fromIndex, toIndex);

    if (fromIndex == toIndex)
        return;

    int startWordIndex = wordIndex(fromIndex);
    int endWordIndex   = wordIndex(toIndex - 1);
    expandTo(endWordIndex);

    long firstWordMask = WORD_MASK << fromIndex;
    long lastWordMask  = WORD_MASK >>> -toIndex;
    if (startWordIndex == endWordIndex) {
        // Case 1: One word
        words[startWordIndex] ^= (firstWordMask & lastWordMask);
    } else {
        // Case 2: Multiple words
        // Handle first word
        words[startWordIndex] ^= firstWordMask;

        // Handle intermediate words, if any
        for (int i = startWordIndex+1; i < endWordIndex; i++)
            words[i] ^= WORD_MASK;

        // Handle last word
        words[endWordIndex] ^= lastWordMask;
    }

    recalculateWordsInUse();
    checkInvariants();
}
```

如果区间跨越多个数组元素，还需要把中间的数个数组元素内容全部翻转。

* AND 操作

```java
public void and(BitSet set) {
    if (this == set)
        return;

    while (wordsInUse > set.wordsInUse)
        words[--wordsInUse] = 0;

    // Perform logical AND on words in common
    for (int i = 0; i < wordsInUse; i++)
        words[i] &= set.words[i];

    recalculateWordsInUse();
    checkInvariants();
}
```

从这个函数体会一下，两个 `BitSet` 对象之间的 `AND` 操作如何进行，其实就是对应的数组元素之间作 `AND` 操作就行。

* hashCode

```java
public int hashCode() {
    long h = 1234;
    for (int i = wordsInUse; --i >= 0; )
        h ^= words[i] * (i + 1);

    return (int)((h >> 32) ^ h);
}
```

计算哈希值的操作，说实话，我是不太明白为什么这样算哈希值的，为什么这样能减少不同 `BitSet` 之间的碰撞呢？

剩下的东西我也不想分析了，总之，需要把握整体的思路，就是如何用一个数组去实现位操作，每次操作需要弄清楚，在数组的哪些元素上操作，与什么数字作位操作，做什么位操作。