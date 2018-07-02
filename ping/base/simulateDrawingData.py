#!/usr/bin/python
import struct
import sys
import socket
import time

if len(sys.argv) == 1:
    print "No parameters supplied.. "
    print "Usage: fakeDrawData.py <X,Y,Z,Q>"
    sys.exit(1)

if not any([sys.argv[1]=='X',sys.argv[1]=='Y',sys.argv[1]=='Z',sys.argv[1]=='Q']):
    print 'Wrong parameter'
    print "Usage: fakeDrawData.py <X,Y,Z,Q>"
    sys.exit(1)


print 'running..'


#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
TXFORMAT = 'cII'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

for x in xrange(0,3):
	y=x+10
	print 'tx: %s%u,%u' % (sys.argv[1],x, y)
	#MESSAGE = struct.pack(TXFORMAT, 'X',x,y)
	MESSAGE = struct.pack(TXFORMAT, sys.argv[1],x,y)
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # INTERNET, UDP
	sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
	time.sleep(0.05)

