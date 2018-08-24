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
distanceTimeout=1

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",incomingPort)
UDPSock.bind(listen_addr)

DISTANCEFORMAT = 'cf' #Char, unsigned short - TODO: looks to be expecting 8 bytes...  Is this Arduino compatible?
DRAWFORMAT     = 'cff'
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





def postIt(distances, payload,timeStamp,outgoingQ): #called when a post-it has 4 distance points and a collection of point data

    #pos = json.dumps({'pos':distances}) #<-works


    #img = json.dumps({'img':payload}, cls=SetEncoder)
    points = "["
    i=0
    while i < len(payload):

        set = payload[i]
#        points += "[" + str(set[0]) + "," + str(set[1]) + "]  " #quick and dirty formatting...
        points += "[ %.3f , %.3f ]" % (set[0],set[1]) #quick and dirty formatting...

        if(i<len(payload)-1) : points +=","

        i += 1

    points +="]"

    dt = json.dumps({'time':timeStamp})

    package = '{'+ '\"cmd\":\"operate\",' + '\"data\":' + '{' + "\"time\": " + str(timeStamp) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "," + "\"img\": " + points + "}}" #quick and dirty, because i couldn't be bothered with jsonmerge

    #print 'pos:' + pos
    #print 'img:' + img
    #print 'time:' + dt

    print 'Packaged post-it. Sending to queue'
    #print package
    outgoingQ.put(package)


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

def dataHandlingThread(dataQ,outgoingQ,commandQ):
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

    calibrationMode = False

    print 'data handling thread started.'


    while True:

        data=[0,0]

        try:
            data = dataQ.get(False)  # get data from other thread (via queue)
            #print data[0]
        except Queue.Empty:
            pass

        try:
            calibrationMode = commandQ.get(False)  # get data from other thread (via queue)
            if calibrationMode==True:
                print 'Switched to calibration mode'
            if calibrationMode==False:
                print 'Switched to operation mode'
        except Queue.Empty:
            pass


        # poorly constructed data validation.. bear with me...
        if(data[0]=='!'):
            print 'got trigger data for: ' + str(data[1])

            if data[1] == 'X':
                Xtriggered=True

            if data[1] == 'Y':
                Ytriggered=True

            if data[1] == 'Z':
                Ztriggered=True

            if data[1] == 'Q':
                Qtriggered=True



            if Xtriggered == True and len(Xpoints) == 0:
                print 'ignoring trigger for X, since it has no image data'
                Xtriggered = False

            if Ytriggered == True and len(Ypoints) == 0:
                print 'ignoring trigger for Y, since it has no image data'
                Ytriggered = False

            if Ztriggered == True and len(Zpoints) == 0:
                print 'ignoring trigger for Z, since it has no image data'
                Ztriggered = False

            if Qtriggered == True and len(Qpoints) == 0:
                print 'ignoring trigger for Q, since it has no image data'
                Qtriggered = False

        if (data[0]=='X' or data[0]=='Y' or data[0]=='Z' or data[0]=='Q') and len(data)==DRAW_EVENT_SIZE:
            (id, x,y) = struct.unpack(DRAWFORMAT, data)
            print 'Got Point Data: x:' + str(x) + ' y:' + str(y)

    #        print id
    #        print x
    #        print y

            #Store in a collection that matches the ID.
            #quick and dirty duplicate code.. sue me.
            if id=='X':
                Xpoints.append([x,y])
            #    print Xpoints
            if id=='Y':
                Ypoints.append([x,y])
            if id=='Z':
                Zpoints.append([x,y])
            if id=='Q':
                Qpoints.append([x,y])

        if (data[0]=='E'): #and len(data)==DISTANCE_EVENT_SIZE:
            print 'Got Position Data'


            id=data[0]

            if calibrationMode==False:
                rx=data.rstrip('\n')
                print rx.split(',')[1]
                print rx.split(',')[2]
                distances['y']=rx.split(',')[2]
                distances['x']=rx.split(',')[1]

            if len(distances)>1:
                distance_data_RX_time = int(time())  # Start a timer


            print 'Distances:' + str(distances)


            #if nothing is triggered ignore distance:
            #TODO: this is where one would implement functionality of moving already placed post-its.
#            if not (calibrationMode==True or Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True):
            if not (Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True):
                print "no post-its are triggered, and not in calibration mode, ignoring distance data."
                distances = {}  # clear the distances dict


    # if $SOMETIME has passed while not receiving 4 distance measurements, cut it short and release it as an incomplete set.
        if calibrationMode==False and ((Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True) and len(distances)==2):

            # Clear the relevant points set:
            if Xtriggered == True:
                postIt(distances, Xpoints, distance_data_RX_time,outgoingQ)
                Xpoints = []
                Xtriggered = False

            if Ytriggered == True:
                postIt(distances, Ypoints, distance_data_RX_time,outgoingQ)
                Ypoints = []
                Ytriggered = False

            if Ztriggered == True:
                postIt(distances, Zpoints, distance_data_RX_time,outgoingQ)
                Zpoints = []
                Ztriggered = False

            if Qtriggered == True:
                postIt(distances, Qpoints, distance_data_RX_time,outgoingQ)
                Qpoints = []
                Qtriggered = False

            distances = {}  # clear the distances dict




def websocketThread(outgoingQ,incomingQ,commandQ):


    print 'websocket thread started.'
    server = BroadcasterWebsocketServer('', wsport, incomingQ, True)
    server.start()
    incomingQ=server.getQ()

    print 'websocket server started'

    while True:

        try:
            postit = outgoingQ.get(False)  # get data from other thread (via queue) - non blocking
            print "Broadcasting data: " + postit
            server.broadcast(postit)
        except Queue.Empty:
            pass

        try:
            incoming = incomingQ.get(False)  # get data from other thread (via queue) - non blocking
            print "got websocket data: " + incoming

            try:
                command = json.loads(incoming)['cmd'].lower() #lowercase...
                if command=='operate':
                    #OPERATE
                    calibrationMode=False
                    commandQ.put(calibrationMode)
                if command=='calibrate':
                    #CALIBRATE
                    calibrationMode=True
                    commandQ.put(calibrationMode)
            except:
                print 'invalid json recieved. did you issue a cmd?'
        except Queue.Empty:
            pass


dataQ = Queue.Queue() #for storing recieved data via UDP
outgoingQ = Queue.Queue() #for moving postit data
incomingQ = Queue.Queue() #for storing rx websocket data
commandQ = Queue.Queue() #for communicating states between threads

thread1 = threading.Thread(target=udpThread,args=(dataQ,))
thread2 = threading.Thread(target=dataHandlingThread,args=(dataQ,outgoingQ,commandQ,))
thread3 = threading.Thread(target=websocketThread,args=(outgoingQ,incomingQ,commandQ,))

#make threads killable with ctrl+c:
thread1.daemon=True
thread2.daemon=True
thread3.daemon=True

thread1.start()
thread2.start()
thread3.start()

while True:
    sleep(1)




