# OpenJDK 源码阅读之 BufferedReader

标签（空格分隔）： 源代码阅读 Java 封神之路

---

## 概要

* 类继承关系 

```java
java.lang.Object
    java.io.Reader
        java.io.BufferedReader
```

* 定义 

```java
public class BufferedReader
extends Reader
```

* 要点

`BufferedReader` 从字符输入流中读取文本，并将其缓存以提升读取速度。缓存的大小可以指定，也可以使用默认值。它可以为其它字符输入流提供缓存。例如：

```java
BufferedReader in
   = new BufferedReader(new FileReader("foo.in"));
```

## 实现

* 初始化

```java
public BufferedReader(Reader in, int sz) {
    super(in);
    if (sz <= 0)
        throw new IllegalArgumentException("Buffer size <= 0");
    this.in = in;
    cb = new char[sz];
    nextChar = nChars = 0;
}
```

`in` 是提供字符的输入流， `sz` 是缓存大小。可以看出，缓存是一个 `char` 类型的数组。

* read

```java
public int read() throws IOException {
    synchronized (lock) {
        ensureOpen();
        for (;;) {
            if (nextChar >= nChars) {
                fill();
                if (nextChar >= nChars)
                    return -1;
            }
            if (skipLF) {
                skipLF = false;
                if (cb[nextChar] == '\n') {
                    nextChar++;
                    continue;
                }
            }
            return cb[nextChar++];
        }
    }
}
```

`read` 的过程和之前讲 `BufferedInputStream` 时相似，如果缓冲区没有数据，就 `fill` 一下进行填充；如果缓冲区有数据，就从中读取。另外，还有一个 `bool` 变量 `skipLF` 决定了是否要跳过换行符。

* readline

```java
String readLine(boolean ignoreLF) throws IOException {
    StringBuffer s = null;
    int startChar;

    synchronized (lock) {
        ensureOpen();
        boolean omitLF = ignoreLF || skipLF;

    bufferLoop:
        for (;;) {

            if (nextChar >= nChars)
                fill();
            if (nextChar >= nChars) { /* EOF */
                if (s != null && s.length() > 0)
                    return s.toString();
                else
                    return null;
            }
            boolean eol = false;
            char c = 0;
            int i;

            /* Skip a leftover '\n', if necessary */
            if (omitLF && (cb[nextChar] == '\n'))
                nextChar++;
            skipLF = false;
            omitLF = false;

        charLoop:
            for (i = nextChar; i < nChars; i++) {
                c = cb[i];
                if ((c == '\n') || (c == '\r')) {
                    eol = true;
                    break charLoop;
                }
            }

            startChar = nextChar;
            nextChar = i;

            if (eol) {
                String str;
                if (s == null) {
                    str = new String(cb, startChar, i - startChar);
                } else {
                    s.append(cb, startChar, i - startChar);
                    str = s.toString();
                }
                nextChar++;
                if (c == '\r') {
                    skipLF = true;
                }
                return str;
            }

            if (s == null)
                s = new StringBuffer(defaultExpectedLineLength);
            s.append(cb, startChar, i - startChar);
        }
    }
}
```

`BufferedReader` 添加了 `readLine` 函数， 所以我们要以行为单位使用一个输入流时，就可以使用 `BufferedReader`。“行”的意思是以 `\r`, `\n`, 或者 `\r\n` 结尾的内容。

代码的重点在名为 `bufferLoop` 的循环里。如果缓冲区的东西读完了，就要再次填充。如果什么都填充不了了，说明数据已经读完了，可以返回内容了。`s` 保存着当前行的内容，它是 `StringBuilder` 类型。由于 `String` 类型不可变，所以每次对其进行改变，其实都是新生成一个 `String` 对象，为了避免这一点，使用 `StringBuilder` 对字符串进行累加。

`omitLF` 决定是否跳过换行符，这里会感觉很奇怪，我们是在找一行的内容，为什么要跳过换行符号？不是应该遇到换行符号就说明一行结束了，然后返回吗？根据注释，这是在去除多余的 `\n`，因为换行符也可能是 `\r\n`，遇到 `\r` 时，我们就认为一行结束了，所以下次要跳过 `\r\n` 中的 `\n`。

看一下 `charLoop`，就是在找一行的开始的结束，在对结束进行探索时，只看当前字符是不是 `\r` 或者  `\n` ，而不用看 `\r\n`，原因就在于 `\n` 会在下次读取时被忽略。

`eol` 代表 `end of line`，遇到 `\r` 或者 `\n` 就会设置为 `true`，然后从缓冲区是提取当前行的内容。随后，如果最后一个字符为 `\r` ，还需要将 `skipLF` 设置为 `true` , 以便下次 `readline` 时，`omitLF` 会被设置，进而 `\r\n` 中的 `\n` 被忽略。

