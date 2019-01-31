# ArtStation Downloader

ArtStation Downloader is a lightweight tool to help you download images and videos from the [ArtStation](https://www.artstation.com/)

ArtStation Downloader 是一个帮助你批量从[ArtStation](https://www.artstation.com/)网站下载图片和视频的小工具

## Usage

### Getting started

[Download here](https://github.com/findix/ArtStationDownloader/releases)
[在此下载](https://github.com/findix/ArtStationDownloader/releases)

### Download from ArtStation

Input the URL of the artist or just the username

just like

https://www.artstation.com/xrnothing or xrnothing

and click the Download button.

You can download more then one artists' whole works at one time.

Just input all the URL or usernames split with ','.

or you can create a txt file with These, one artist one line.
(you can use python style comment, any text after # will be ignored, space charactor and empty line are also ignored)

and click the Download txt button to select file.

The combobox named Type means you can choose what resources are required. image only, video only or both

The Path means the path of the download folder，just set it.

输入你希望下载的作者的主页地址，或者其用户名

如

https://www.artstation.com/xrnothing 或者 xrnothing

然后点击 Download 按钮

你可以一次下载多位作者的作品

只需要在输入他们的 URL 或用户名时，在中间加入英文的","即可

或者，你也可以新建一个文本文件（.txt），每一行输入一位作者的信息。
（允许使用 Python 风格的注释，即 # 后的内容会被忽略，空白符与空行同样也会被忽略）

然后点击 Download txt 按钮选择文件即可。

Type 下拉选单可以设置下载资源的类型, 你可以选择“只下载图片”、“只下载视频”以及“全部下载”

Path 输入框内是下载文件夹位置，你可以按需求设置。

## Bugs and Feedback

For bugs, questions and discussions please use the [Github Issues](https://github.com/findix/ArtStationDownloader/issues).

Pull requests are all welcome!

如果在使用过程中发现任何错误、问题或是希望讨论，请使用 [Github Issues](https://github.com/findix/ArtStationDownloader/issues).

非常欢迎提交 Pull requests！

## Build

Require Pyinstaller.

Just execute build.bat

## For macOS/Linux/Shell

install dependencies py run `pip install -r requirements.txt` first

just run `python ./src/ArtStationDownloader.py` in shell to run in GUI mode

or

run like this:

`python ./src/ArtStationDownloader.py -u username_of_artist other_username or_more -d where/you/what` in shell

try `python ./src/ArtStationDownloader.py --help` to get more usage

## LICENSE

MIT License

Copyright (c) 2018-2019 Sean Feng