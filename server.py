#!/usr/bin/env python

import socket

ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ss.bind(("localhost",9999))
ss.listen(3)
while True:
    client,adrr=ss.accept()
    print client,adrr
    data=client.recv(1024)
    print data
    if data:
        client.send(data)
    client.close()
    


