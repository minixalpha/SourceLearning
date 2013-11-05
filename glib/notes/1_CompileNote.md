# GLib 源码阅读手记

看着 `glib-2.37.93` 下那么多文件和目录，头都大了，不知道从哪儿读起，
那就翻翻手册好了。跟着手册的路线先读一下。

[GLib Reference Manual](https://developer.gnome.org/glib/2.37/) 第一部分讲的是
[GLib Overview](https://developer.gnome.org/glib/2.37/glib.html)，所以我们从这里开始。

## GLib Overview

这一部分主要讲的是如何编译 GLib, 如何使用 GLib 写程序，编译，并运行。
因为之前没有用过 GLib, 要直接阅读源代码可能会有困难，所以这一部分要先了解一下。

### Compiling the GLib package

这一节讲如何编译 GLib 包，编译的方法和一般 Linux C 项目一样

    ./configure
    make
    make install

老实说，这几个命令不知道打多少次了，但是不知道他们之前的关系，工作原理。近来深深
感觉到这样学习是不行的。再说，我们要阅读源代码了，所有和源代码相关的都要了解。

Google 了一下，这几个命令和 GNU build system相关，于是，先把 wikipedia 上的词条
[GNU build system](http://en.wikipedia.org/wiki/GNU_build_system)读一下。

GNU build system 也叫做 Autotools, 主要解决可移植性问题，每个系统的C编译器可能不同，
库函数也可能不同，为了保证软件正常编译，屏蔽编译环境的不同，Autotools 应运而生。
Autotools 提供了一系列的工具，使得我们在不同的系统上，只需要运行那三条命令就可以
编译安装软件。

一图胜千言:

![Autotools](http://upload.wikimedia.org/wikipedia/commons/8/84/Autoconf-automake-process.svg)

从这张图可以看出 Autotools 的工作流程。我们也明白了 `glib-2.37.93/` 目录下那些 `.in`, `.am`, `.m4`
文件的由来及作用。同时也明白了与编译安装相关的 `configure` 脚本, `Makefile` 文件的来源。
如果想亲自使用 Autotools 作一个实验，可以参考这篇 
[GNU Autotools的使用方法](http://blog.csdn.net/scucj/article/details/6079052)
