# -*- coding: utf-8 -*-

"""内核方法
Copyright 2018-2019 Sean Feng(sean@FantaBlade.com)
"""

import os
from concurrent import futures
from enum import Enum
from multiprocessing import cpu_count

from bs4 import BeautifulSoup, element
from pytube import YouTube

from http_client import HttpClient


class DownloadSorting(Enum):
    TITLE_BASED = "Title-based"
    USERNAME_BASED = "Username-based"
    ALL_IN_ONE = "All-in-one"

    def __str__(self) -> str:
        return self.value


class Core:
    def log(self, message):
        if self._log_print:
            self._log_print(message)
        else:
            print(message)

    def __init__(self, log_print=None):
        self._log_print = log_print
        max_workers = cpu_count() * 4
        self.executor = futures.ThreadPoolExecutor(max_workers)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.invoke = self._get_invoke()
        self.invoke_video = self._get_invoke("video")
        self.root_path: str = None
        self.download_sorting: DownloadSorting = None
        self.futures = []
        self.http_client = HttpClient(log_print=log_print)

    def download_file(self, url, file_path, file_name):
        url = url.replace("/large/", "/4k/")
        file_full_path = os.path.join(file_path, file_name)
        if os.path.exists(file_full_path):
            self.log("[Exist][image][{}]".format(file_full_path))
        else:
            resp = self.http_client.http_get(url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(resp.content)
            self.log("[Finish][image][{}]".format(file_full_path))

    def download_video(self, youtube_id, file_path):
        file_full_path = os.path.join(file_path, "{}.{}".format(youtube_id, "mp4"))
        if os.path.exists(file_full_path):
            self.log("[Exist][video][{}]".format(file_full_path))
        else:
            try:
                yt = YouTube(f'https://www.youtube.com/watch?v={youtube_id}')
                stream = yt.streams.filter(file_extension='mp4').first()
                stream.download(output_path=file_path)
                self.log("[Finish][video][{}]".format(file_full_path))
            except Exception as e:
                self.log("[Error][video][{}]".format(e))

    def download_project(self, hash_id):
        url = "https://www.artstation.com/projects/{}.json".format(hash_id)
        resp = self.http_client.http_client_get_json(url)
        j = resp
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
                file_name = HttpClient.urlparse(url).path.split("/")[-1]
                try:
                    self.futures.append(
                        self.invoke(self.download_file, url, file_path, file_name)
                    )
                except Exception as e:
                    self.log(e)
            if not self.no_video and asset["has_embedded_player"]:  # 包含视频
                player_embedded = BeautifulSoup(asset["player_embedded"], "html.parser")
                src = player_embedded.find("iframe").get("src")
                if "youtube" in src:
                    youtube_id = self.http_client.urlparse(src).path[-11:]
                    try:
                        self.futures.append(
                            self.invoke_video(self.download_video, youtube_id, file_path)
                        )
                    except Exception as e:
                        self.log(e)

    def get_projects(self, username) -> element.ResultSet[element.Tag]:
        data = []
        if username != "":
            page = 0
            while True:
                page += 1
                url = "https://{}.artstation.com/rss?page={}".format(username, page)
                resp = self.http_client.http_client_get(url)
                if resp.status != 200:
                    err = "[Error] [{} {}] ".format(resp.status, resp.reason)
                    if resp.status == 403:
                        self.log(err + "You are blocked by artstation")
                    elif resp.status == 404:
                        self.log(err + "Username not found")
                    else:
                        self.log(err + "Unknown error")
                    break
                channel = BeautifulSoup(
                    resp.read().decode("utf-8"), "lxml-xml"
                ).rss.channel
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
                if project.string.startswith("https://www.artstation.com/artwork/"):
                    future = self.invoke(
                        self.download_project, project.string.split("/")[-1]
                    )
                    future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(
        self, usernames, download_type, download_sorting: DownloadSorting
    ):
        self.http_client.proxy_setup()
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
