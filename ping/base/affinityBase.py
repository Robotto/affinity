#!/usr/bin/python

from IPy import IP
import socket
from time import time, ctime
import struct
import json

incomingPort = 5005

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",incomingPort)
UDPSock.bind(listen_addr)

DISTANCEFORMAT = 'cI' #Char, unsigned Int
DRAWFORMAT     = 'cII'
RELEASEFORMAT  = 'cc'
DRAW_EVENT_SIZE = struct.calcsize(DRAWFORMAT)
DISTANCE_EVENT_SIZE = struct.calcsize(DISTANCEFORMAT)


#ideal data format for a post-it note:
# A - Distance in mm from sensor A
# B - Distance in mm from sensor B
# C - Distance in mm from sensor C
# D - Distance in mm from sensor D
# X - Collection of x,y coordinates that constitute a payload for picture data

distances={} #dict
Xpoints=[] #set
Ypoints=[] #set


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
       if isinstance(obj, set):
          return list(obj)
       return json.JSONEncoder.default(self, obj)

def postIt(distances, payload,timeStamp): #called when a post-it has 4 distance points and a collection of point data

    pos = json.dumps({'pos':distances}) #<-works


    img = json.dumps({'img':payload}, cls=SetEncoder)

    dt = json.dumps({'time':timeStamp})

    package = '{\"postIt\":{' + dt + ',' + pos + img + '}}' #quick and dirty, because i couldn't be bothered with jsonmerge

    #print 'pos:' + pos
    #print 'img:' + img
    #print 'time:' + dt

    print 'package: '
    print package

while True:

    # Report on all data packets received and
    # where they came from in each case (as this is UDP, each may be from a different source and it's up to the server to sort this out!)

    # recvfrom waits for incoming data:
    data, addr = UDPSock.recvfrom(5005) #Data is prefixed with type:  A,B,C and D are distance measurements, X is touch panel data


    remoteIP = IP(addr[0]).strNormal()  # convert address of packet origin to string

    print (str(ctime()) + ': RX: \"' + str(data.rstrip('\n')) + '\" from ' + str(remoteIP)) + "size: " + str(len(data)) + " bytes total"

    print
    print ' RX: "%s" @ %s from %s' % (data.rstrip('\n'), ctime(), remoteIP)
    print

    # poorly constructed data validation.. bear with me...

    if (data[0]=='X' or data[0]=='Y') and len(data)==DRAW_EVENT_SIZE:
        print 'Got Point Data'
        (id, x,y) = struct.unpack(DRAWFORMAT, data)

#        print id
#        print x
#        print y

        #Store in a collection that matches the ID.
        #quick and dirty duplicate code.. sue me.
        if id=='X':
            Xpoints.append({x,y})
            #print Xpoints

        if id=='Y':
            Ypoints.append({x, y})

    if (data[0]=='A' or data[0]=='B' or data[0]=='C' or data[0]=='D') and len(data)==DISTANCE_EVENT_SIZE:
        print 'Got Distance Data'
        (id,distance) = struct.unpack(DISTANCEFORMAT, data)

    #        print id
    #        print distance

        distance_data_RX_time = int(time())  # Start a timer

        distances[id]=distance

        print 'Distances:' + str(distances)

        if len(distances)==4:
            postIt(distances,Xpoints,distance_data_RX_time)

    #if $SOMETIME has passed while not receiving 4 distance measurements, cut it short and release it as an incomplete set.






