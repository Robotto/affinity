#!/usr/bin/python
import struct
import sys
import socket

print 'running..'

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "12")

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
TXFORMAT = 'cII'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)

x=None
y=None
oldX=None
oldY=None
eventcounter=0

xmax=0
ymax=0

xOffset=-140
yOffset=-72

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#types:
# 3: move
# 1: pen up

while event:
	(tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

	# Events with code, type and value == 0 are "separator" events
	if type != 0 or code != 0 or value != 0: 
		if type == 1:
				x=None
				y=None
				oldX=None
				oldY = None
				#REVERSING COODRINATES TO ACCOUNT FOR HARDWARE LAYOUT!!
		if type == 3 and code == 00: #Type: MOVE, CODE: X (set to y)
				#print("x: %u") % value
				#oldX=x
				y=value
				eventcounter+=1
		if type == 3 and code == 01: #Type: MOVE, CODE: Y (set to x)
				#print("y: %u") % value
				#oldY=y
				x=value
				eventcounter+=1
		if type == 3 and x!=None and y!=None:
				#print("x,y: %u,%u") %(x,y)
				#print eventcounter
				#		pass
				if eventcounter%2==0:
					eventcounter=0

					x=x+xOffset
					y=y+yOffset

					if x<0: x=0
					if y<0: y=0
					if x!=0 and y!=0:

						print 'tx: X%u,%u' % (x, y)
						MESSAGE = struct.pack(TXFORMAT, 'X',x,y)
						sock = socket.socket(socket.AF_INET, # Internet
                     						 socket.SOCK_DGRAM) # UDP
						sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


					#if x>xmax:
					#	xmax=x

					#if y>ymax:
					#	ymax=y

					#print 'Max: X:%u Y:%u' % (xmax,ymax) 
					#Max: X:1757 Y:1889

					
	else:
		pass
	event = in_file.read(EVENT_SIZE)

in_file.close()
