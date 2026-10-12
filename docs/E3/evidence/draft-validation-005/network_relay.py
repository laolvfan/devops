"""Temporary authenticated proxy relay; no daemon configuration changes."""
import base64
import os
import select
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import ProxyHandler, Request, build_opener

proxy_url = os.environ['HTTPS_PROXY']
proxy = urlsplit(proxy_url)
if proxy.scheme != 'http':
    raise SystemExit('Expected the existing HTTP proxy')
credentials = f'{unquote(proxy.username or "")}:{unquote(proxy.password or "")}'.encode()
authorization = b'Proxy-Authorization: Basic ' + base64.b64encode(credentials)
hop_headers = {'connection', 'proxy-connection', 'proxy-authorization', 'transfer-encoding', 'keep-alive'}


class Relay(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_CONNECT(self):
        with socket.create_connection((proxy.hostname, proxy.port), timeout=30) as upstream:
            upstream.sendall(f'CONNECT {self.path} HTTP/1.1\r\nHost: {self.path}\r\n'.encode()
                             + authorization + b'\r\n\r\n')
            header = b''
            while not header.endswith(b'\r\n\r\n'):
                byte = upstream.recv(1)
                if not byte:
                    return
                header += byte
                if len(header) > 65536:
                    return
            self.connection.sendall(header)
            upstream.settimeout(None)
            while True:
                readable, _, _ = select.select([self.connection, upstream], [], [], 60)
                for source in readable:
                    data = source.recv(65536)
                    if not data:
                        return
                    (upstream if source is self.connection else self.connection).sendall(data)

    def do_GET(self):
        opener = build_opener(ProxyHandler({'http': proxy_url, 'https': proxy_url}))
        headers = {k: v for k, v in self.headers.items() if k.lower() not in hop_headers}
        request = Request(self.path, headers=headers, method=self.command)
        response = None
        for attempt in range(4):
            try:
                response = opener.open(request, timeout=60)
                break
            except (HTTPError, URLError) as exc:
                if attempt == 3:
                    self.send_error(exc.code if isinstance(exc, HTTPError) else 502)
                    return
                print(f'Retrying upstream request: {urlsplit(self.path).hostname}, attempt {attempt + 2}', flush=True)
                time.sleep(0.5)
        with response:
            self.send_response(response.status)
            for key, value in response.headers.items():
                if key.lower() not in hop_headers:
                    self.send_header(key, value)
            self.send_header('Connection', 'close')
            self.end_headers()
            while self.command != 'HEAD':
                data = response.read(65536)
                if not data:
                    break
                self.wfile.write(data)

    do_HEAD = do_GET


server = ThreadingHTTPServer(('127.0.0.1', 18443), Relay)
threading.Thread(target=server.serve_forever, daemon=True).start()
print(f'Temporary relay 127.0.0.1:18443 -> {proxy.hostname}:{proxy.port}', flush=True)
try:
    result = subprocess.run(sys.argv[1:])
finally:
    server.shutdown()
    server.server_close()
raise SystemExit(result.returncode)
