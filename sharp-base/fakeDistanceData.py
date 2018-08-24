#!/usr/bin/python
#!/usr/bin/python
import struct
import sys
import socket

if len(sys.argv) == 1:
	print "No parameters supplied.. "
	print "Usage: fakeDistanceData.py <number-from-0-to-2>"
	sys.exit(1)

num=int(sys.argv[1])

if num>2:
	print 'number too high!'
	sys.exit(1)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#print 'tx: X%f,%f' % (x, y) #blue
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto('S'+str(num), (UDP_IP, UDP_PORT))
