import os, sys
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.exception import ConnectError

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fname", action="store", type=str, default='hosts',help="hosts file")
parser.add_argument("-v", "--ver", action="store", type=str, default='unset',help="detail level")
parser.add_argument("-p", "--package", action="store", type=str, default='unset',help="detail level")

args =  parser.parse_args()

if args.ver=="unset":
    print "Please provide a target version (e.g. 17.1 or 14.2R7) with the -v flag when launching the script."
    print "Exiting..."
    sys.exit()

if args.pkg=="unset":
    print "Please provide a path to find the upgrade package using the -p flag."
    print "Exiting..."
    sys.exit()

remote_path = '/var/tmp'
validate = True

hosts={}
fhn = args.fname + ".txt"
fh = fp = open(fhn, 'r')  
line = fp.readline()
while line:
    h = line.split(" ")
    hosts[h[0]]=h[1]
    line = fp.readline()

if not (os.path.isfile(package)):
    msg = 'Software package does not exist: {0}. '.format(package)
    sys.exit()

for x in hosts.keys():

    dev = Device(host=hosts[x], user="root", password="Embe1mpls")
    dev.open()
    
    if dev.facts['version']!=args.ver:
        
        sw = SW(dev)
        try:
            ok = sw.install(package=package, remote_path=remote_path, progress=True, validate=validate)
        except Exception as err:
            msg = 'Unable to install software, {0}'.format(err)
            ok = False
        
        if ok is True:
            sw.reboot()
        else:
            print 'Unable to install software.'
    else:
        print "Device already has the target version, No need for upgrade!"
        
    dev.close()