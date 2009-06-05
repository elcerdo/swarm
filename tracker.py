#!/usr/bin/env python

import threading
import socket
import sys
import pickle
import time
import signal

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--port",dest="port",type="int",default=9999)
    parser.add_option("-b","--backlog",dest="backlog",type="int",default=5)
    parser.add_option("-s","--packet-size",dest="packet_size",type="int",default=1024)
    parser.add_option("--timeout",dest="timeout",type="float",default=1.)
    parser.add_option("--chocketimeout",dest="chocke_timeout",type="float",default=3.)
    (options,args) = parser.parse_args()
    return options

def init_server_socket(options):
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

def orly(client,data=None):
    client.send(pickle.dumps(("err",data)))

def ack(client,data=None):
    client.send(pickle.dumps(("ok",data)))

class Peers:
    def __init__(self):
        self.__peers = {}
        self.__peers_lock = threading.Lock()

    def register_peer(self,data,client):
        idseed = data["idseed"]

        self.__peers_lock.acquire()
        if idseed not in self.__peers:
            self.__peers[idseed] = time.time()
            peers_list=[id for id in self.__peers]
            self.__peers_lock.release()
            ack(client,peers_list)
        else:
            self.__peers_lock.release()
            orly(client,"already registered")

    def chocke_peer(self,data,client):
        idseed = data["idseed"]

        self.__peers_lock.acquire()
        if idseed in self.__peers:
            self.__peers[idseed] = time.time()
            peers_list=[id for id in self.__peers]
            self.__peers_lock.release()
            ack(client,peers_list)
        else:
            self.__peers_lock.release()
            orly(client,"not registered yet")

    def unregister_peer(self,data,client):
        idseed = data["idseed"]

        self.__peers_lock.acquire()
        if idseed in self.__peers:
            del self.__peers[idseed]
            self.__peers_lock.release()
            ack(client)
        else:
            self.__peers_lock.release()
            orly(client,"not registered")

    def __str__(self):
        current_time = time.time()

        self.__peers_lock.acquire()
        aa = ["%d peers" % len(self.__peers)]
        for idseed,data in self.__peers.items():
            aa.append("%s last seen %fs ago" % (idseed,current_time-data))
        self.__peers_lock.release()

        return '\n'.join(aa)

    def clean_unchocked_peers(self,chocke_timeout):
        current_time = time.time()

        self.__peers_lock.acquire()
        for idseed,data in self.__peers.items():
            if current_time-data > chocke_timeout:
                del self.__peers[idseed]
        self.__peers_lock.release()

class Server(threading.Thread):
    def __init__(self,peers,options):
        threading.Thread.__init__(self)
        self.options = options
        self.peers = peers
        self.quit = False

    def run(self):
        actions = {"sayhello":self.peers.register_peer,"chocke":self.peers.chocke_peer,"goodbye":self.peers.unregister_peer}

        server = init_server_socket(options)
        server.settimeout(1)
        while not self.quit:
            try:
                client,address = server.accept()

                client.settimeout(options.timeout)
                data = pickle.loads(client.recv(options.packet_size))
                if "action" in data and "idseed" in data and data["action"] in actions:
                    actions[data["action"]](data,client)
                else:
                    orly(client,"invalid action or no idseed")

                client.close()
            except socket.timeout:
                pass

        server.close()

class Cleaner(threading.Thread):
    def __init__(self,peers,options):
        threading.Thread.__init__(self)
        self.peers = peers
        self.options = options
        self.quit = False

    def run(self):
        while not self.quit:
            self.peers.clean_unchocked_peers(self.options.chocke_timeout)

            time.sleep(self.options.timeout)
            
if __name__=="__main__":
    peers = Peers()
    options = parse_options()
    server = Server(peers,options)
    cleaner = Cleaner(peers,options)

    server.start()
    cleaner.start()
    quit = False
    while not quit:
        cmd = raw_input("> ").strip().split()
        if not cmd:
            continue

        if cmd[0]=="quit" or cmd[0]=="q":
            quit = True
        elif cmd[0]=="status" or cmd[0]=="s":
            print peers


    server.quit = True
    cleaner.quit = True
    cleaner.join()
    server.join()
    
