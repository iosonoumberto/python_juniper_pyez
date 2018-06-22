#! /usr/bin/python

'''Import Required Modules'''
from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.utils.config import Config

import time
import argparse
import re
import sys
import yaml

'''Allow user to Define Username and Password'''
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fname", action="store", type=str, default='hosts',help="hosts file")
parser.add_argument("-d", "--det", action="store", type=str, default='a',help="detail level")

args =  parser.parse_args()

#CREATE HOSTS DICTIONARY
hosts={}
fhn = args.fname + ".txt"
fh = fp = open(fhn, 'r')  
line = fp.readline()
while line:
    h = line.split(" ")
    hosts[h[0]]=h[1]
    line = fp.readline()

hinfo={}
agginfo={'models':{},'versions':{},'dres':{}}

print "Starting collecting infos...\n"
for x in hosts.keys():
    '''Connect to device'''
    dev = Device(host=hosts[x], user="root", password="Embe1mpls")
    dev.open()
    hinfo[x]={}
    hinfo[x]['ip']=hosts[x]
    hinfo[x]['model']=dev.facts['model']
    hinfo[x]['hostname']=dev.facts['hostname']
    hinfo[x]['version']=dev.facts['version']
    hinfo[x]['serialnumber']=dev.facts['serialnumber']
    hinfo[x]['dre']=dev.facts['2RE']
    
    if agginfo['versions'].has_key(dev.facts['version']):
        agginfo['versions'][dev.facts['version']]+=1
    else:
        agginfo['versions'][dev.facts['version']]=1
    if agginfo['models'].has_key(dev.facts['model']):
        agginfo['models'][dev.facts['model']]+=1
    else:
        agginfo['models'][dev.facts['model']]=1
    if agginfo['dres'].has_key(dev.facts['2RE']):
        agginfo['dres'][dev.facts['2RE']]+=1
    else:
        agginfo['dres'][dev.facts['2RE']]=1
    
    dev.close()

print "Installed base versions"
for key, value in sorted(agginfo['versions'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
    print "%s: %s" % (key, value)

print "Installed base models"
for key, value in sorted(agginfo['models'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
    print "%s: %s" % (key, value)

print "Installed base double RE architecture"
for key, value in sorted(agginfo['dres'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
    print "%s: %s" % (key, value)

if args.det == "g":    
    print "Indivisual routers informaiton"
    for x in hinfo.keys():
        print ""+x+":"
        print "\thostname: "+hinfo[x]['hostname']
        print "\tmgmt ip: "+hinfo[x]['ip'].strip()
        print "\tmodel: "+hinfo[x]['model']
        print "\tversion: "+hinfo[x]['version']
        print "\tserial number: "+hinfo[x]['serialnumber']
        print "\tdouble RE: "+str(hinfo[x]['dre'])
        print "------------------"