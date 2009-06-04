#!/usr/bin/env python

"""
A simple echo client that handles some exceptions
"""

import socket
import sys
import time
import pickle
import random

host = 'sd-12155.dedibox.fr'
host = 'localhost'
port = 9999
size = 1024

while True:
    s = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))
    except socket.error, (value,message):
        if s:
            s.close()
        print "Could not open socket: " + message
        sys.exit(1)

    snd_data={"host":socket.gethostname(),"seed":random.randint(0,255),"time":time.time()}
    s.send(pickle.dumps(snd_data))
    rec_data = pickle.loads(s.recv(size))
    s.close()
    print 'Received: %s in %fms' % (rec_data,1e3*(time.time()-rec_data["time"]))
    time.sleep(1)
