#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""批量下载ArtStation图片

Copyright 2018-2019 Sean Feng(sean@FantaBlade.com)

CHANGELOG

20180611 0.1.0-alpha1
允许在txt中使用Python风格的注释，即以#开头的内容会被忽略
对txt中的空白符进行处理
保存路径不再强制包含 ArtStation
默认保存路径现在为用户根路径

20190131 0.1.1-alpha
重构代码结构
加入命令行模式
GUI和命令行均加入允许选择下载文件类型（所有、图片、视频）功能
"""
__version__ = "0.1.1-alpha"
# $Source$

import argparse

from app import App
from console import Console


def main():
    parser = argparse.ArgumentParser(
        prog='ArtStationDownloader',
        description='ArtStation Downloader is a lightweight tool to help you download images and videos from the ArtStation')
    parser.add_argument('--version', action='version',
                        version='%(prog)s '+__version__)
    parser.add_argument('-u', '--username',
                        help='choose who\'s project you want to download, one or more', nargs='*')
    parser.add_argument('-d', '--directory', help='output directory')
    parser.add_argument(
        '-t', '--type', choices=['all', 'image', 'video'], default="all", help='what do you what to download, default is all')
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity")
    args = parser.parse_args()

    if args.username:
        if args.directory:
            console = Console()
            console.download_by_usernames(args.username, args.directory, args.type)
        else:
            print("no output directory, please use -d or --directory option to set")
    else:
        app = App(version=__version__)
        app.mainloop()  # 进入主循环，程序运行


if __name__ == '__main__':
    main()
