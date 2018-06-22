#! /usr/bin/python

'''Import Required Modules'''
from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.utils.config import Config
from jnpr.junos.op.fpc import FpcHwTable
from jnpr.junos.op.fpc import FpcInfoTable
from jnpr.junos.utils.scp import SCP
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.op.routes import RouteTable

import time
import argparse
import re
import sys
import yaml
import datetime

from getpass import getpass
from pprint import pprint as pp
from lxml import etree

'''Allow user to Define Username and Password'''
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fname", action="store", type=str, default='yhosts',help="hosts file")
parser.add_argument("-d", "--det", action="store", type=str, default='a',help="detail level")
parser.add_argument("-l", "--logs", action="store", type=str, default='logsdefault',help="logs and filters")

args =  parser.parse_args()

#LOAD INPUT YAML FILE
yinput = args.fname + ".yaml"
stream = open(yinput, 'r')
hosts = yaml.load(stream)


print "Starting collecting infos...\n"
for x in hosts.keys():
    '''Connect to device'''
    dev = Device(host=hosts[x]['ip'], user="root", password="Embe1mpls")
    dev.open()
    
    print "Working on " + str(x) + " at " + str(hosts[x]['ip']) + "..."
    
    #LOAD BGP SUMMARY MODEL
    yml = '''
    bgpNeighbor:
     rpc: get-bgp-summary-information
     item: bgp-peer
     key: peer-address
     view: bgpNeighborView
     
    bgpNeighborView:
     fields:
      peer: peer-address
      state: peer-state
    '''
    
    globals().update(FactoryLoader().load(yaml.load(yml)))
    bt = bgpNeighbor(dev).get()
    
    #CHECK NOT ESTABLISHED BGP SESSIONS
    noest=[]
    for y in bt.keys():
        if bt[y]['state'] != "Established":
            noest.append(bt[y]['peer'])
    
    if len(noest) > 0:
        print "Non established BGP sessions: " + str(len(noest))
        print "Involved peers: "
        for z in noest:
            print "\t- " + z
    else:
        print "All BGP sessions are in a Established state."
    
    #LOAD ROUTES INFO
    yml = '''
    bgpRoutes:
     rpc: get-route-information
     args:
      protocol: bgp
      extensive: True
     item: route-table/rt
     key: rt-destination
     view: bgpView
     
    bgpView:
     fields:
      as_path: rt-entry/as-path
      rt_destination: rt-destination
      rt_prefix_length: rt-prefix-length
      community: rt-entry/communities/community
    '''
    
    globals().update(FactoryLoader().load(yaml.load(yml)))
    bt = bgpRoutes(dev).get()
    
    #CHECK FOR BAD PATTERNS
    for y in bt.keys():
        flag=0
        
        #CHECK FOR BAD AS PATHS
        fbap=[]
        for z in hosts[x]['badas']:
            if z in bt[y]['as_path']:
                fbap.append(z)
                if flag==0:
                    print "Route " + y + "/" + bt[y]['rt_prefix_length'] + " contains:"
                flag=1
        if len(fbap)>0:
            print "\tbad AS PATH(s): " + str(fbap)
    
        #CHECK FOR BAD COMMUNITIES
        fbc=[]
        if bt[y]['community'] != None:
            for z in hosts[x]['badcomm']:
                if z in bt[y]['community']:
                    fbc.append(z)
                    if flag==0:
                        print "Route " + y + "/" + bt[y]['rt_prefix_length'] + " contains:"
                    flag=1
            if len(fbc)>0:
                print "\tbad community(s): " + str(fbc)
    
        #CREATE ROUTES IN ADDR/MASK FORMAT
        fullroute = y + "/" + bt[y]['rt_prefix_length']
        if fullroute in hosts[x]['badroutes']:
            if flag==0:
                print "Route " + y + "/" + bt[y]['rt_prefix_length'] + " contains:"
            print "\tis a bad route."
            flag=1
    
    #CHECK ADVERTISED ROUTES
    for y in hosts[x]['checkann'].keys():
        routes = RouteTable(dev)
        routes.get(advertising_protocol_name="bgp", neighbor=y)
        adv = routes.keys()
        nf=[]
        
        print "Checking advertised routes to neighbor " + y + " " + str(hosts[x]['checkann'][y])
        for z in hosts[x]['checkann'][y]:
            if z not in adv:
                print "\t" + z + " not found"
                nf.append(z)
        
        if len(nf)==0:
            print "\tAll OK!"
        
    dev.close()



