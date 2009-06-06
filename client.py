#!/usr/bin/env python

import socket
import sys
import time
import pickle
import random
import hashlib
import threading
import re
import os

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
    parser.add_option("-t","--tracker",dest="tracker",type="string",default="sd-12155.dedibox.fr")
    parser.add_option("-b","--backlog",dest="backlog",type="int",default=5)
    parser.add_option("-s","--packet-size",dest="packet_size",type="int",default=1024)
    parser.add_option("--timeout",dest="timeout",type="int",default=2)
    parser.add_option("--chocketime",dest="chocke_time",type="int",default=3)
    (options,args) = parser.parse_args()
    return options


class Client:
    def __init__(self,options):
        self.options = options
        self.seed = hashlib.sha1("%s%s%s" % (socket.gethostname(),random.randint(0,65535),time.time())).hexdigest()
        self.peers = {}
        self.idpeers = hashlib.sha1("%s" % self.peers).hexdigest()
        self.connected = False

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
        while not self.connected:
            try:
                self.send_resquest({"action":"sayhello","name":socket.gethostname()})
                self.connected = True
            except NoWayError:
                self.connected = False
                time.sleep(options.chocke_time)

    def say_bye(self):
        if not self.connected: return 
        
        self.send_resquest({"action":"goodbye"})
        self.connected = False

    def chocke_tracker(self,links):
        try:
            peers,idpeers = self.send_resquest({"action":"chocke","idpeers":self.idpeers,"links":[(link.target_idseed,link.success,link.avg) for link in links.values() if link.last_ping is not None]})
            if idpeers != self.idpeers:
                self.peers = peers
                self.idpeers = idpeers
                return True
            else:
                return False
        except NoWayError:
            self.connected = False
            return False

class DataPing:
    class Pinger(threading.Thread):
        def __init__ (self,link,n=10):
            threading.Thread.__init__(self)
            self.link = link
            self.lifeline = re.compile(r"(\d+) received")
            self.statline = re.compile(r"(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)")
            self.n = n

        def run(self):
            pingaling = os.popen("ping -q -c%d %s" % (self.n,self.link.ip),"r")
            success = False
            avg = 0
            std = 0

            while 1:
                line = pingaling.readline()
                if not line: break

                igot = re.findall(self.lifeline,line)
                if igot:
                    success = (int(igot[0])==self.n)

                igot = re.findall(self.statline,line)
                if igot:
                    avg = float(igot[0][1])
                    std = float(igot[0][3])

            self.link.update(success,avg,std)

    class Link:
        def __init__(self,target_idseed,ip,name):
            self.last_ping = None
            self.success = False
            self.count = 0
            self.avg = 0
            self.std = 0
            self.target_idseed = target_idseed
            self.ip = ip
            self.name = name

        def update(self,success,avg,std):
            self.count += 1
            self.last_ping = time.time()
            self.success = success
            self.avg = avg
            self.std = std

        def __cmp__(self,y):
            if self.last_ping is None and y.last_ping is None:
                return 0
            if self.last_ping is not None and y.last_ping is None:
                return -1
            if self.last_ping is None and y.last_ping is not None:
                return 1
            if self.last_ping is not None and y.last_ping is not None:
                return -cmp(self.count,y.count)

        def __repr__(self):
            base="name=%s ip=%s" % (self.name,self.ip)
            if self.last_ping is None:
                return "%s never pinged" % base
            elif not self.success:
                return "%s count=%d success=%d" % (base,self.count,self.success)
            elif self.success:
                return "%s count=%d success=%d avg=%f std=%f" % (base,self.count,self.success,self.avg,self.std)

    def __init__(self,options):
        self.links = {}
        self.pinger = None
        self.options = options

    def update(self,peers):
        active_idseed = set(peers.keys())
        active_links = set(self.links.keys())

        for idseed in active_idseed.difference(active_links):
            self.links[idseed] = DataPing.Link(idseed,peers[idseed][0],peers[idseed][1])

        for idseed in active_links.difference(active_idseed):
            del self.links[idseed]

    def manage_pinger(self):
        if self.pinger is not None and not self.pinger.isAlive():
            print "Pinger acquired data %s" % self.pinger.link
            self.pinger = None

        if self.pinger is None and self.links:
            candidates = self.links.values()
            candidates.sort()
            #print "Launching pinger on link %s" % candidates[-1]
            self.pinger = DataPing.Pinger(candidates[-1])
            self.pinger.start()



if __name__=="__main__":
    options = parse_options()
    client = Client(options)
    dataping = DataPing(options)

    try:
        while True:
            if not client.connected:
                print "Connecting to tracker"
                client.say_hi()

            if client.chocke_tracker(dataping.links):
                dataping.update(client.peers)
                print "Updated peers (%d peers)" % len(client.peers)

            dataping.manage_pinger()
            time.sleep(options.chocke_time)
    except socket.error, e:
        print "Connection error: %s" % e
    except KeyboardInterrupt:
        print "Disconnecting tracker"
        client.say_bye()
