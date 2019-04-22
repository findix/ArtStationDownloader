# ArtStation Downloader

[中文说明](./README-zh.md)

ArtStation Downloader is a lightweight tool to help you download images and videos from the [ArtStation](https://www.artstation.com/)

## Usage

### Getting started

[Download here](https://github.com/findix/ArtStationDownloader/releases)

### Download from ArtStation

Input the URL of the artist or just the username

just like

`https://www.artstation.com/xrnothing` or `xrnothing`

and click the Download button.

You can download more then one artists' whole works at one time.

Just input all the URL or usernames split with ','.

or you can create a txt file with These, one artist one line.
(you can use python style comment, any text after # will be ignored, space charactor and empty line are also ignored)

and click the Download txt button to select file.

The combobox named Type means you can choose what resources are required. image only, video only or both

The Path means the path of the download folder，just set it.

## Bugs and Feedback

For bugs, questions and discussions please use the [Github Issues](https://github.com/findix/ArtStationDownloader/issues).

Pull requests are all welcome!

## Package

Require Pyinstaller.

Just execute `build.bat`

## For macOS/Linux/Shell

install dependencies py run `pip install -r requirements.txt` first

just run `python ./src/ArtStationDownloader.py` in shell to run in GUI mode

or

run like this:

`python ./src/ArtStationDownloader.py -u username_of_artist other_username or_more -d where/you/what` in shell

try `python ./src/ArtStationDownloader.py --help` to get more usage

## FAQ

> **Why I get a message says `[Error] [403 Forbidden] You are blocked by artstation`?**

The ArtStation has a [CAPTCHA](https://en.wikipedia.org/wiki/CAPTCHA) system (by Cloudflare) which need you proof you are human otherwise forbid you. I haven't found a way solve this for now. If you have idea, please tell me.

## LICENSE

MIT License

Copyright (c) 2018-2019 Sean Feng