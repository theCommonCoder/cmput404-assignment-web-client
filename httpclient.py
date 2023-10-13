#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Mason Bly, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import time

# you may use urllib to encode data appropriately
import urllib.parse as parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        # host = socket.gethostbyname(host)
        if port is None:
            port = 80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((host, port))

    def get_code(self, data):
        code = re.search(r"[0-9]{3}", data)
        if not code:
            return 000
        return int(code.group(0))

    def get_headers(self, data):
        return None

    def get_body(self, data: str):
        _, body = data.split("\r\n\r\n", 1)
        return body

    def sendall(self, data: str):
        self.socket.sendall(data.encode("utf8"))
        # self.socket.shutdown(socket.SHUT_WR)

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):
        result: parse.ParseResult = parse.urlparse(url)
        resource = result.path if len(result.path) != 0 else "/"
        if result.params:
            resource += ";" + result.params
        if result.query:
            resource += "?" + result.query
        request = (
            f"GET {resource} HTTP/1.1\r\n"
            f"Host: {result.netloc}\r\n"
            "User-Agent: teapot\r\n"
            "Accept: */*\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        self.connect(result.hostname, result.port)
        self.sendall(request)

        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        result: parse.ParseResult = parse.urlparse(url)

        content = ""
        if args:
            content = parse.urlencode(args)
        resource = result.path if len(result.path) != 0 else "/"
        if result.params:
            resource += ";" + result.params
        if result.query:
            resource += "?" + result.query
        request = (
            f"POST {resource} HTTP/1.1\r\n"
            f"Host: {result.scheme}://{result.netloc}\r\n"
            f"User-Agent: I come from a school project\r\n"
            f"Accept: application/json\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"\r\n"
            f"{content}\r\n"
            f"\r\n"
        )
        self.connect(result.hostname, result.port)
        self.sendall(request)

        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))