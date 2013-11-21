# web.py 项目之 googlemodules

## 目录树

```
src/
├── application.py
├── forum.py
├── config_example.py
├── INSTALL
├── LICENCE
├── app
│   ├── controllers
│   ├── helpers
│   ├── models
│   └── views
├── app_forum
│   ├── controllers
│   ├── models
│   └── views
├── data
├── public
│   ├── css
│   ├── img
│   │   └── star
│   ├── js
│   └── rss
├── scripts
└── sql

18 directories
```

终于遇到个稍微大一点的项目了，要好好看看。

从目录上看，整个项目分成两个部分，app 和 app_forum,每个部分都使用了
典型的MVC结构，将app分成 controllers, models, views 三大部分。

另外，网站使用的 css, js 文件，图片，也都统一放在了public目录下。

INSTALL 文件描述了如何安装部署项目, 包括在哪里下载项目，哪里下载web.py，如何
配置 lighttpd, 如何配置项目。

config_example.py 文件给了一个配置文件模板，按自己的需要修改其中内容，最后
把文件名改为 config.py 就可以了，其中包括对数据的配置，调试，缓存的开启等等。

LICENCE 文件描述了项目使用的开源协议: GPLv3。

项目使用的脚本放在scripts目录下，创建数据库使用的文件放在了sql目录下。

## 代码统计

先看看代码统计

![googlemodules_code_stat.jpg](/StrayBirds/images/googlemodules_code_stat.jpg)

| py | js | html | css | sql | total |
|1333 | 36 | 672 | 636 | 53 | 2730 |

2730 不算多，也不算少，看看读过源代码后，还可以加些什么功能吧。
