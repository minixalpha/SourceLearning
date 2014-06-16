# OpenJDK 源码阅读之 InputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
```

* 定义 

```java
public abstract class InputStream
extends Object
implements Closeable
```

* 要点

`InputStream` 类是所有以字节为输入流的类的基类，子类需要实现 `read` 方法以便获取下一个输入的字节。


## 实现 

* read

```
public abstract int read() throws IOException;
```

子类需要实现这个 `read` 方法，返回一个 `0~255` 的数值。

* read

另外，定义了一个多态的  `read`，用于读入数组

```java
public int read(byte b[], int off, int len) throws IOException {
    if (b == null) {
        throw new NullPointerException();
    } else if (off < 0 || len < 0 || len > b.length - off) {
        throw new IndexOutOfBoundsException();
    } else if (len == 0) {
        return 0;
    }

    int c = read();
    if (c == -1) {
        return -1;
    }
    b[off] = (byte)c;

    int i = 1;
    try {
        for (; i < len ; i++) {
            c = read();
            if (c == -1) {
                break;
            }
            b[off + i] = (byte)c;
        }
    } catch (IOException ee) {
    }
    return i;
}
```

首先，参数检查。其次，读入一个字符，看看是不是空，不是空就放进数组。然后，循环读入数组，一直到读够了 `len` 个，或者是读不出数据了。

* skip 

skip 会跳过 n 个字符：


```java
public long skip(long n) throws IOException {

    long remaining = n;
    int nr;

    if (n <= 0) {
        return 0;
    }

    int size = (int)Math.min(MAX_SKIP_BUFFER_SIZE, remaining);
    byte[] skipBuffer = new byte[size];
    while (remaining > 0) {
        nr = read(skipBuffer, 0, (int)Math.min(size, remaining));
        if (nr < 0) {
            break;
        }
        remaining -= nr;
    }

    return n - remaining;
}
```

开一个 byte数组，`skipBuffer` ，每次把数据读进来，一直到读不出数据，或者读够了。最后，返回 `skip` 过的数目。