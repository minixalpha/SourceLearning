# OpenJDK 源码阅读之 FileOutputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.FileOutputStream
```

* 类定义 

```java
public class FileOutputStream
extends OutputStream
```

* 要点 

`FileOutputStream` 会将内容输出到 `File` 或者 `FileDescriptor`，此类是按照字节输出，如果想按照字符输出，可以使用 `FileReader` 类。

## 实现


* 构造器 

构造器有好几个，关键的一个下面这个，其它的需要调用它来实现最终的功能。


```java
public FileOutputStream(File file, boolean append)
    throws FileNotFoundException
{
    String name = (file != null ? file.getPath() : null);
    SecurityManager security = System.getSecurityManager();
    if (security != null) {
        security.checkWrite(name);
    }
    if (name == null) {
        throw new NullPointerException();
    }
    this.fd = new FileDescriptor();
    this.append = append;

    fd.incrementAndGetUseCount();
    open(name, append);
}
```

这里先使用了 `SecurityManager` 来检查这个文件是否可写，然后增加 `FileDescriptor` 的数目，最后调用 `open` 函数打开这个文件。

`SecurityManager` 用来管理 Java 的安全策略，有一系列 `check` 函数，检查是否违反安全策略，如果违反，JVM 会抛出异常。`FileDescriptior` 用来处理和操作系统相关的数据结构，例如文件，socket等，你不需要自己调用，它只会出现在 `FileInputStream` 和  `FileOutputStream` 中。

至于  `open` 函数，是一个 `native` 函数，

```java
private native void open(String name, boolean append)
    throws FileNotFoundException;
```

也就是说是与操作系统相关的一个函数，由各个不同的操作系统提供的文件打开函数实现。

* write

```java
private native void write(int b, boolean append) throws IOException;
```

同理，也是一个 `native` 函数，和操作系统相关。

* close

```java
public void close() throws IOException {
    synchronized (closeLock) {
        if (closed) {
            return;
        }
        closed = true;
    }

    if (channel != null) {
        /*
         * Decrement FD use count associated with the channel
         * The use count is incremented whenever a new channel
         * is obtained from this stream.
         */
        fd.decrementAndGetUseCount();
        channel.close();
    }

    /*
     * Decrement FD use count associated with this stream
     */
    int useCount = fd.decrementAndGetUseCount();

    /*
     * If FileDescriptor is still in use by another stream, the finalizer
     * will not close it.
     */
    if ((useCount <= 0) || !isRunningFinalize()) {
        close0();
    }
}
```

这里的 `close` ，需要先作一些处理，例如，设置 `closed` 标志，将初始化时增加的 `FileDescriptor` 恢复，最后，再调用与系统相关的，`native` 函数 `close0`:

```java
private native void close0() throws IOException;
```