# OpenJDK 源码阅读之 InputStreamReader

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.InputStreamReader
```

* 定义 

```java
public class InputStreamReader
extends Reader
```

* 要点 

`InputStreamReader` 是字节流与字符流之间的桥梁，它读取字节，并将其解码后转化成字符。

## 实现

* 初始化 

```java
 private final StreamDecoder sd;
public InputStreamReader(InputStream in) {
    super(in);
    try {
        sd = StreamDecoder.forInputStreamReader(in, this, (String)null); // ## check lock object
    } catch (UnsupportedEncodingException e) {
        // The default encoding should always be available
        throw new Error(e);
    }
}
```

既然是将字节解码后转化成字符，你总得告诉我从哪儿读取字节流吧，看！就是从这里，这里生成了一个 `StreamDecoder` ， 因为转化的过程，    其实就是解码的过程。

我们进一步看看这个 `StreamDecoder` 里都有什么， 因为既然是解码， 总得有一个 `编码格式` 才行啊，比如 `utf-8` 啊什么的。


```java
 public static StreamDecoder forInputStreamReader(
 InputStream in, Object lock, String charsetName)
        throws UnsupportedEncodingException {
        
    String csn = charsetName;
    if (csn == null)
        csn = Charset.defaultCharset().name();
    try {
        if (Charset.isSupported(csn))
            return new StreamDecoder(in, lock, Charset.forName(csn));
    } catch (IllegalCharsetNameException x) { }
    throw new UnsupportedEncodingException (csn);
}
```

由于我们的 `charsetName` 传入的是空，所以需要使用 `Charset.defaultChaset` 来获取默认的编码格式名。

我们进一步跟踪下去，


```java
public static Charset defaultCharset() {
    if (defaultCharset == null) {
        synchronized (Charset.class) {
            String csn = AccessController.doPrivileged(
                new GetPropertyAction("file.encoding"));
            Charset cs = lookup(csn);
            if (cs != null)
                defaultCharset = cs;
            else
                defaultCharset = forName("UTF-8");
        }
    }
    return defaultCharset;
}
```

这里，先调用了 `AccessController` 的方法获取一个 `csn` ，再用 `lookup` 去查询，然后看有没有查询到，如果没查询到的话，就将默认编码赋值为 `UTF-8`。`AccessController` 是与访问控制相关的类，`doPrivileged` 是一个 `native` 方法，我们只要知道这是在查询编码方式就好了。

现在看看 `read` 方法。

* read

```java
public int read() throws IOException {
    return sd.read();
}
```

`read` 很简单，使用刚才的解码器 `read` 一下。我们跟踪进去，看里面发生了什么。


```java
public int read() throws IOException {
    return read0();
}

private int read0() throws IOException {
    synchronized (lock) {

        // Return the leftover char, if there is one
        if (haveLeftoverChar) {
            haveLeftoverChar = false;
            return leftoverChar;
        }

        // Convert more bytes
        char cb[] = new char[2];
        int n = read(cb, 0, 2);
        switch (n) {
        case -1:
            return -1;
        case 2:
            leftoverChar = cb[1];
            haveLeftoverChar = true;
            // FALL THROUGH
        case 1:
            return cb[0];
        default:
            assert false : n;
            return -1;
        }
    }
}
```

这个 `read0` 还挺有意思的，先不管 `haveLeftoverChar` ，先看 `read(cb, 0, 2)`，它读取了两个字符。如果返回 `-1` ，说明读不出来了。如果返回 `1`，那么把这个返回的值 `return` ，如果返回的是 `2`，说明读了两个字符，这时候只能返回一个，就是 `cb[0]` ，注意 `case 2` 后面没有 `break`。多读的那个字符 `cb[1]` 放在 `haveLeftoverChar` 中，以备下次使用，所以，这个 `haveLeftoverChar` 有点缓冲区的意思了。

剩下的没什么好说的了，其实我是想看看解码的过程的，但是怎么找不到呢？