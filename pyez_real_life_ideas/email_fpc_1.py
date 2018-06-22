#! /usr/bin/python

'''Import Required Modules'''
from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.utils.config import Config
from jnpr.junos.op.fpc import FpcHwTable
from jnpr.junos.op.fpc import FpcInfoTable

import time
import argparse
import re
import sys
import yaml

from getpass import getpass
from pprint import pprint as pp
from lxml import etree

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

'''Allow user to Define Username and Password'''
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fname", action="store", type=str, default='hosts',help="hosts file")
parser.add_argument("-d", "--det", action="store", type=str, default='a',help="detail level")
parser.add_argument("-c", "--cpu", action="store", type=str, default=85,help="cpu threshold")
parser.add_argument("-m", "--mem", action="store", type=str, default=85,help="memory threshold")


args =  parser.parse_args()

hosts={}
fhn = args.fname + ".txt"
fh = fp = open(fhn, 'r')  
line = fp.readline()
while line:
    h = line.split(" ")
    hosts[h[0]]=h[1]
    line = fp.readline()

thrcpu=int(args.cpu)
thrmem=int(args.mem)

ifpcs={}
sfpcs={}

print "Using the following thresholds:"
print "\tcpu: " + str(thrcpu) + "%"
print "\tmemory: " + str(thrmem) + "%"
print ""

print "Starting collecting infos...\n"
for x in hosts.keys():
    '''Connect to device'''
    dev = Device(host=hosts[x], user="root", password="Embe1mpls")
    dev.open()
    fpcs = FpcHwTable(dev)
    fpcs.get()
    
    ifpcs[x]={}
    for y in fpcs.keys():
        ifpcs[x][y]={}
        ifpcs[x][y]['type']=fpcs[y]['desc']
    
    jfpcs = FpcInfoTable(dev)
    jfpcs.get()
    
    sfpcs[x]={'online':0, 'empty':0, 'offline':[], 'highcpu':{}, 'highmem':{}, 'details':{}}
    for y in jfpcs.keys():
        if jfpcs[y]['state'] == 'Online':
            sfpcs[x]['online']+=1
            if int(jfpcs[y]['cpu']) > thrcpu:
                sfpcs[x]['highcpu'][y]=int(jfpcs[y]['cpu'])
            if int(jfpcs[y]['memory']) > thrmem:
                sfpcs[x]['highmem'][y]=int(jfpcs[y]['memory'])
            if args.det == "g":
                sfpcs[x]['details'][y]=jfpcs[y]
        if jfpcs[y]['state'] == 'Empty':
            sfpcs[x]['empty']+=1
        if jfpcs[y]['state'] == 'Offline':
            sfpcs[x]['offline'].append(y)
    dev.close()

body =  "Devices relevant information\n"
for x in sfpcs.keys():
    if len(sfpcs[x]['offline']) + len(sfpcs[x]['highcpu'].keys()) + len(sfpcs[x]['highmem'].keys()) > 0:
        fl=0
        body += str(x)+"\n"
        if len(sfpcs[x]['offline']) > 0:
            body += "\tDevice has " + str(len(sfpcs[x]['offline'])) + " fpc in offline state. They are in slots " + str(sfpcs[x]['offline']) + ".\n"
            fl=1
        if len(sfpcs[x]['highcpu'].keys()) > 0:
            hc = "\tFPCS with high cpu values: " + str(len(sfpcs[x]['highcpu'])) + "\n"
            for y in sfpcs[x]['highcpu'].keys():
                hc += "\t\tslot " + str(y) + " : " + str(sfpcs[x]['highcpu'][y]) + "% \n"
            body += str(hc[:-1]) + "\n"
            body += "Perform this action...\n"
            fl=1
        if len(sfpcs[x]['highmem'].keys()) > 0:
            hm = "\tFPCs with high memory values: " + str(len(sfpcs[x]['highmem'])) + "\n"
            for y in sfpcs[x]['highmem'].keys():
                hm += "\t\tslot " + str(y) + " : " + str(sfpcs[x]['highmem'][y]) + "% \n"
            body +=  str(hm[:-1]) + "\n"
            body += "Perform this action...\n"
            fl=1
        if fl == 0:
            body +=  "All ok here!\n"
        body +=  "----------\n"
    
fromaddr = "pyez_juniper_italy@yahoo.com"
toaddr = "umberto.manferdini@gmail.com"


msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "FPC WARNINGS!"
 
msg.attach(MIMEText(body, 'plain'))
print "step0" 
server = smtplib.SMTP('smtp.mail.yahoo.it', 25)
print "step1"
#server.starttls()
print "step2"
server.login(fromaddr, "python123!")
print "step3"
text = msg.as_string()
print "step4"
server.sendmail(fromaddr, toaddr, text)
print "step5"
server.quit()
print "step6"

print body
