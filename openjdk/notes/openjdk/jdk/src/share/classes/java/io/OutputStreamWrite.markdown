# OpenJDK 源码阅读之 OutputStreamWrite

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
        java.io.OutputStreamWriter
```

* 定义 

```java
public class OutputStreamWriter
extends Writer
```

* 要点

这个类根据 charset 将字节流转化成字符流。


## 实现

* 编码器 

```java
private final StreamEncoder se;
```

这是此类的核心，所有操作，都会用这个编码器完成。

* 构造器 

```java
public OutputStreamWriter(OutputStream out, String charsetName)
    throws UnsupportedEncodingException
{
    super(out);
    if (charsetName == null)
        throw new NullPointerException("charsetName");
    se = StreamEncoder.forOutputStreamWriter(out, this, charsetName);
}
```

构造函数可以指定 `charset` 的名字，同一个字节流，如果编码方式不同，转化出的字符就不同，所以，需要指定 `charset`，然后，通过 `StreamEncoder.forOutputStreamWriter` 得到编码器。如果没有指定：

```java
public OutputStreamWriter(OutputStream out) {
    super(out);
    try {
        se = StreamEncoder.forOutputStreamWriter(out, this, (String)null);
    } catch (UnsupportedEncodingException e) {
        throw new Error(e);
    }
}
```

在 `charsetName` 的参数位置上，会传入空，`forOutputStreamWriter` 会寻找系统的相应设置，如果找不到，会被设置为 `UTF-8`。

* write

```java
public void write(int c) throws IOException {
    se.write(c);
}
```

调用的是编码器的 `write`，它会将 `c` 按照 charset 编码，然后写入。`write` 背后最终的编码函数是一个 `native` 函数。

其它函数，如 `flush, close` 都是调用  `se` 的相应函数实现的。
