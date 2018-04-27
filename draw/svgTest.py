#!/usr/bin/python
import svgwrite
import struct
#import time
import sys
from bs4 import BeautifulSoup

print 'running..'

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "12")

outfile_path = sys.argv[1] if len(sys.argv) < 3 else sys.argv[2]

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

#open file in text mode
out_file = open(outfile_path,"w")

svg_size_width = 1700
svg_size_height = 1900

dwg = svgwrite.Drawing('test.svg', (svg_size_width, svg_size_height))
#dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(255,255,255)'))

event = in_file.read(EVENT_SIZE)

x=None
y=None
oldX=None
oldY=None
eventcounter=0

#types:
# 3: move
# 1: pen up

while event:
	(tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

	if type != 0 or code != 0 or value != 0:
		if type == 1:
				x=None
				y=None
				oldX=None
				oldY = None
		if type == 3 and code == 00:
				#print("x: %u") % value
				oldX=x
				x=value
				eventcounter+=1
		if type == 3 and code == 01:
				#print("y: %u") % value
				oldY=y
				y=value
				eventcounter+=1
		if x!=None and y!=None and oldX!=None and oldY!=None:
				#print("x,y: %u,%u") %(x,y)
				#print eventcounter
				if x>1700 and y>1850:
						dwg.save()
						print
						print 'Created SVG. Putting it into body of webstrate.'
						svgSTR = dwg.tostring()

						print 'new SVG:'
						print svgSTR

						#htmlIn=out_file.read()

						#soup = BeautifulSoup(htmlIn,"lxml")

						#htmlBody = soup.find('body')

						print
						print 'html before:'
						#print htmlIn

						before = """<html __wid="q5Ip4n9R"><head __wid="k8mytF1Q"><style id="style-main" __wid="C615cdZ3">
body {
  margin: 0px;
  }
</style></head><body __wid="wfvTr6tn">"""

						after = """</body></html>"""


						#print 'before: ',before
						#print 'after: ',after
						htmlOut = before + svgSTR + after

						#print
						#print 'html after:'
						#print #soup.find('body')
						#print htmlOut
						#out_file.write(htmlOut)

						#out_file.close()

						break
				#		pass
				else:
					if eventcounter%2==0:
						eventcounter=0
						#dwg.add(dwg.line((oldX, oldY), (x, y), stroke=svgwrite.rgb(0, 0, 0, '%')))
						#dwg.add(dwg.line((oldX, oldY), (x, y), stroke='red', stroke_width=3))
						#dwg.add(dwg.line((oldX, oldY), (x, y), stroke='red', stroke_width=3))
						p = dwg.path(d="M {0},{1} {2},{3} z".format(oldX, oldY, x, y), stroke="red", stroke_width=10)
						dwg.add(p)

						print 'added path from %u,%u to %u,%u' %(oldX, oldY, x, y)

		#print("Event type %u, code %u, value %u at %d.%d" % \
		#    (type, code, value, tv_sec, tv_usec))
	else:
		# Events with code, type and value == 0 are "separator" events
		#print("===========================================")
		pass
	event = in_file.read(EVENT_SIZE)

in_file.close()
