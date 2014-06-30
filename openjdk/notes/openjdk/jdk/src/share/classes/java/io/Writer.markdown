# OpenJDK 源码阅读之 Writer

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Writer
```

* 定义 

```java
public abstract class Writer
extends Object
implements Appendable, Closeable, Flushable
```

* 要点 

写入字符流的抽象类，其子类必需实现 `write(char[], int, int), flush(), and close()`，另外，也会添加或者覆盖其它方法，以提升效率或增加功能。


## 实现

* write

```java
public void write(int c) throws IOException {
    synchronized (lock) {
        if (writeBuffer == null){
            writeBuffer = new char[writeBufferSize];
        }
        writeBuffer[0] = (char) c;
        write(writeBuffer, 0, 1);
    }
}
```

注意，会用一个 `writeBuffer` 保存要写入的数据，然后调用 `write(char[], int, int)` 写入数据，这个函数是个抽象函数，具体实现由子类完成。

另外两个子类需要实现的函数是：

```java
abstract public void flush() throws IOException;
abstract public void close() throws IOException;
```




