# OpenJDK 源码阅读之 FileInputStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.InputStream
        java.io.FileInputStream
```

* 定义 

```java
public class FileInputStream
extends InputStream
```

* 要点 

`FileInputStream` 的字节来源于文件系统中的文件，它是用来读入字节的，如果想读入字符，可以使用 `FileReader`。

## 实现

* 初始化

```java
public FileInputStream(File file) throws FileNotFoundException {
    String name = (file != null ? file.getPath() : null);
    SecurityManager security = System.getSecurityManager();
    if (security != null) {
        security.checkRead(name);
    }
    if (name == null) {
        throw new NullPointerException();
    }
    fd = new FileDescriptor();
    fd.incrementAndGetUseCount();
    open(name);
```

使用 `File` 对象对 `FileInputStream` 进行初始化。先看文件描述符 `FileDescriptor`，`incrementAndGetUseCount` 我猜测应该是增加系统打开的文件数目，之前看 `K&R` 的 `The C Programming Language` 时，提到过文件描述符，用于描述每个打开的文件的信息，其数目是有限的。

跟踪过去。


```java
int incrementAndGetUseCount() {
    return useCount.incrementAndGet();
}
```

其中 , `userCount` 是一个原子类型的整数变量，会对其加1。

```java
private AtomicInteger useCount;
```

之后就没有什么了，还是没有明白有什么用。

继续看 `open` 吧。


```java
private native void open(String name) throws FileNotFoundException;
```

一个 `native` 的函数，和操作系统相关。到目录 `/jdk/src/share/native/java/io` 下查找 `FileInputStream.c`，可以看到：


```c
JNIEXPORT void JNICALL
Java_java_io_FileInputStream_open(JNIEnv *env, jobject this, jstring path) {
    fileOpen(env, this, path, fis_fd, O_RDONLY);
}
```

啊，又调用了 `fileOpen`。。找不到在哪儿定义的，但是最终肯定会调用操作系统打开文件的函数。

* read

```java
public native int read() throws IOException;
```

`read` 操作也是一个 `native` 函数，可是在哪里定义啊，啊啊啊啊啊～

找来找去也没找到，看看以后读虚拟机的源代码的时候能不能找到吧!