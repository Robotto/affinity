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

#TESTDATA: send 'Fn' where n is 0-2 to the UDP port (5005) to simulate sensor data for a post it placement:
        if data[0]=='S':
            print 'creating simulated postit data'
            distance_data_RX_time = int(time())  # Start a timer

            if data[1]=='0': #X=60, Y=100
                distances['A']= 558.7933428379404
                distances['B']= 456.2071897723662
                distances['C']= 370.3039292257105
                distances['D']= 491.1720676097125
            if data[1] == '1': #X=200, Y=75
                distances['A'] = 653.1653695657785
                distances['B'] = 593.5065290289564
                distances['C'] = 287.14108030722457
                distances['D'] = 396.01136347332255
            if data[1] == '2': #X=0, Y=0
                distances['A'] = 447.49301670528894
                distances['B'] = 463.81569615527235
                distances['C'] = 478.87889909662965
                distances['D'] = 463.0874647407334
            print distances

#TESTDATA: send '?n' where n is 0-4 to the UDP port (5005) to simulate calibration sensor data:
#        if data[0]=='?':
#            distance_data_RX_time = int(time())  # Start a timer
#            if data[1]=='0': #Top left
#                distances['A'] = 958.4247492630811
#                distances['B'] = 788.4624277668531
#                distances['C'] = 90.7358804442873
#                distances['D'] = 552.3929760596164

#            if data[1] == '1': #Top right
#                distances['A'] = 1021.7524161948431
#                distances['B'] = 864.333847538091
#                distances['C'] = 160.3527361787132
#                distances['D'] = 567.9947182853024

#            if data[1] == '2': #Bottom left
#                distances['A'] = 1003.7419987227794
#                distances['B'] = 787.497936505233
#                distances['C'] = 81.93289937503738
#                distances['D'] = 627.7403922004701

#            if data[1] == '3': #Bottom right
#                distances['A'] = 1064.3768129755551
#                distances['B'] = 863.4541099560532
#                distances['C'] = 155.54099138169335
#                distances['D'] = 641.5122757983669

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

        if (data[0]=='A' or data[0]=='B' or data[0]=='C' or data[0]=='D'): #and len(data)==DISTANCE_EVENT_SIZE:
            print 'Got Distance Data'


            id=data[0]

            if calibrationMode==False:
                distance=ord(data[1])<<8 | ord(data[2]) #manual unpack, since debugging the python unpack took too long.

            #if calibrationMode==True: #Proper unpack, since the data comes from a script...
            #    (id,distance) = struct.unpack(DISTANCEFORMAT, data)


            if len(distances)>2:
                distance_data_RX_time = int(time())  # Start a timer


            distances[id]=distance

            print 'Distances:' + str(distances)


            #if nothing is triggered ignore distance:
            #TODO: this is where one would implement functionality of moving already placed post-its.
#            if not (calibrationMode==True or Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True):
            if not (Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True):
                print "no post-its are triggered, and not in calibration mode, ignoring distance data."
                distances = {}  # clear the distances dict


    # if $SOMETIME has passed while not receiving 4 distance measurements, cut it short and release it as an incomplete set.
        if calibrationMode==False and ((Xtriggered==True or Ytriggered==True or Ztriggered==True or Qtriggered==True) and len(distances)==4 or (len(distances)>2 and (int(time())>distance_data_RX_time+distanceTimeout))):

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

        #if calibrationMode==True and (len(distances)>0 and (int(time())>distance_data_RX_time+distanceTimeout)):
        if calibrationMode==True and data[0]=='?':

            #package ='{'+ '\"cmd\":\"calibrate\",' + '\"data\":' '{' + "\"time\": " + str(distance_data_RX_time) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "}}"
            distance_data_RX_time = int(time())
            distances['A'] = 958.4247492630811
            distances['B'] = 788.4624277668531
            distances['C'] = 90.7358804442873
            distances['D'] = 552.3929760596164
            package ='{'+ '\"cmd\":\"calibrate\",' + '\"data\":' '{' + "\"time\": " + str(distance_data_RX_time) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "}}"
            outgoingQ.put(package)

            distance_data_RX_time = int(time())
            distances['A'] = 1021.7524161948431
            distances['B'] = 864.333847538091
            distances['C'] = 160.3527361787132
            distances['D'] = 567.9947182853024
            package ='{'+ '\"cmd\":\"calibrate\",' + '\"data\":' '{' + "\"time\": " + str(distance_data_RX_time) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "}}"
            outgoingQ.put(package)

            distance_data_RX_time = int(time())
            distances['A'] = 1003.7419987227794
            distances['B'] = 787.497936505233
            distances['C'] = 81.93289937503738
            distances['D'] = 627.7403922004701
            package ='{'+ '\"cmd\":\"calibrate\",' + '\"data\":' '{' + "\"time\": " + str(distance_data_RX_time) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "}}"
            outgoingQ.put(package)

            distances['A'] = 1064.3768129755551
            distances['B'] = 863.4541099560532
            distances['C'] = 155.54099138169335
            distances['D'] = 641.5122757983669
            package ='{'+ '\"cmd\":\"calibrate\",' + '\"data\":' '{' + "\"time\": " + str(distance_data_RX_time) + "," + "\"pos\": " + str(distances).replace('\'','\"') + "}}"
            outgoingQ.put(package)

            print 'Packaged calibration data'

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




