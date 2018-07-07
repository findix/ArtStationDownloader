#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""批量下载ArtStation图片

Copyright 2018 Sean Feng(sean@FantaBlade.com)

CHANGELOG

20180611 0.1.0-alpha1
允许在txt中使用Python风格的注释，即以#开头的内容会被忽略
对txt中的空白符进行处理
保存路径不再强制包含 ArtStation
默认保存路径现在为用户根路径

"""
__version__ = "0.1.0-alpha1"
# $Source$

from urllib.parse import urlparse
from concurrent import futures
from xml.dom.minidom import parseString

from tkinter import Tk, Frame, Label, Button, Scrollbar, Text, Entry, messagebox, filedialog  # 引入Tkinter工具包
from tkinter import TOP, LEFT, BOTTOM, BOTH, X, Y, END
from tkinter import ttk

import threading
import os
import requests
import json
import re
import pafy

import Config


class App(Frame):

    def log(self, value):
        self.text.configure(state="normal")
        self.text.insert(END, value + '\n')
        self.text.see(END)
        self.text.configure(state="disabled")

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
            self.log('[Exist][video][{}]'.format(file_full_path))

    def download_project(self, hash_id):
        url = 'https://www.artstation.com/projects/{}.json'.format(hash_id)
        r = requests.get(url)
        j = r.json()
        assets = j['assets']
        title = j['slug'].strip()
        # self.log('=========={}=========='.format(title))
        username = j['user']['username']
        for asset in assets:
            file_path = os.path.join(self.root_path, username, title)
            if asset['has_image']:  # 包含图片
                url = asset['image_url']
                file_name = urlparse(url).path.split('/')[-1]
                try:
                    self.executor.submit(self.download_file,
                                         url, file_path, file_name)
                except Exception as e:
                    print(e)
            if asset['has_embedded_player']:  # 包含视频
                player_embedded = asset['player_embedded']
                id = re.search(
                    r'(?<=https://www\.youtube\.com/embed/)[\w_]+', player_embedded).group()
                self.executor_video.submit(self.download_video, id, file_path)

    def get_projects(self, username):
        data = []
        if username is not '':
            page = 0
            user_path = os.path.join(self.root_path, username)
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
                    self.log('=========={}=========='.format(username))
                    os.makedirs(user_path, exist_ok=True)
                data_fragment = j['data']
                data += data_fragment
                self.log('==========Get page {}/{}=========='.format(page,
                                                                     total_count // 50 + 1))
                if page > total_count / 50:
                    break
        return data

    def download_by_usernames(self, usernames):
        max_workers = 20
        if self.executor is None:
            self.executor = futures.ThreadPoolExecutor(max_workers)
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split('/')[-1]
            username_set.add(username)
        for username in username_set:            
            data = self.get_projects(username)
            if len(data) is not 0:
                args = [project['hash_id'] for project in data]
                for hash_id in args:
                    self.executor.submit(self.download_project, hash_id)

    def download(self):
        self.btn_download.configure(state="disabled")
        self.btn_download_txt.configure(state="disabled")
        username_text = self.entry_filename.get()
        if len(username_text) is 0:
            messagebox.showinfo(
                title='Warning', message='Please input usernames')
        else:
            usernames = username_text.split(',')
            self.download_by_usernames(usernames)
        self.btn_download.configure(state="normal")
        self.btn_download_txt.configure(state="normal")

    def download_txt(self):
        self.btn_download.configure(state="disabled")
        self.btn_download_txt.configure(state="disabled")
        filename = os.path.normpath(filedialog.askopenfilename(
            filetypes=(('text files', '*.txt'), ("all files", "*.*"))))
        if filename is not '.':
            with open(filename, "r") as f:
                usernames = []
                # 预处理，去掉注释与空白符
                for username in f.readlines():
                    username = username.strip()
                    if len(username) is 0:
                        continue
                    sharp_at = username.find('#')
                    if sharp_at is 0:
                        continue
                    if sharp_at is not -1:
                        username = username[:sharp_at]
                    usernames.append(username.strip())
            self.download_by_usernames(usernames)
        self.btn_download.configure(state="normal")
        self.btn_download_txt.configure(state="normal")

    def browse_directory(self):
        dir = os.path.normpath(filedialog.askdirectory())
        if dir is not '':
            self.root_path = dir 
            Config.write_config('config.ini', 'Paths',
                                'root_path', self.root_path)
            self.entry_path.delete(0, END)
            self.entry_path.insert(0, self.root_path)

    def createWidgets(self):
        frame_tool = Frame(self.window)
        frame_path = Frame(self.window)
        frame_log = Frame(self.window)
        self.lbl_username = Label(
            frame_tool, text='Usernames(split by \',\'):')
        self.entry_filename = Entry(frame_tool)
        self.btn_download = Button(
            frame_tool, text='Download', command=lambda: self.executor_ui.submit(self.download))
        self.btn_download_txt = Button(
            frame_tool, text='Download txt', command=lambda: self.executor_ui.submit(self.download_txt))
        self.lbl_path = Label(frame_path, text='Path:')
        self.entry_path = Entry(frame_path)
        self.entry_path.insert(END, self.root_path)
        self.btn_path_dialog = Button(
            frame_path, text="Browse", command=lambda: self.browse_directory())
        self.scrollbar = Scrollbar(frame_log)
        self.text = Text(frame_log)
        self.text.configure(state="disabled")
        self.lbl_status = Label(
            self.window, text='Feel free to use! Support: Sean Feng(sean@FantaBlade.com)')

        frame_tool.pack(side=TOP, fill=X)
        self.lbl_username.pack(side=LEFT)
        self.entry_filename.pack(side=LEFT, fill=X, expand=True)
        self.btn_download.pack(side=LEFT)
        self.btn_download_txt.pack(side=LEFT)
        frame_path.pack(side=TOP, fill=X)
        self.lbl_path.pack(side=LEFT)
        self.entry_path.pack(side=LEFT, fill=X, expand=True)
        self.btn_path_dialog.pack(side=LEFT)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=LEFT, fill=Y)
        frame_log.pack(side=TOP, fill=BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.text.focus()
        self.lbl_status.pack(side=LEFT, fill=X, expand=True)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title('ArtStation Downloader ' + __version__)  # 定义窗体标题
        root_path_config = Config.read_config(
            'config.ini', 'Paths', 'root_path')
        self.root_path = os.path.join(
            os.path.expanduser("~")) if root_path_config is '' else root_path_config
        self.executor = None
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.window = master
        self.pack()
        self.createWidgets()


def main():
    window = Tk()
    app = App(master=window)
    app.mainloop()  # 进入主循环，程序运行


if __name__ == '__main__':
    main()
