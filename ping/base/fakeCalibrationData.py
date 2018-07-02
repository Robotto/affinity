#!/usr/bin/python
#!/usr/bin/python
import struct
import sys
import socket

if len(sys.argv) == 1:
	print "No parameters supplied.. "
	print "Usage: fakeCalibrationData.py <number-from-0-to-4>"
	sys.exit(1)

num=int(sys.argv[1])

#topleft, topright, bottomleft, bottomright, center

aPoints=[380,442,443,486,432]
bPoints=[470,521,414,472,467]
cPoints=[540,488,490,434,488]
dPoints=[473,409,461,515,544]

TXFORMAT = 'cL'

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#print 'tx: X%f,%f' % (x, y) #blue
MESSAGE = struct.pack(TXFORMAT, 'A',aPoints[num])
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

MESSAGE = struct.pack(TXFORMAT, 'B',bPoints[num])
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

MESSAGE = struct.pack(TXFORMAT, 'C',cPoints[num])
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

MESSAGE = struct.pack(TXFORMAT, 'D',dPoints[num])
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))