#!/usr/bin/env python

import socket
import sys
import time
import pickle
import random
import hashlib

class NoWayError(Exception):
    def __init__(self,request,answer):
        self.request=request
        self.answer=answer
    def __str__(self):
        return "Error while sendind query '%s' got '%s'" % (self.request,self.answer)

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--port",dest="port",type="int",default=9999)
    parser.add_option("-t","--tracker",dest="tracker",type="string",default="localhost")
    parser.add_option("-b","--backlog",dest="backlog",type="int",default=5)
    parser.add_option("-s","--packet-size",dest="packet_size",type="int",default=1024)
    parser.add_option("--timeout",dest="timeout",type="int",default=1)
    parser.add_option("--chocketime",dest="chocke_time",type="int",default=3)
    (options,args) = parser.parse_args()
    return options


class Client:
    def __init__(self,options):
        self.options = options
        self.seed = hashlib.sha1("%s%s%s" % (socket.gethostname(),random.randint(0,65535),time.time())).hexdigest()
        self.peers = []
        self.idpeers = hashlib.sha1("%s" % self.peers).hexdigest()

    def send_resquest(self,send_data):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((self.options.tracker,self.options.port))
        s.settimeout(self.options.timeout)
        send_data["idseed"]=self.seed
        s.send(pickle.dumps(send_data))
        answer,recv_data = pickle.loads(s.recv(self.options.packet_size))
        s.close()
        if answer!="ok":
            raise NoWayError(send_data,recv_data)
            return None
        else:
            return recv_data

    def say_hi(self):
        self.send_resquest({"action":"sayhello","name":socket.gethostname()})

    def say_bye(self):
        self.send_resquest({"action":"goodbye"})

    def chocke_tracker(self):
        peers,idpeers = self.send_resquest({"action":"chocke","idpeers":self.idpeers})
        if idpeers != self.idpeers:
            self.peers = peers
            self.idpeers = idpeers
            print "Updated peers %s" % self.peers


if __name__=="__main__":
    options = parse_options()
    client = Client(options)

    client.say_hi()
    try:
        while True:
            time.sleep(options.chocke_time)
            client.chocke_tracker()
    except KeyboardInterrupt:
        client.say_bye()
