#!/usr/bin/python
import struct
import sys
import socket

print 'running..'

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "12")

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
TXFORMAT = 'cff'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)

x=None
y=None
eventcounter=0

#XRANGE : 0-890
#YRANGE : 70-1660

xOffset=-140
yOffset=-72

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#types:
# 3: move
# 1: pen up

while event:
	(tv_sec, tv_usec, eventtype, code, value) = struct.unpack(FORMAT, event)

	# Events with code, type and value == 0 are "separator" events
	if eventtype != 0 or code != 0 or value!=0: 
		#print 'type=' + str(eventtype)
		#print 'code=' + str(code)
		#print 'value=' + str(value)
		#print
		if eventtype == 1:
				x=None
				y=None
				eventcounter=0
				#REVERSING COODRINATES TO ACCOUNT FOR HARDWARE LAYOUT!!
		if eventtype == 3 and code == 00: #Type: MOVE, CODE: X (set to y)
				#print("x: %u") % value
				#oldX=x
				y=value
				eventcounter+=1
		if eventtype == 3 and code == 01: #Type: MOVE, CODE: Y (set to x)
				#print("y: %u") % value
				#oldY=y
				x=value
				eventcounter+=1

		if eventtype == 3 and x!=None and y!=None and eventcounter==2:
				#print("x,y: %u,%u") %(x,y)
				#print eventcounter
				#		pass
				eventcounter=0

				x=x+xOffset
				y=y+yOffset



				if x<0: x=0
				if y<0: y=0
				if x!=0 and y!=0:

					if y>1660: y=1660
					y=1660.0-y #flip the y axis
				
					y=y/1660.0 #normalize

					if x<890:
						x=x/890.0 #normalize
						print 'tx: X%f,%f' % (x, y) #blue
						MESSAGE = struct.pack(TXFORMAT, 'X',x,y)
					else:
						x=x-890
						x=x/890.0 #normalize
						print 'tx: Y%f,%f' % (x, y) #green
						MESSAGE = struct.pack(TXFORMAT, 'Y',x,y)
					
					sock = socket.socket(socket.AF_INET, # Internet
                 						 socket.SOCK_DGRAM) # UDP
					sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
					
	else:
		pass
	event = in_file.read(EVENT_SIZE)

in_file.close()
