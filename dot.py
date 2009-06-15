#!/usr/bin/env python

import pydot
import pickle

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i","--input",dest="input",type="string",default="dump.pck")
    parser.add_option("-o","--output",dest="output",type="string",default="test.png")
    (options,args) = parser.parse_args()
    return options

if __name__=="__main__":
    options = parse_options()
    file=open(options.input,"rb")
    data=pickle.load(file)
    file.close()

    dot=pydot.Dot()
    dot.set_prog('neato')
    dot.set_type('graph')

    times={}
    nodes={}
    for (sid,rid),(sn,rn,ss,time) in data.items():
        if sid==rid: #parse self pinging node
            assert(ss)
            assert(sn==rn)
            node=pydot.Node(sn.split('.')[0])
            nodes[sid]=(time,node)
            dot.add_node(node)
            del data[(sid,rid)]
        elif not ss: #remove failed ping
            try:
                del data[(sid,rid)]
                del data[(rid,sid)]
            except KeyError:
                pass

    edges={}
    while data:
        (sid,rid),(sn,rn,ss,time)=data.popitem()
        assert(ss)
        edges[frozenset((sid,rid))]=(nodes[sid][1],nodes[rid][1],(time-nodes[sid][0]+data[(rid,sid)][3]-nodes[rid][0])/2)
        del data[(rid,sid)]

    max_time=max(time for sn,rn,time in edges.values())
    min_time=min(time for sn,rn,time in edges.values())
    def clamp(time,min_len=2,max_len=5):
        return min_len+(max_len-min_len)*(time-min_time)/(max_time-min_time)

    for sn,rn,time in edges.values():
        edge=pydot.Edge(sn,rn)
        edge.set_label("%.2f" % time)
        edge.set_len("%f" % clamp(time))
        dot.add_edge(edge)

    dot.write(options.output,format="png")


