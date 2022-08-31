# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
# import the socket module
import socket

# Create a socket instance
socketObject = socket.socket()
# Using the socket connect to a server...in this case localhost
socketObject.connect(("localhost", 35495))
print("Connected to localhost")

# Send a message to the web server to supply a page as given by Host param of GET request
HTTPMessage = (
    "hi there!"  # "GET / HTTP/1.1\r\nHost: localhost\r\n Connection: close\r\n\r\n"
)
bytes = str.encode(HTTPMessage)
socketObject.sendall(bytes)

# Receive the data
while True:
    data = socketObject.recv(1024)
    if data == b"":
        print("Connection closed")
        break
    d = str(data)
    print(d.replace("\\n", "\n"))

socketObject.close()
