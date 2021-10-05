#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    def parse_url(self, url):
        result = urllib.parse.urlparse(url)
        self.port = result.port if result.port else 80
        self.path = result.path if result.path != "" else "/"
        self.hostname = result.hostname

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split()[1]
        return int(code)

    def get_headers(self, data):
        headers = data.split("\r\n\r\n")[0].split("\r\n")[1:]
        header_info = {}
        for header in headers:
            field_name = header.split(":")[0]
            field_value = header.split(":")[1]
            header_info[field_name] = field_value
        return header_info

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    # This will generate the body for a POST form in a dict
    def generate_form(self, entity={}):
        body = ""
        for key, value in entity.items():
            body += "{key}={value}&".format(key=key, value=value)
        # Remove the extra &
        if body != "":
            body = body[:-1]
        return body
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.parse_url(url)
        self.connect(self.hostname, self.port)
        # Create the status line
        body = "GET {path} HTTP/1.1\r\n".format(path=self.path)
        # Set the headers
        body += "Host: {host}:{port}\r\n".format(host=self.hostname, port=self.port)
        body += "Connection: close\r\n"
        body += "Accept: */*\r\n"
        body += "\r\n"
        # End of headers

        # Send the requests
        self.sendall(body)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        self.parse_url(url)
        self.connect(self.hostname, self.port)

        if args != None:
            form_body = self.generate_form(args)
        else:
            form_body = ""
        # Create the status line
        body = "POST {path} HTTP/1.1\r\n".format(path=self.path)
        # Set the headers
        body += "Host: {host}:{port}\r\n".format(host=self.hostname, port=self.port)
        body += "Connection: close\r\n"
        if args != None:
            body += "Content-Type: application/x-www-form-urlencoded\r\n"
            body += "Content-Length: {}\r\n".format(len(form_body))
        else:
            body += "Content-Length: {}\r\n".format(0)
        body += "\r\n"
        # End of Headers
        body += form_body
        
        # send the request
        self.sendall(body)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
