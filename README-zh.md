# ArtStation Downloader

ArtStation Downloader 是一个帮助你批量从[ArtStation](https://www.artstation.com/)网站下载图片和视频的小工具

## 用法

### 从这里开始

[在此下载](https://github.com/findix/ArtStationDownloader/releases)

### 如何下载

输入你希望下载的作者的主页地址，或者其用户名

如

`https://www.artstation.com/xrnothing` 或者 `xrnothing`

然后点击 Download 按钮

你可以一次下载多位作者的作品

只需要在输入他们的 URL 或用户名时，在中间加入英文的","即可

或者，你也可以新建一个文本文件（.txt），每一行输入一位作者的信息。
（允许使用 Python 风格的注释，即 # 后的内容会被忽略，空白符与空行同样也会被忽略）

然后点击 Download txt 按钮选择文件即可。

Type 下拉选单可以设置下载资源的类型, 你可以选择“只下载图片”、“只下载视频”以及“全部下载”

Path 输入框内是下载文件夹位置，你可以按需求设置。

## 缺陷与反馈

如果在使用过程中发现任何错误、问题或是希望讨论，请使用 [Github Issues](https://github.com/findix/ArtStationDownloader/issues).

非常欢迎提交 Pull requests！

## 打包

需要 Pyinstaller.

运行 `build.bat`

## For macOS/Linux/Shell

首先执行 `pip install -r requirements.txt` 安装依赖

在 shell 中执行 `python ./src/ArtStationDownloader.py` 开启图形界面

或者

直接运行类似下面的命令:

`python ./src/ArtStationDownloader.py -u username_of_artist other_username or_more -d where/you/what`

您可以尝试输入 `python ./src/ArtStationDownloader.py --help` 查看更多用法

## FAQ

> **为什么我在点击下载后报错 `[Error] [403 Forbidden] You are blocked by artstation`？**

ArtStation 有一个 [验证码](https://zh.wikipedia.org/zh-hans/%E9%AA%8C%E8%AF%81%E7%A0%81) 系统 (由 Cloudflare 提供)。如果你无法证明你不是爬虫，就会被禁止访问，这个问题目前我还没有找到解决办法，如果您有方式解决，请告诉我。


## LICENSE

MIT License

Copyright (c) 2018-2019 Sean Feng