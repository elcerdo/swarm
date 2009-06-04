#!/usr/bin/env python

import socket
import sys
import time
import pickle
import random
import hashlib

class NoWayError(Exception):
    pass

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--port",dest="port",type="int",default=9999)
    parser.add_option("-t","--tracker",dest="tracker",type="string",default="localhost")
    parser.add_option("-b","--backlog",dest="backlog",type="int",default=5)
    parser.add_option("-s","--packet-size",dest="packet_size",type="int",default=1024)
    parser.add_option("--timeout",dest="timeout",type="float",default=1.)
    (options,args) = parser.parse_args()
    return options

def init_socket(options):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((options.tracker,options.port))
        s.settimeout(options.timeout)
        return s
    except socket.error, (value,message):
        if s:
            s.close()
        print "Could not open socket: " + message
        sys.exit(1)
        return None

def create_seed():
    sha1 = hashlib.sha1("%s%s%s" % (socket.gethostname(),random.randint(0,65535),time.time()))
    return sha1.hexdigest()

def send_resquest(data,options):
    s = init_socket(options)
    s.send(pickle.dumps(data))
    rec_data = pickle.loads(s.recv(options.packet_size))
    s.close()
    if rec_data is None:
        raise NoWayError
    return rec_data[1]

def say_hi(seed,options):
    return send_resquest({"action":"sayhello","name":socket.gethostname(),"idseed":seed},options)

def say_bye(seed,options):
    return send_resquest({"action":"goodbye","idseed":seed},options)

if __name__=="__main__":
    options = parse_options()
    seed = create_seed()

    say_hi(seed,options)

    try:
        while True:
            time.sleep(1)

            tic = time.time()
            rec_data = send_resquest({"action":"chocke","name":socket.gethostname(),"seed":seed},options)
            toc = time.time()

            if not rec_data:
                print "Problem connecting to tracker"
                continue

            print 'Received: %s in %fms' % (rec_data,1e3*(toc-tic))
    except KeyboardInterrupt:
        say_bye(seed,options)
