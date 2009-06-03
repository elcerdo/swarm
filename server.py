#!/usr/bin/env python

"""
A simple echo server that handles some exceptions
"""

import socket
import sys

host = ''
port = 9999
backlog = 5
size = 1024
s = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind((host,port))
    s.listen(backlog)
except socket.error, (code,message):
    if s:
        s.close()
    print "Could not open socket: " + message
    sys.exit(1)
while 1:
    client, address = s.accept()
    data = client.recv(size)
    print "Received: " + data
    if data:
        client.send(data)
    client.close()
