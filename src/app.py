# -*- coding: utf-8 -*-

import os
import PySimpleGUI as sg

import config
from core import Core, DownloadSorting


class App:
    def __init__(self, version):
        self.core = Core(self.log)
        self.user_settings = sg.UserSettings()

        # 兼容模式
        if not self.user_settings.exists("root_path"):
            root_path = config.read_config("config.ini", "Paths", "root_path")
            if root_path:
                self.user_settings.set("root_path", root_path)

        self.root_path = self.user_settings.get(
            "root_path", os.path.join(os.path.expanduser("~"), "ArtStation")
        )
        self.download_sorting: DownloadSorting = DownloadSorting[
            self.user_settings.get("download_sorting", DownloadSorting.TITLE_BASED.name)
        ]
        self.window = sg.Window(
            "ArtStation Downloader " + version,
            layout=self.create_layout(),
            finalize=True,
        )

        self.window["-DOWNLOAD-SORTING-"].Update(self.download_sorting)

        self.event_callbacks = {
            "-DOWNLOAD-": lambda: self.window.perform_long_operation(self.download, ""),
            "-DOWNLOAD_TXT-": self.get_download_txt_file,
            "continue_download_txt": lambda args: self.window.perform_long_operation(
                lambda: self.download_txt(args), ""
            ),
            "-DOWNLOAD-SORTING-": self._set_download_sorting,
            "log": self._log,
            "popup": self._popup,
            "set_download_buttons": self._set_download_buttons,
        }

    def _set_download_sorting(self, value: DownloadSorting):
        self.download_sorting = value
        self.user_settings.set("download_sorting", value.name)

    def _log(self, value):
        current_text = self.window["-LOG-"].get()
        self.window["-LOG-"].update(f"{current_text}\n{value}\n")
        self.window["-LOG-"].Widget.see("end")

    def log(self, value):
        self.window.write_event_value("log", value)

    def _set_download_buttons(self, state):
        self.window["-DOWNLOAD-"].update(disabled=not state)
        self.window["-DOWNLOAD_TXT-"].update(disabled=not state)

    def _popup(self, args):
        message, title = args
        sg.popup_ok(
            message,
            title=title,
            modal=True,
        )

    def download(self):
        username_text = self.window["-USERNAME-"].get()
        if not username_text:
            self.window.write_event_value(
                "popup", ("Please input usernames", "Warning")
            )
            return
        self.window.write_event_value("set_download_buttons", False)
        usernames = username_text.split(",")
        self.core.root_path = self.root_path
        self.core.download_by_usernames(
            usernames, self.window["-TYPE-"].get(), self.download_sorting
        )
        self.window.write_event_value("set_download_buttons", True)

    def get_download_txt_file(self):
        self.window.write_event_value("set_download_buttons", False)
        filename = sg.popup_get_file(
            "Select a file", file_types=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        self.window.write_event_value("continue_download_txt", filename)

    def download_txt(self, filename):
        if filename and filename != ".":
            with open(filename, "r", encoding="utf-8") as f:
                usernames = []
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
                self.core.root_path = self.root_path
                self.core.download_by_usernames(
                    usernames, self.window["-TYPE-"].get(), self.download_sorting
                )
        self.window.write_event_value("set_download_buttons", True)

    def browse_directory(self):
        root_path = sg.popup_get_folder("Select a folder")
        if root_path:
            self.root_path = root_path
            self.window["-PATH-"].update(root_path)
            self.user_settings.set("root_path", root_path)

    def create_layout(self):
        sg.theme("Dark Blue 3")
        layout = [
            [sg.Text('Usernames (split by ","):'), sg.InputText(key="-USERNAME-")],
            [
                sg.Text("Type:"),
                sg.Combo(
                    values=("all", "image", "video"),
                    key="-TYPE-",
                    default_value="all",
                    readonly=True,
                    enable_events=True,
                ),
                sg.Text("File Download Sorting"),
                sg.Combo(
                    tuple(DownloadSorting.__members__.values()),
                    key="-DOWNLOAD-SORTING-",
                    default_value=DownloadSorting.TITLE_BASED,
                    readonly=True,
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Path:"),
                sg.InputText(key="-PATH-", default_text=self.root_path),
                sg.FolderBrowse("Browse", key="-BROWSE-"),
            ],
            [
                sg.Button("Download", key="-DOWNLOAD-", bind_return_key=True),
                sg.Button("Download txt", key="-DOWNLOAD_TXT-"),
            ],
            [sg.Multiline(size=(80, 20), key="-LOG-", disabled=True)],
            [sg.StatusBar("Feel free to use! Support: Sean Feng(sean@fantablade.com)")],
        ]
        return layout

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event in self.event_callbacks:
                if event in values:
                    self.event_callbacks[event](values[event])
                else:
                    self.event_callbacks[event]()

        self.window.close()
