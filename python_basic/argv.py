#! /usr/bin/python

import sys

i=0

for x in sys.argv:
    print "Argument " + str(i) + " : " + str(x)
    i+=1 
