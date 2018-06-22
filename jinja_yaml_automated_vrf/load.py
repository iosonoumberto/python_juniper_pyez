
#! /usr/bin/python

#Import Required Modules
from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.utils.config import Config
import sys
import yaml

a_device=Device (host='10.92.35.2', user="root", password="Embe1mpls")
a_device.open()

cfg = Config(a_device)

yfile = "vpn.yaml"
s=open(yfile).read()
myvars=yaml.load(s)

jfile = "vpn.j2"
cfg.load(template_path=str(jfile), template_vars=myvars, format='set')

cfg.pdiff()
cfg.commit()

