import http.client as http_client
import ssl
import json
import os
import ssl
from urllib.parse import urlparse, ParseResult

import requests

from config import Config


class HttpClient:
    def log(self, message):
        if self._log_print:
            self._log_print(message)
        else:
            print(message)

    def __init__(self, log_print=None):
        self._log_print = log_print
        self._session = requests.session()
        self.proxy_setup(self._session)

    def http_client_get(self, url, ignoreCertificateError=None):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            parsed_url = urlparse(url)
            if ignoreCertificateError:
                context = ssl._create_unverified_context()
            else:
                context = None
            conn = http_client.HTTPSConnection(parsed_url.netloc, context=context)
            conn.request(
                "GET", parsed_url.path + "?" + parsed_url.query, headers=headers
            )

            resp = conn.getresponse()
        except ssl.SSLCertVerificationError:
            return self.http_client_get(url, ignoreCertificateError=True)
        except Exception as e:
            self.log(f"Connect error [{e}]")
            return

        return resp

    def http_client_get_json(self, url):
        resp = self.http_client_get(url)
        try:
            resp_str = resp.read().decode()
            json_result = json.loads(resp_str)
        except json.decoder.JSONDecodeError:
            self.log(f"json decode error\nurl:{url}\n{resp_str}")
            return
        return json_result

    def http_get(self, url):
        try:
            resp = self._session.get(url, timeout=10)
        except requests.exceptions.InvalidURL:
            self.log(f'"{url}" is not valid url')
            return
        return resp

    def proxy_setup(self, session=None):
        if not session:
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
                os.environ["HTTP_PROXY"] = http
            if https:
                proxys["https"] = https
                os.environ["HTTPS_PROXY"] = https
            session.proxies.update(proxys)

    @staticmethod
    def urlparse(url: str) -> ParseResult:
        return urlparse(url)
