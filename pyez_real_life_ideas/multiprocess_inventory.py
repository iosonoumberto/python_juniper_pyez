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
from prettytable import PrettyTable
from multiprocessing import Pool


def f(x):
    dev = Device(host=x[1], user="root", password="Embe1mpls")
    dev.open()
    
    print "Working on " + str(x[0]) + " at " + str(x[1][:-1]) + "..."
    print ""
    
    fname = "./mpinvout/"+str(x[0])+"_"+str(x[1][:-1])+".txt"
    fo = open (fname,"w")
    
    ##### PRINT CHASSIS INFORMATION
    fo.write("\n")
    fo.write("----- CHASSIS INVENTORY -----\n")
    fo.write("\n")
    fp = open("myrpcs/chassis_inv.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = ChassisInv(dev).get()
    
    chinv = PrettyTable (['Name','Description','Serial Number'])
    chinv.padding_width=1
    
    for y in ct.keys():
        chinv.add_row([ct[y]['name'], ct[y]['description'],ct[y]['sn']])
    fo.write(str(chinv))
    
    ##### CREATE CHASSIS CSV FOR EXCEL
    fp = open("myrpcs/chassis_inv.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = ChassisInv(dev).get()
    
    fcsv = open ("chassis_example.csv",'w')
    fcsv.write("Name,Description,Serial Number\n")    
    for y in ct.keys():
        fcsv.write(str(ct[y]['name'])+","+str(ct[y]['description'])+","+str(ct[y]['sn'])+"\n")
    fcsv.close()
    
    ##### PRINT OSPF NEIGHBOR INFORMATION
    fo.write("\n")
    fo.write("----- OSPF NEIGHBORS -----\n")
    fo.write("\n")
    
    fp = open("myrpcs/ospf_neigh.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = OspfIface(dev).get()
    
    chinv = PrettyTable (['Address','Interface','State'])
    chinv.padding_width=1
    
    for y in ct.keys():
        chinv.add_row([ct[y]['addr'], ct[y]['iface'],ct[y]['state']])
    fo.write(str(chinv))
    
    ##### PRINT INTERFACE TERSE INFORMATION
    fo.write("\n")
    fo.write("----- INTERFACE INVENTORY -----\n")
    fo.write("\n")
    fp = open("myrpcs/iface_terse.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = IfaceTerse(dev).get()
    
    chinv = PrettyTable (['Name','Admin Status','Op Status','Family','Bundle','IP Address'])
    chinv.padding_width=1
        
    for y in ct.keys():
        chinv.add_row([ct[y]['name'], ct[y]['as'],ct[y]['os'],ct[y]['family'],ct[y]['bundle'],ct[y]['add']])
    fo.write(str(chinv))
    
    ##### PRINT UPTIME SYSTEM INFORMATION
    fo.write("\n")
    fo.write("----- SYSTEM UPTIME -----\n")
    fo.write("\n")
    tt = PrettyTable (['What','When'])
    resp = dev.rpc.get_system_uptime_information()
    tt.add_row(["Current time: " , resp.findtext('.//current-time/date-time')])
    tt.add_row(["Device booted from: " , resp.findtext('.//system-booted-time/time-length')])
    tt.add_row(["Last configuration: " , resp.findtext('.//last-configured-time/date-time')])
    fo.write(str(tt))
    
    ##### PRINT ROUTING ENGINE INFORMATION
    fo.write("\n")
    fo.write("----- ROUTING ENGINE -----\n")
    fo.write("\n")
    fp = open("myrpcs/re.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = RoutingEngine(dev).get()
    
    chinv = PrettyTable (['Slot','Role','Status','Model','Serial Number','Memory %'])
    chinv.padding_width=1
        
    for y in ct.keys():
        chinv.add_row([ct[y]['slot'], ct[y]['role'],ct[y]['status'],ct[y]['model'],ct[y]['sn'],ct[y]['mem']])
    fo.write(str(chinv))
    
    ##### PRINT ROUTE INSTANCES SUMMARY
    fo.write("\n")
    fo.write("----- ROUTE INSTANCE SUMMARY -----\n")
    fo.write("\n")
    fp = open("myrpcs/route_instance.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = RouteInstance(dev).get()
    
    chinv = PrettyTable (['Instance','RIB','Active','HoldDown','Hidden'])
    chinv.padding_width=1
        
    for y in ct.keys():
        fp = open("myrpcs/rib_instance.yaml", 'r')
        yml = fp.read()
        fp.close()
        yml=yml.replace("xxxxx",y)
        globals().update(FactoryLoader().load(yaml.load(yml)))
        rt = RibInstance(dev).get()
        for z in rt.keys():
            chinv.add_row([y, rt[z]['name'],rt[z]['act'],rt[z]['hold'],rt[z]['hid']])
    fo.write(str(chinv))
    
    ##### PRINT VLANS ACTIVE ON INTERFACES
    fo.write("\n")
    fo.write("----- CONFIGURED VLANS -----\n")
    fo.write("\n")
    fp = open("myrpcs/vlans.yaml", 'r')
    yml = fp.read()
    fp.close()
        
    globals().update(FactoryLoader().load(yaml.load(yml)))
    ct = IfaceVlan(dev).get()
    
    chinv = PrettyTable (['Interface','Vlan'])
    chinv.padding_width=1
    
    for y in ct.keys():
        if ct[y]['vlan']!=None:
            for c in ct[y]['vlan']:
                chinv.add_row([ct[y]['name'], c.split(".")[1][:-2]])
    fo.write(str(chinv))
    
    dev.close()
    print "DONE! "+x[0]+"@"+x[1]+"\n"
    return 1


if __name__ == '__main__':
    '''Allow user to Define Username and Password'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fname", action="store", type=str, default='hosts',help="hosts file")
    
    args =  parser.parse_args()
    
    hosts=[]
    fhn = args.fname + ".txt"
    fh = fp = open(fhn, 'r')  
    line = fp.readline()
    while line:
        h = line.split(" ")
        tmpl=[h[0],h[1]]
        hosts.append(tmpl)
        line = fp.readline()
    fp.close()
    
    print str(datetime.datetime.now())
    print "Starting collecting infos...\n"
    
    p = Pool(10)
    p.map(f, hosts)
    
    print str(datetime.datetime.now())
    



