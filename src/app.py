# -*- coding: utf-8 -*-

import os
from concurrent import futures

from tkinter import (
    Tk,
    Frame,
    Label,
    Button,
    Scrollbar,
    Text,
    Entry,
    messagebox,
    filedialog,
    StringVar,
)  # 引入Tkinter工具包
from tkinter import TOP, LEFT, BOTTOM, BOTH, X, Y, END
from tkinter import ttk

import config
from core import Core


class App(Frame):
    def log(self, value):
        self.text.configure(state="normal")
        self.text.insert(END, value + "\n")
        self.text.see(END)
        self.text.configure(state="disabled")

    def download(self):
        self.btn_download.configure(state="disabled")
        self.btn_download_txt.configure(state="disabled")
        username_text = self.entry_filename.get()
        if not username_text:
            messagebox.showinfo(title="Warning", message="Please input usernames")
        else:
            usernames = username_text.split(",")
            self.core.root_path = self.root_path.get()
            self.core.download_by_usernames(usernames, self.combobox_type.current())
        self.btn_download.configure(state="normal")
        self.btn_download_txt.configure(state="normal")

    def download_txt(self):
        self.btn_download.configure(state="disabled")
        self.btn_download_txt.configure(state="disabled")
        filename = os.path.normpath(
            filedialog.askopenfilename(
                filetypes=(("text files", "*.txt"), ("all files", "*.*"))
            )
        )
        if filename != ".":
            with open(filename, "r", encoding="utf-8") as f:
                usernames = []
                # 预处理，去掉注释与空白符
                for username in f.readlines():
                    username = username.strip()
                    if not username:
                        continue
                    sharp_at = username.find("#")
                    if sharp_at == 0:
                        continue
                    if sharp_at != -1:
                        username = username[:sharp_at]
                    usernames.append(username.strip())
            self.core.root_path = self.root_path.get()
            self.core.download_by_usernames(usernames, self.combobox_type.current())
        self.btn_download.configure(state="normal")
        self.btn_download_txt.configure(state="normal")

    def load_root_path(self):
        return config.read_config("config.ini", "Paths", "root_path")

    def save_root_path(self, root_path):
        config.write_config("config.ini", "Paths", "root_path", root_path)

    def browse_directory(self):
        root_path = os.path.normpath(filedialog.askdirectory())
        if root_path:
            self.root_path.set(root_path)
            self.save_root_path(root_path)

    def createWidgets(self):
        frame_tool = Frame(self.window)
        frame_path = Frame(self.window)
        frame_log = Frame(self.window)
        self.lbl_username = Label(frame_tool, text="Usernames(split by ','):")
        self.entry_filename = Entry(frame_tool)
        self.btn_download = Button(
            frame_tool,
            text="Download",
            command=lambda: self.executor_ui.submit(self.download),
        )
        self.btn_download_txt = Button(
            frame_tool,
            text="Download txt",
            command=lambda: self.executor_ui.submit(self.download_txt),
        )
        self.lbl_type = Label(frame_path, text="Type:")
        self.combobox_type = ttk.Combobox(frame_path, state="readonly")
        self.combobox_type["values"] = ("all", "image", "video")
        self.combobox_type.current(0)
        self.lbl_path = Label(frame_path, text="Path:")
        self.entry_path = Entry(frame_path, textvariable=self.root_path)
        self.btn_path_dialog = Button(
            frame_path, text="Browse", command=self.browse_directory
        )
        self.scrollbar = Scrollbar(frame_log)
        self.text = Text(frame_log)
        self.text.configure(state="disabled")
        self.lbl_status = Label(
            self.window,
            text="Feel free to use! Support: Sean Feng(sean@fantablade.com)",
        )

        frame_tool.pack(side=TOP, fill=X)
        self.lbl_username.pack(side=LEFT)
        self.entry_filename.pack(side=LEFT, fill=X, expand=True)
        self.btn_download.pack(side=LEFT)
        self.btn_download_txt.pack(side=LEFT)
        frame_path.pack(side=TOP, fill=X)
        self.lbl_type.pack(side=LEFT)
        self.combobox_type.pack(side=LEFT)
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

    def __init__(self, version):
        self.core = Core(self.log)
        master = Tk()
        Frame.__init__(self, master)
        master.title("ArtStation Downloader " + version)  # 定义窗体标题
        self.root_path = StringVar()
        self.root_path.trace_add("write", lambda name, index, mode: self.save_root_path(self.root_path.get()))
        root_path_config = self.load_root_path()
        self.root_path.set(
            root_path_config or os.path.join(os.path.expanduser("~"), "ArtStation")
        )
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.window = master
        self.pack()
        self.createWidgets()
