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
    dot.set_type('digraph')

    nodes={}
    for (sid,rid),(sn,rn,ss,time) in data.items():
        if sid not in nodes:
            node=pydot.Node(sn.split('.')[0])
            dot.add_node(node)
            nodes[sid]=node
        if rid not in nodes:
            node=pydot.Node(rn.split('.')[0])
            dot.add_node(node)
            nodes[rid]=node
        
        if ss:
                edge=pydot.Edge(nodes[sid],nodes[rid])
                edge.set_label("%.1f" % time)
                edge.set_len("%f" % time)
                dot.add_edge(edge)

    dot.write(options.output,format="png")


