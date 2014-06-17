# OpenJDK 源码阅读之 DataInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.FilterInputStream
            java.io.DataInputStream
```

* 定义 

```java
public class DataInputStream
extends FilterInputStream
implements DataInput
```

* 要点

`DataInputStream` 可以从底层的流中读取基本数据类型，例如 `int`, `char` 等等。`DataInputStream` 是非线程安全的，你必须自己保证处理线程安全相关的细节。


## 实现

* 初始化 

```java
public DataInputStream(InputStream in) {
    super(in);
}
```

需要一个底层的流，告诉 `DataInputStream` 从哪里读取数据。


下面看看是如何读取各种数据类型的 

* readBoolean

```java
public final boolean readBoolean() throws IOException {
    int ch = in.read();
    if (ch < 0)
        throw new EOFException();
    return (ch != 0);
}
```

可以看出，调用  `in.read()` 读了一个字节，然后根据这个字节是否为0,决定返回 `true/false`。


* readShort

```java
public final short readShort() throws IOException {
    int ch1 = in.read();
    int ch2 = in.read();
    if ((ch1 | ch2) < 0)
        throw new EOFException();
    return (short)((ch1 << 8) + (ch2 << 0));
}
```

`short`  是读入了两个字节，然后拼起来。到这里，思路已经很明显了，就是读取字节，然后把字节转化成相应数据类型。


* readInt

```java
public final int readInt() throws IOException {
    int ch1 = in.read();
    int ch2 = in.read();
    int ch3 = in.read();
    int ch4 = in.read();
    if ((ch1 | ch2 | ch3 | ch4) < 0)
        throw new EOFException();
    return ((ch1 << 24) + (ch2 << 16) + (ch3 << 8) + (ch4 << 0));
}
```

`int` 是拼接了四个字节。由于 `Java` 中，各个基本数据类型的字节数是固定的，所以类型确定了，要读几个字节也就确定了。 

* readLong

`readLong` 和对其它的基本类型的处理不太一样，是先读取到缓冲区里，再作处理。


```java
private byte readBuffer[] = new byte[8];
public final long readLong() throws IOException {
    readFully(readBuffer, 0, 8);
    return (((long)readBuffer[0] << 56) +
            ((long)(readBuffer[1] & 255) << 48) +
            ((long)(readBuffer[2] & 255) << 40) +
            ((long)(readBuffer[3] & 255) << 32) +
            ((long)(readBuffer[4] & 255) << 24) +
            ((readBuffer[5] & 255) << 16) +
            ((readBuffer[6] & 255) <<  8) +
            ((readBuffer[7] & 255) <<  0));
}
```

* readFloat

前面的都是类似整数的，比较好拼接，到浮点数这，就无法直接拼接了。

```java
public final float readFloat() throws IOException {
    return Float.intBitsToFloat(readInt());
}
```

先是按照 `int` 读入，然后调用  `Float` 的方法转换成了 `float` 类型的数据。

* readDouble

`readDouble` 类似 `readFloat` ，只不过会读入 `Long` 类型，这个要看字节数目的对应关系。


```java
public final double readDouble() throws IOException {
    return Double.longBitsToDouble(readLong());
}
```