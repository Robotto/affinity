#!/usr/bin/python
import sys
import ast

if len(sys.argv) == 1:
	print "No parameters supplied.. "
	print "Usage: quickPlot.py <imagedata as string>"
	print "Example quickPlot.py \"[ 0.834 , 0.380 ],[ 0.830 , 0.381 ],[ 0.828 , 0.386 ],[ 0.826 , 0.393 ],[ 0.824 , 0.400 ]\""
	sys.exit(1)

testarray = ast.literal_eval(sys.argv[1])

import numpy as np
from matplotlib import pyplot as plt

data = np.array(testarray)

x, y = data.T

plt.gca().invert_yaxis() #because image data in webstrates origins at top left

plt.scatter(x,y)

plt.show()	