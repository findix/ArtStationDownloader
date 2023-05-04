# -*- coding: utf-8 -*-

"""内核方法
Copyright 2018-2019 Sean Feng(sean@FantaBlade.com)
"""

from enum import Enum
import os
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse
import http.client
from bs4 import BeautifulSoup
import pafy
import requests

from config import Config


class DownloadSorting(Enum):
    TITLE_BASED = "Title-based"
    USERNAME_BASED = "Username-based"
    ALL_IN_ONE = "All-in-one"

    def __str__(self) -> str:
        return self.value


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
        self.invoke = self._get_invoke()
        self.invoke_video = self._get_invoke("video")
        self.root_path: str = None
        self.download_sorting: DownloadSorting = None
        self.futures = []
        self._session = requests.session()
        self.proxy_setup()
    
    def http_client_get(self, url):
        try:
            headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            'Accept-Language': "en-US,en;q=0.5",
            'Accept-Encoding': "gzip, deflate, br",
            }
            parsed_url = urlparse(url)
            conn = http.client.HTTPSConnection(parsed_url.netloc)
            conn.request("GET", parsed_url.path+"?"+parsed_url.query, headers=headers)

            r = conn.getresponse()

        except:
            print(f'Error in http_client_get')
            
        return r

    def http_get(self, url):
        try:
            r = self._session.get(url, timeout=10)
        except requests.exceptions.InvalidURL:
            print(f'"{url}" is not valid url')
            return
        return r

    def proxy_setup(self):
        session = self._session
        # 设置 User Agent
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
            }
        )
        # 设置代理
        config = Config("config.ini")
        http = config.get("Proxy", "http")
        https = config.get("Proxy", "https")
        if http or https:
            proxys = {}
            if http:
                proxys["http"] = http
            if https:
                proxys["https"] = https
            session.proxies.update(proxys)

    def download_file(self, url, file_path, file_name):
        url = url.replace("/large/", "/4k/")
        file_full_path = os.path.join(file_path, file_name)
        if os.path.exists(file_full_path):
            self.log("[Exist][image][{}]".format(file_full_path))
        else:
            r = self.http_get(url)
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
            r = self.http_get(best.url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log("[Finish][video][{}]".format(file_full_path))

    def download_project(self, hash_id):
        url = "https://www.artstation.com/projects/{}.json".format(hash_id)
        r = self.http_get(url)
        j = r.json()
        assets = j["assets"]
        title = j["slug"].strip()
        # self.log('=========={}=========='.format(title))
        username = j["user"]["username"]
        for asset in assets:
            assert self.root_path
            if self.download_sorting != DownloadSorting.ALL_IN_ONE:
                user_path = os.path.join(self.root_path, username)
            else:
                user_path = self.root_path
            os.makedirs(user_path, exist_ok=True)
            if self.download_sorting == DownloadSorting.TITLE_BASED:
                file_path = os.path.join(user_path, title)
            else:
                file_path = user_path
            if not self.no_image and asset["has_image"]:  # 包含图片
                url = asset["image_url"]
                file_name = urlparse(url).path.split("/")[-1]
                try:
                    self.futures.append(
                        self.invoke(self.download_file, url, file_path, file_name)
                    )
                except Exception as e:
                    print(e)
            if not self.no_video and asset["has_embedded_player"]:  # 包含视频
                player_embedded = BeautifulSoup(asset["player_embedded"], "html.parser")
                src = player_embedded.find("iframe").get("src")
                if "youtube" in src:
                    try:
                        self.futures.append(
                            self.invoke_video(self.download_video, src, file_path)
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
                r = self.http_client_get(url)
                if r.status != 200:
                    err = "[Error] [{} {}] ".format(r.status, r.reason)
                    if r.status == 403:
                        self.log(err + "You are blocked by artstation")
                    elif r.status == 404:
                        self.log(err + "Username not found")
                    else:
                        self.log(err + "Unknown error")
                    break
                channel = BeautifulSoup(r.read().decode("utf-8"), "lxml-xml").rss.channel
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
                future = self.invoke(
                    self.download_project, project.string.split("/")[-1]
                )
                future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(
        self, usernames, download_type, download_sorting: DownloadSorting
    ):
        self.proxy_setup()
        self.no_image = download_type == "video"
        self.no_video = download_type == "image"
        self.download_sorting = download_sorting
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split("/")[-1]
            if username not in username_set:
                username_set.add(username)
                self.download_by_username(username)
        futures.wait(self.futures)
        self.log("\n========ALL DONE========")

    def _get_invoke(self, executor=None):
        def invoke(func, *args, **kwargs):
            def done_callback(worker):
                worker_exception = worker.exception()
                if worker_exception:
                    self.log(str(worker_exception))
                    raise (worker_exception)

            if executor == "video":
                futurn = self.executor_video.submit(func, *args, **kwargs)
                futurn.add_done_callback(done_callback)
            else:
                futurn = self.executor.submit(func, *args, **kwargs)
                futurn.add_done_callback(done_callback)
            return futurn

        return invoke
