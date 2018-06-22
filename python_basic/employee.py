#! /usr/bin/python

class employee:

    def __init__(self, n, a, s):
        self.n=n
        self.a=a
        self.s=s

    def get(self):
        print "Name: " + str(self.n) + ", age: " + str(self.a) + ", salary: " + str(self.s) + "$."

    def money(self, r):
        self.s+=r

    def birthday(self):
        self.a+=1
