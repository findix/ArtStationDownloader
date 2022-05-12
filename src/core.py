# -*- coding: utf-8 -*-

"""内核方法
Copyright 2018-2019 Sean Feng(sean@FantaBlade.com)
"""

import os
import re
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import pafy
import requests

import config


class Core:
    def log(self, message):
        print(message)

    def __init__(self, log_print=None):
        if log_print:
            global print
            print = log_print
        max_workers = cpu_count() * 4
        self.executor = futures.ThreadPoolExecutor(max_workers)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.root_path = None
        self.futures = []
        self.session = requests.session()
        # 设置 User Agent
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
            }
        )
        # 设置代理
        http = config.read_config("config.ini", "Proxy", "http")
        https = config.read_config("config.ini", "Proxy", "https")
        if http or https:
            proxys = {}
            if http:
                proxys["http"] = http
            if https:
                proxys["https"] = https
            self.session.proxies.update(proxys)

    def download_file(self, url, file_path, file_name):
        url = url.replace("/large/", "/4k/")
        file_full_path = os.path.join(file_path, file_name)
        if os.path.exists(file_full_path):
            self.log("[Exist][image][{}]".format(file_full_path))
        else:
            r = self.session.get(url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log("[Finish][image][{}]".format(file_full_path))

    def download_video(self, id, file_path):
        file_full_path = os.path.join(file_path, "{}.{}".format(id, "mp4"))
        if os.path.exists(file_full_path):
            self.log("[Exist][video][{}]".format(file_full_path))
        else:
            video = pafy.new(id)
            best = video.getbest(preftype="mp4")
            r = self.session.get(best.url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log("[Finish][video][{}]".format(file_full_path))

    def download_project(self, hash_id):
        url = "https://www.artstation.com/projects/{}.json".format(hash_id)
        r = self.session.get(url)
        j = r.json()
        assets = j["assets"]
        title = j["slug"].strip()
        # self.log('=========={}=========='.format(title))
        username = j["user"]["username"]
        for asset in assets:
            assert self.root_path
            user_path = os.path.join(self.root_path, username)
            os.makedirs(user_path, exist_ok=True)
            file_path = os.path.join(user_path, title)
            if not self.no_image and asset["has_image"]:  # 包含图片
                url = asset["image_url"]
                file_name = urlparse(url).path.split("/")[-1]
                try:
                    self.futures.append(
                        self.executor.submit(
                            self.download_file, url, file_path, file_name
                        )
                    )
                except Exception as e:
                    print(e)
            if not self.no_video and asset["has_embedded_player"]:  # 包含视频
                player_embedded = asset["player_embedded"]
                id = re.search(
                    r"(?<=https://www\.youtube\.com/embed/)[\w_]+", player_embedded
                ).group()
                try:
                    self.futures.append(
                        self.executor_video.submit(self.download_video, id, file_path)
                    )
                except Exception as e:
                    print(e)

    def get_projects(self, username):
        data = []
        if username != "":
            page = 0
            while True:
                page += 1
                url = "https://{}.artstation.com/rss?page={}".format(username, page)
                r = self.session.get(url)
                if not r.ok:
                    err = "[Error] [{} {}] ".format(r.status_code, r.reason)
                    if r.status_code == 403:
                        self.log(err + "You are blocked by artstation")
                    elif r.status_code == 404:
                        self.log(err + "Username not found")
                    else:
                        self.log(err + "Unknown error")
                    break
                channel = BeautifulSoup(r.text, "lxml-xml").rss.channel
                links = channel.select("item > link")
                if len(links) == 0:
                    break
                if page == 1:
                    self.log("\n==========[{}] BEGIN==========".format(username))
                data += links
                self.log("\n==========Get page {}==========".format(page))
        return data

    def download_by_username(self, username):
        data = self.get_projects(username)
        if len(data) != 0:
            future_list = []
            for project in data:
                future = self.executor.submit(
                    self.download_project, project.string.split("/")[-1]
                )
                future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(self, usernames, type):
        self.no_image = type == "video"
        self.no_video = type == "image"
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split("/")[-1]
            if username not in username_set:
                username_set.add(username)
                self.download_by_username(username)
        futures.wait(self.futures)
        self.log("\n========ALL DONE========")
