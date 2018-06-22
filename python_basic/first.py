#! /usr/bin/python

import sys

def square(x):
    return int(x)**2

def cube(x):
    return int(x)**3

def main():
    n=sys.argv[1]
    s=square(n)
    c=cube(n)
    print s
    print c

if __name__ == "__main__":
    main()
