#!/usr/bin/python
import struct
import time
import sys

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "19")

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)
x=None
y=None
while event:
    (tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

#types:
# 3: move
# 1: pen up

    if type != 0 or code != 0 or value != 0:
    	if type==3 and code == 00:
    			#print("x: %u") % value
    			x=value
    	if type==3 and code == 01:
    			#print("y: %u") % value
    			y=value
        #if x!=None and y!=None:
    	#		print("x,y: %u,%u") %(x,y)
        print("Event type %u, code %u, value %u at %d.%d" % \
        (type, code, value, tv_sec, tv_usec))
    else:
        # Events with code, type and value == 0 are "separator" events
        #print("===========================================")
        pass
    event = in_file.read(EVENT_SIZE)

in_file.close()
