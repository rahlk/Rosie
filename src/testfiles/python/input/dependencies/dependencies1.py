#The MIT License (MIT)
#
#Copyright (c) 2017 Jordan Connor
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pandas
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from project import lattice
from collections import Counter,defaultdict
from multiprocessing import Process, Pipe
from datetime import datetime
from math import *


QUIT = "QUIT"

class sim_helper(object):

    def __init__(self,L,fN,u):
        self.L = L
        self.u = u
        # Set our initial state
        self.E1 = None
        while self.E1 is None or (self.E1 < self.u[0] or self.E1 >= self.u[1]):
            self.lat = lattice.isinglattice(L)
            self.E1 = self.lat.E()

        #Set the initial f paramater
        self.f = np.e
        #Define our histogram counter
        self.H = Counter()
        #Define our density of states and initialize to our guess
        self.g0 = np.log(1)
        #Define our modification paramater
        self.fN = fN

        self.G = {self.E1 : self.g0}

    def sweep(self):
        for i in range(self.L**2):
            #Do the trial flip and calculate the new energy
            E2 = None
            x = None
            y = None

            x,y = np.random.randint(0,self.L,2)
            #self.lat.flip(x,y)
            #E2 = self.lat.E()
            E2 = self.E1 + self.lat.dU(x, y)

            if not (E2 < self.u[0] or E2 >= self.u[1]):
                #self.lat.flip(x, y)

            #else:
                #Accept the energy if it meets the wang landau criterion
                #or reverse the flip
                if E2 not in self.G.keys():
                    self.G[E2] = self.g0
                if(np.random.uniform() <= np.exp(float(self.G[self.E1])-self.G[E2])):
                    self.E1 = E2
                    self.lat.flip(x, y)
                #else:
                    #self.lat.flip(x,y)

            #update our DOS for the current energy
            self.G[self.E1] += np.log(self.f)
            #Add our new energy to the histogram
            self.H[self.E1] += 1

    def clear(self,f):
        self.f = f
        self.H.clear()

def sim_process(conn):
    L,fN,u = conn.recv()
    helper = sim_helper(L,fN,u)
    while(conn.recv() != "EOF"):
        for i in range(10000):
            helper.sweep()
        conn.send(helper.G)
        conn.send(helper.H)
        newF = conn.recv()
        if(newF != helper.f):
            helper.clear(newF)
    conn.close()

class wanglandauising(object):

    def __init__(self,L,p,fN):
        self.L = L
        self.p = p
        #Define our normalized DOS
        self.GN = {}
        #Define an nonnormalized DOS
        self.G = {}
        #Define our modification factors
        self.f = np.e
        self.fN = fN
        self.H = Counter()
        self.pCount = 2
        self.processes = []
        self.conns = []
        A = 2*L**2+.06
        #self.ranges = [[-A,-A/2.0],[-A/2.0,0],[0,A/2.0],[A/2.0,A]]
        #print(self.ranges)
        self.ranges = [[-100,0],[0,100]]
        #self.ranges=[[-1000,1000]]

    def run(self):
        for i in range(self.pCount):
            parent_conn, child_conn = Pipe()
            self.processes.append(Process(target=sim_process, args=(child_conn,)))
            self.conns.append(parent_conn)
            self.processes[i].start()
            self.conns[i].send([self.L,self.fN,self.ranges[i]])


        while not self.f < np.exp(10**-8):
            for i in range(self.pCount):
                self.conns[i].send("GO")

            for conn in self.conns:
                for e,g in conn.recv().iteritems():
                    self.G[e] = g
                self.H += conn.recv()

            self.check_flatness()

        for i in range(self.pCount):
            self.conns[i].send("EOF")
            self.conns[i].close()
            self.processes[i].join()

        #Normalize our DOS
        for e,g in self.G.iteritems():
            self.GN[e] = g - self.G[-2] + np.log(2)
        #print(self.GN)

    def check_flatness(self,a=":)"):
        #Determine the average histogram
        avgH = 0.0
        size = 0.0
        for e,count in self.H.iteritems():
            avgH += count
            size += 1.0
        avgH = avgH/size
        #Now finish our average and determine our percetnage
        avgH = avgH*self.p

        #Now verify the wanglandau criterion is satisfied
        cSat = True
        for e,count in self.H.iteritems():
            if count <= avgH:
                print(str(count) + " " + str(avgH))
                cSat = False
                break

        #If satisfied we reduce our modification factor
        if cSat:
            self.f = self.f**(1/float(self.fN))
            self.H.clear()
        for conn in self.conns:
            conn.send(self.f)
        print(self.f)


    def u(self,T):
        num = 0.0
        den = 0.0
        for e,g in self.G.iteritems():
            num += (e*g*np.exp(-float(e)/T))
            den += (g*np.exp(-float(e)/T))
        return (num/den)/self.L

if __name__ == '__main__':
    #Run the simulation
    L = 4
    sim = wanglandauising(L,.8,2)
    t1 = datetime.now()
    sim.run()
    t2 = datetime.now()
    delta = t2-t1
    print(delta.microseconds)
    #Now use the DOS to generate our energies for various values of t
    U = []
    G = []
    for e,g in sim.GN.iteritems():
        U.append(e)
        G.append(g)

    s1 = figure(width=500, plot_height=500,title="DOS for" + str(L) +" x "+str(L)+ "Ising Model")
    s1.circle(U,G,size=5,color="navy",alpha=.5)
    s1.xaxis.axis_label = "Energy per Lattice Site"
    s1.yaxis.axis_label = "ln(g(e))"
    show(s1)
