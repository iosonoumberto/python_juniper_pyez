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
parser.add_argument("-u", "--username", action="store", type=str, default='root',
help="Username for Connection")
parser.add_argument("-p", "--password", action="store", type=str, default='Embe1mpls',
help="Password for Connection")
parser.add_argument("-a", "--address", action="store", type=str, default='172.30.200.231',
help="Password for Connection")
parser.add_argument("-f", "--fname", action="store", type=str, default='junipervmx',
help="Configuration file")

args =  parser.parse_args()

print args

hosts={}
fh = fp = open('hosts.txt', 'r')  
line = fp.readline()
while line:
    h = line.split(" ")
    hosts[h[0]]=h[1]
    line = fp.readline()

cfbase=args.fname
jfile = "jtemplates/"+cfbase+".j2"

for x in hosts.keys():
    '''Connect to device'''
    print 'Connecting to {0}...'.format(x)
    dev = Device(host=hosts[x], user=args.username, password=args.password)
    dev.open(gather_facts=False)
    cfg = Config(dev)
    yfile = "ytemplates/"+x+"_"+cfbase+".yaml"
    s=open(yfile).read()
    myvars=yaml.load(s)
    cfg.load(template_path=str(jfile), template_vars=myvars, format='set')
    if cfg.commit_check():
        if cfg.commit:
            print 'Committing...'
            cfg.commit(timeout=300)
            print 'Successfully Committed'
        else:
            print 'Commit Failed'
    else:
        print 'Commit Check Failed'
    dev.close()
