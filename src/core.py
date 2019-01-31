# -*- coding: utf-8 -*-

"""内核方法
Copyright 2018-2019 Sean Feng(sean@FantaBlade.com)
"""

import os
import re
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse

import pafy
import requests


class Core:

    def log(self, message):
        print(message)

    def __init__(self, log_print=None):
        if log_print:
            global print
            print = log_print
        max_workers = cpu_count()*4
        self.executor = futures.ThreadPoolExecutor(max_workers)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.root_path = None
        self.futures = []

    def download_file(self, url, file_path, file_name):
        file_full_path = os.path.join(file_path, file_name)
        if os.path.exists(file_full_path):
            self.log('[Exist][image][{}]'.format(file_full_path))
        else:
            r = requests.get(url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log('[Finish][image][{}]'.format(file_full_path))

    def download_video(self, id, file_path):
        file_full_path = os.path.join(file_path, "{}.{}".format(id, 'mp4'))
        if os.path.exists(file_full_path):
            self.log('[Exist][video][{}]'.format(file_full_path))
        else:
            video = pafy.new(id)
            best = video.getbest(preftype="mp4")
            r = requests.get(best.url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log('[Finish][video][{}]'.format(file_full_path))

    def download_project(self, hash_id):
        url = 'https://www.artstation.com/projects/{}.json'.format(hash_id)
        r = requests.get(url)
        j = r.json()
        assets = j['assets']
        title = j['slug'].strip()
        # self.log('=========={}=========='.format(title))
        username = j['user']['username']
        for asset in assets:
            assert(self.root_path)
            user_path = os.path.join(self.root_path, username)
            os.makedirs(user_path, exist_ok=True)
            file_path = os.path.join(user_path, title)
            if not self.no_image and asset['has_image']:  # 包含图片
                url = asset['image_url']
                file_name = urlparse(url).path.split('/')[-1]
                try:
                    self.futures.append(self.executor.submit(self.download_file,
                                                             url, file_path, file_name))
                except Exception as e:
                    print(e)
            if not self.no_video and asset['has_embedded_player']:  # 包含视频
                player_embedded = asset['player_embedded']
                id = re.search(
                    r'(?<=https://www\.youtube\.com/embed/)[\w_]+', player_embedded).group()
                try:
                    self.futures.append(self.executor_video.submit(
                        self.download_video, id, file_path))
                except Exception as e:
                    print(e)

    def get_projects(self, username):
        data = []
        if username is not '':
            page = 0
            while True:
                page += 1
                url = 'https://www.artstation.com/users/{}/projects.json?page={}'.format(
                    username, page)
                r = requests.get(url)
                if not r.ok:
                    self.log("[Error] Please input right username")
                    break
                j = r.json()
                total_count = int(j['total_count'])
                if total_count == 0:
                    self.log("[Error] Please input right username")
                    break
                if page is 1:
                    self.log('\n==========[{}] BEGIN=========='.format(username))
                data_fragment = j['data']
                data += data_fragment
                self.log('\n==========Get page {}/{}=========='.format(page,
                                                                     total_count // 50 + 1))
                if page > total_count / 50:
                    break
        return data

    def download_by_username(self, username):
        data = self.get_projects(username)
        if len(data) is not 0:
            future_list = []
            for project in data:
                future = self.executor.submit(
                    self.download_project, project['hash_id'])
                future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(self, usernames, type):
        self.no_image = type == 'video'
        self.no_video = type == 'image'
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split('/')[-1]
            if username not in username_set:
                username_set.add(username)
                self.download_by_username(username)
        futures.wait(self.futures)
        self.log("\n========ALL DONE========")
