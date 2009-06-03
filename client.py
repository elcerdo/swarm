#!/usr/bin/env python

"""
A simple echo client that handles some exceptions
"""

import socket
import sys
import time

host = 'sd-12155.dedibox.fr'
port = 9999
size = 1024
s = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
except socket.error, (value,message):
    if s:
        s.close()
    print "Could not open socket: " + message
    sys.exit(1)

delay=time.time()
s.send('Hello, world from ' + socket.gethostname())
data = s.recv(size)
delay-=time.time()
s.close()
print 'Received: %s in %fms' % (data,-1e3*delay)
