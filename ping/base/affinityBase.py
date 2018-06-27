#!/usr/bin/python

from IPy import IP
import socket
from time import time, ctime, sleep

from BroadcasterWebsocketServer import BroadcasterWebsocketServer


import struct
import json
import threading, Queue



wsport = 5000
incomingPort = 5005
distanceTimeout=2

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",incomingPort)
UDPSock.bind(listen_addr)

DISTANCEFORMAT = 'cH' #Char, unsigned short - TODO: looks to be expecting 8 bytes...  Is this Arduino compatible?
DRAWFORMAT     = 'cII'
DRAW_EVENT_SIZE = struct.calcsize(DRAWFORMAT)
DISTANCE_EVENT_SIZE = struct.calcsize(DISTANCEFORMAT)

print 'distance_event_size:' + str(DISTANCE_EVENT_SIZE)
print 'draw_event_size:' + str(DRAW_EVENT_SIZE)


#ideal data format for a post-it note:
# A - Distance in mm from sensor A
# B - Distance in mm from sensor B
# C - Distance in mm from sensor C
# D - Distance in mm from sensor D
# X - Collection of x,y coordinates that constitute a payload for picture data





def postIt(distances, payload,timeStamp,postitQ): #called when a post-it has 4 distance points and a collection of point data

    #pos = json.dumps({'pos':distances}) #<-works


    #img = json.dumps({'img':payload}, cls=SetEncoder)
    points = "{"
    i=0
    while i < len(payload):
        set=iter(payload[i])
        #points += "\"" + str(i) + "\": " + "{\"X\": "+ str(next(set)) + ", \"Y\": " + str(next(set)) + "}" #quick and dirty formatting...
        points += "[" + str(next(set)) + "," + str(next(set)) + "]  " #quick and dirty formatting...
        if(i<len(payload)-1) : points +=","
        i += 1
    points +="}"

    dt = json.dumps({'time':timeStamp})

    package = '{' + "\"time\": " + str(timeStamp) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "," + "\"img\": " + points + "}" #quick and dirty, because i couldn't be bothered with jsonmerge

    #print 'pos:' + pos
    #print 'img:' + img
    #print 'time:' + dt

    print 'Packaged post-it. Sending to queue'
    #print package
    postitQ.put(package)
    # TODO: Serve the data through a websocket to whomever is listening...


def udpThread(dataQ):
    print 'udp thread started.'

    while True:

        # Report on all data packets received and
        # where they came from in each case (as this is UDP, each may be from a different source and it's up to the server to sort this out!)

        # recvfrom waits for incoming data:
        data, addr = UDPSock.recvfrom(incomingPort) #Data is prefixed with type:  A,B,C and D are distance measurements, X is touch panel data


        remoteIP = IP(addr[0]).strNormal()  # convert address of packet origin to string

        print ' RX: "%s" @ %s from %s' % (data.rstrip('\n'), ctime(), remoteIP)

        dataQ.put(data) #push data to other thread (via queue)

def dataHandlingThread(dataQ,postitQ):
    distances = {}  # dict
    Xpoints = []  # set
    Ypoints = []  # set
    Zpoints = []  # set
    Qpoints = []  # set

    Xtriggered = False
    Ytriggered = False
    Ztriggered = False
    Qtriggered = False

    distance_data_RX_time = 0

    print 'data handling thread started.'


    while True:

        data=[0,0]

        try:
            data = dataQ.get(False)  # get data from other thread (via queue)
        except Queue.Empty:
            pass


        # poorly constructed data validation.. bear with me...
        if(data[0]=='!'):
            print 'got trigger data'

            if data[1] == 'X':
                Xtriggered=True
            if data[1] == 'Y':
                Ytriggered=True
            if data[1] == 'Z':
                Ztriggered=True
            if data[1] == 'Q':
                Qtriggered=True

        if (data[0]=='X' or data[0]=='Y' or data[0]=='Z' or data[0]=='Q') and len(data)==DRAW_EVENT_SIZE:
            (id, x,y) = struct.unpack(DRAWFORMAT, data)
            print 'Got Point Data: x:' + str(x) + ' y:' + str(y)

    #        print id
    #        print x
    #        print y

            #Store in a collection that matches the ID.
            #quick and dirty duplicate code.. sue me.
            if id=='X':
                Xpoints.append({x,y})
                #print Xpoints
            if id=='Y':
                Ypoints.append({x,y})
            if id=='Z':
                Zpoints.append({x,y})
            if id=='Q':
                Qpoints.append({x,y})

        if (data[0]=='A' or data[0]=='B' or data[0]=='C' or data[0]=='D') and len(data)==DISTANCE_EVENT_SIZE:
            print 'Got Distance Data'

    #        print format(ord(data[0]), 'b')
    #        print format(ord(data[1]), 'b')
    #        print format(ord(data[2]), 'b')
    #        print format(ord(data[3]), 'b')


            id=data[0]

            distance=ord(data[1])<<8 | ord(data[2]) #manual unpack, since debugging the python unpack took too long.

            #(id,distance) = struct.unpack(DISTANCEFORMAT, data)

        #        print id
        #        print distance

            distance_data_RX_time = int(time())  # Start a timer

            #print(distance_data_RX_time)

            distances[id]=distance

            print 'Distances:' + str(distances)

            #if nothing is triggered ignore distance:
            #TODO: this is where one would implement functionality of moving already placed post-its.
            if not (Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True):
                print "no post-its are triggered, ignoring distance data."
                distances = {}  # clear the distances dict


    # if $SOMETIME has passed while not receiving 4 distance measurements, cut it short and release it as an incomplete set.
                # TODO: The timeout does not fire!
        if (Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True) and len(distances)==4 or (len(distances)>0 and (int(time())>distance_data_RX_time+distanceTimeout)):

            # Clear the relevant points set:
            if Xtriggered == True:
                postIt(distances, Xpoints, distance_data_RX_time,postitQ)
                Xpoints = []
                Xtriggered = False

            if Ytriggered == True:
                postIt(distances, Ypoints, distance_data_RX_time,postitQ)
                Ypoints = []
                Ytriggered = False

            if Ztriggered == True:
                postIt(distances, Zpoints, distance_data_RX_time,postitQ)
                Zpoints = []
                Ztriggered = False

            if Qtriggered == True:
                postIt(distances, Qpoints, distance_data_RX_time,postitQ)
                Qpoints = []
                Qtriggered = False

            distances = {}  # clear the distances dict





def websocketThread(postitQ):


    print 'websocket thread started.'
    server = BroadcasterWebsocketServer('', wsport, True)
    server.start()

    print 'websocket server started'

    while True:

        try:
            postit = postitQ.get(False)  # get data from other thread (via queue) - non blocking
            print "got postit data:" + postit
            server.broadcast(postit)
        except Queue.Empty:
            pass


dataQ = Queue.Queue()
postitQ = Queue.Queue()

thread1 = threading.Thread(target=udpThread,args=(dataQ,))
thread2 = threading.Thread(target=dataHandlingThread,args=(dataQ,postitQ,))
thread3 = threading.Thread(target=websocketThread,args=(postitQ,))

#make threads killable with ctrl+c:
thread1.daemon=True
thread2.daemon=True
thread3.daemon=True

thread1.start()
thread2.start()
thread3.start()

while True:
    sleep(1)




