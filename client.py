#!/usr/bin/env python

import socket

ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ss.bind(("localhost",9998))
ss.send("coucou")
data=ss.recv(1024)
s.close()

print "got back %s" % data

