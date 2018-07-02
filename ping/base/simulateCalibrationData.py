#!/usr/bin/python
#!/usr/bin/python
import struct
import sys
import socket

TXFORMAT = 'c'

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto('?', (UDP_IP, UDP_PORT))
