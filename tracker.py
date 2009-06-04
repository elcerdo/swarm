#!/usr/bin/env python

import socket
import sys
import pickle
import time

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--port",dest="port",type="int",default=9999)
    parser.add_option("-b","--backlog",dest="backlog",type="int",default=5)
    parser.add_option("-s","--packet-size",dest="packet_size",type="int",default=1024)
    parser.add_option("--timeout",dest="timeout",type="float",default=1.)
    (options,args) = parser.parse_args()
    return options

def init_socket(options):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(('',options.port))
        s.listen(options.backlog)
        return s
    except socket.error, (code,message):
        if s:
            s.close()
        print "Could not open socket: " + message
        sys.exit(1)
        return None

def orly(client):
    client.send(pickle.dumps(None))

def ack(client,data):
    client.send(pickle.dumps(("ok",data)))

if __name__=="__main__":
    options = parse_options()
    s = init_socket(options)
    while True:
        client,address = s.accept()

        client.settimeout(options.timeout)
        data = client.recv(options.packet_size)
        print "Received: %s" % pickle.loads(data)
        if data:
            ack(client,"prout prout")
        client.close()


