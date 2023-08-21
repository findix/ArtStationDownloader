#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""批量下载ArtStation图片

Copyright 2018 Sean Feng(sean@fantablade.com)
"""

__version__ = "0.3.3"
# $Source$

import argparse

from app import App
from core import DownloadSorting
from console import Console


def main():
    parser = argparse.ArgumentParser(
        prog="ArtStationDownloader",
        description="ArtStation Downloader is a lightweight tool to help you download images and videos from the ArtStation",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "-u",
        "--username",
        help="choose who's project you want to download, one or more",
        nargs="*",
    )
    parser.add_argument("-d", "--directory", help="output directory")
    parser.add_argument(
        "-t",
        "--type",
        choices=["all", "image", "video"],
        default="all",
        help="what do you what to download, default is all",
    )
    parser.add_argument(
        "-s",
        "--sorting",
        choices=[sorting.name for sorting in DownloadSorting],
        default=DownloadSorting.TITLE_BASED.name,
        help="download sorting",
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", help="increase output verbosity"
    )
    args = parser.parse_args()

    if args.username:
        if args.directory:
            console = Console()
            console.download_by_usernames(args.username, args.directory, args.type, DownloadSorting[args.sorting])
        else:
            print("no output directory, please use -d or --directory option to set")
    else:
        app = App(version=__version__)
        app.run()  # 进入主循环，程序运行


if __name__ == "__main__":
    main()
