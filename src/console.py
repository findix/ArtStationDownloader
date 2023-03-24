# -*- coding: utf-8 -*-

from core import Core


class Console:
    def __init__(self):
        self.core = Core()

    def download_by_usernames(self, usernames, directory, download_type, download_sorting):
        self.core.root_path = directory
        self.core.download_by_usernames(usernames, download_type, download_sorting)
