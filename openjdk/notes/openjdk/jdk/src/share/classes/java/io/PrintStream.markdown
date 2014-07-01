# OpenJDK 源码阅读之 PrintStream

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.OutputStream
        java.io.FilterOutputStream
            java.io.PrintStream
```

* 定义 

```java
public class PrintStream
extends FilterOutputStream
implements Appendable, Closeable
```

* 要点

`PrintStream` 是 `FilterOutputStream` 的子类，这意味着它在构造器中，会保存一个底层流，然后在此基础上加功能，具体写入功能都是由底层流完成的。它不会抛出IOException异常，并且，当 `byte` 数组被写入，或者 println 被调用，或者输出 `\n` 时，flush 会被自动调用。

人民大众喜闻乐见的 `System.out` 就是 `PrintStream` 类型的。其定义为:

```java
public final static PrintStream out = null;
```

作为标准输出，它提供了很多输出功能，这些功能都是在 `PrintStream` 中完成的。

## 实现 

* 构造器 

```java
private PrintStream(boolean autoFlush, OutputStream out, Charset charset) {
    super(out);
    this.autoFlush = autoFlush;
    this.charOut = new OutputStreamWriter(this, charset);
    this.textOut = new BufferedWriter(charOut);
}
```

构造器中，可以指定是否自动刷新，底层输出流，以及字符集。通过字符集，可以指定与此字节流对应的一个字符流。另外，还提供了一个 `textOut` 用于输出时的缓冲。

* write

```java
public void write(int b) {
    try {
        synchronized (this) {
            ensureOpen();
            out.write(b);
            if ((b == '\n') && autoFlush)
                out.flush();
        }
    }
    catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    }
    catch (IOException x) {
        trouble = true;
    }
}
```

`write` 时，要调用底层流的 `write` 功能，另外，像要点中说的一样，如果输出 `\n` ，并且打开了 `autoFlush` ，此时会刷新。

另外，注意 `IOException` 不会被抛出，而是设置一个错误标志， `trouble`，另外，提供了一系列函数，用于操作这个错误标志，例如，检查，清除,设置等等 ：


```java
protected void clearError() {
    trouble = false;
}

protected void setError() {
    trouble = true;
}

public boolean checkError() {
    if (out != null)
        flush();
    if (out instanceof java.io.PrintStream) {
        PrintStream ps = (PrintStream) out;
        return ps.checkError();
    }
    return trouble;
}
```

* more write

这个类还提供了一些输出至字节数组，字符数组的方法：

```java
public void write(byte buf[], int off, int len) {
    try {
        synchronized (this) {
            ensureOpen();
            out.write(buf, off, len);
            if (autoFlush)
                out.flush();
        }
    }
    catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    }
    catch (IOException x) {
        trouble = true;
    }
}

private void write(char buf[]) {
    try {
        synchronized (this) {
            ensureOpen();
            textOut.write(buf);
            textOut.flushBuffer();
            charOut.flushBuffer();
            if (autoFlush) {
                for (int i = 0; i < buf.length; i++)
                    if (buf[i] == '\n')
                        out.flush();
            }
        }
    }
    catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    }
    catch (IOException x) {
        trouble = true;
    }
}
```

注意，输出至字节数组时，直接调用底层流进行 `write`，而输出至字符数组时，调用的是初始化时生成的字符流 `textOut` 进行 `write`。

* print

有一系列的 `print` 函数，它们会先转化成 `String` ，再调用 `PrintStream` 的 `write` 方法，进行输出：


```java
public void print(boolean b) {
    write(b ? "true" : "false");
}

public void print(char c) {
    write(String.valueOf(c));
}

public void print(int i) {
    write(String.valueOf(i));
}

...
```

`write(String)` 方法定义为：

```java
private void write(String s) {
    try {
        synchronized (this) {
            ensureOpen();
            textOut.write(s);
            textOut.flushBuffer();
            charOut.flushBuffer();
            if (autoFlush && (s.indexOf('\n') >= 0))
                out.flush();
        }
    }
    catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    }
    catch (IOException x) {
        trouble = true;
    }
}
```

调用字符流输出，并刷新，另外，如果字符串中包括 `\n` ，还会对底层流进行刷新。问题是：

> 对底层流的刷新，为什么放在对字符流的刷新之后？

* println

`println` 函数会在 `print` 的基础上，再输出一个换行符, 例如：

```java
public void println(boolean x) {
    synchronized (this) {
        print(x);
        newLine();
    }
}
```

`newLine` 函数会调用字符流输出一个换行符：

```java
private void newLine() {
    try {
        synchronized (this) {
            ensureOpen();
            textOut.newLine();
            textOut.flushBuffer();
            charOut.flushBuffer();
            if (autoFlush)
                out.flush();
        }
    }
    catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    }
    catch (IOException x) {
        trouble = true;
    }
}
```

* printf

另外，还提供了一系列 `printf` 函数，用于格式化输出：


```java
public PrintStream printf(String format, Object ... args) {
    return format(format, args);
}
```

`format`  函数会调用  `Formatter` 的相关函数进行最终的输出。

```java
public PrintStream format(String format, Object ... args) {
    try {
        synchronized (this) {
            ensureOpen();
            if ((formatter == null)
                || (formatter.locale() != Locale.getDefault()))
                formatter = new Formatter((Appendable) this);
            formatter.format(Locale.getDefault(), format, args);
        }
    } catch (InterruptedIOException x) {
        Thread.currentThread().interrupt();
    } catch (IOException x) {
        trouble = true;
    }
    return this;
}
```