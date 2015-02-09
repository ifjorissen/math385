

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import facet, color
from random import random
from math import sin, cos, acos, pi, sqrt

def genCube():
	size = 2
	points = [[0,0,0],
						[0, 1*size, 0], 
						[1*size, 0, 0], 
						[1*size, 1*size, 0],
						[0,0,1*size],
						[1*size, 0, 1*size],
						[1*size, 1*size, 1*size],
						[0, 1*size, 1*size]
	]

		#back face
	facets = [[0, 1, 3],
						[0, 2, 3], #back face
						[0, 1, 7],
						[0, 4, 7], #left
						[0, 4, 5],
						[0, 2, 5], #bottom
						[6, 1, 3],
						[6, 1, 7], #top
						[6, 2, 3],
						[6, 2, 5], #right
						[6, 4, 7],
						[6, 4, 5]  #front
	]

	return points, facets;

def genSphere(smooth):
	smoothness = smooth
	radius = 2
	numPoints = 2*pi/smoothness
	points=[]
	facets=[]

	#generate the points of the sphere
	for i in range(0, smoothness):
		#latitude (goes from (pi/2) to (-pi/2))
		theta = ((i/2)*numPoints-pi)

		for j in range(0, smoothness):
			#longitude (goes from -pi to pi)
			phi = j*numPoints

			# convert spherical coordinates into R^3
			x=radius*sin(theta)*cos(phi)
			y=radius*sin(theta)*sin(phi)
			z=radius*cos(theta)
			points.append(point(x, y, z))

	#generate the facets of the sphere
	#rows
	for row in range(0, smoothness):
		for p in range(0, smoothness):
			k = (p + 1)%(smoothness)

			p1 = smoothness*row + p
			p2 = smoothness*row + k
			p3 = smoothness*(row-1) + k
			p4 = smoothness*(row-1)+ p


			#top facets 
			# / \
			# ---
			#account for first row
			# if (row+2) is smoothness:
			# 	p2 = smoothness*row

			# if (row-1) is 0:
			# 	p4 = smoothness*(row-1)

			if row is not 0:
				facets.append([p4, p3, p2])

			#bottom facets
			 # ---
			 # \ /
			#account for last row
			# if (row-1) is 0:
			# 	p4 = smoothness*(row-1)

				facets.append([p1, p2, p4])

	return points, facets

def genTorus(smooth):
	innerR = 1
	outerR = 3
	smoothness = smooth
	numPoints = 2*pi/smoothness
	points=[]
	facets=[]

	#generate the points of the sphere
	for i in range(0, smoothness):
		#latitude (goes from (pi/2) to (-pi/2))
		theta = (i*numPoints-pi)

		for j in range(0, smoothness):
			#longitude (goes from -pi to pi)
			phi = j*numPoints

			# plug into parametrization
			x = (outerR + innerR*cos(theta))*cos(phi)
			y = (outerR + innerR*cos(theta))*sin(phi)
			z = innerR*sin(theta)
			points.append(point(x, y, z))

	#generate the facets of the torus
	#rows
	for row in range(0, smoothness):
		for p in range(0, smoothness):
			k = (p + 1)%(smoothness)

			p1 = smoothness*row + p
			p2 = smoothness*row + k
			p3 = smoothness*(row-1) + k
			p4 = smoothness*(row-1)+ p


			#top facets 
			# / \
			# ---
			#account for first row
			if row is not 0:
				facets.append([p4, p3, p2])

			#bottom facets
			 # ---
			 # \ /

				facets.append([p1, p2, p4])

	return points, facets


def genCylinder(smooth):
	smoothness = smooth
	radius = 2
	height = 5
	numPoints = 2*pi/smoothness
	points=[]
	facets=[]

	#generate the points of the sphere
	for i in range(0, smoothness):
		#latitude (goes from (pi/2) to (-pi/2))
		for j in range(0, smoothness):
			#longitude (goes from -pi to pi)
			phi = j*numPoints

			# cylindrical coordinates ==> R^3
			x=radius*cos(phi)
			y=radius*sin(phi)
			z=i*(height/smoothness)
			points.append(point(x, y, z))

	#generate the facets of the sphere
	#rows
	for row in range(0, smoothness):
		for p in range(0, smoothness):
			k = (p + 1)%(smoothness)

			p1 = smoothness*row + p
			p2 = smoothness*row + k
			p3 = smoothness*(row-1) + k
			p4 = smoothness*(row-1)+ p


			#top facets 
			# / \
			# ---
			#bottom facets
		  # ---
	  	# \ /

			if row is not 0:
				facets.append([p4, p3, p2])
				facets.append([p1, p2, p4])

	return points, facets

#shape handler function
def genShape(s, smoothness):
	facets = []
	points = []
	res = []
	if s == "cylinder":
		res = genCylinder(smoothness)
	elif s == "torus":
		res = genTorus(smoothness)
	elif s == "sphere":
		res = genSphere(smoothness)
	elif s == "cube":
		res = genCube()

	points = res[0]
	facets = res[1] 

	return points, facets


#this function writes an object's points and facets to a .obj file
#the file name output is <shape><smoothness>.obj
def writeObj(shape, smoothness=10):
	points = []
	facets = []

	fileName = str(shape) + str(smoothness) + ".obj" 
	shapeFile = open(fileName, 'w')

	shapeFile.truncate()

	res = genShape(shape, int(smoothness))
	points = res[0]
	facets = res[1]

	print ("I'm going to write these to the file.")
	info = "\t#" + fileName + "\n\t#Smoothness: " + str(smoothness) + "\n\n"
	shapeFile.write(info)
	for point in points:
		p = 'v {: f} {: f} {: f}\n'.format(point[0], point[1], point[2])
		shapeFile.write(p)
	shapeFile.write("\n")
	for facet in facets:
		f = 'f {} {} {}\n'.format(facet[0], facet[1], facet[2])
		shapeFile.write(f)

	shapeFile.close()

def readObjFile(s):
	facets = []
	points = []

	#parse the file (very minimal)
	objFile = open(s)
	for line in objFile:
		if line.startswith('v'):
			pf = []
			pstr = line.split()
			pstr.pop(0)
			for p in pstr:
				pf.append(float(p))
			points.append(point(pf[0], pf[1], pf[2]))
		elif line.startswith('f'):
			pts = []
			fstr = line.split()
			fstr.pop(0)
			for f in fstr:
				fint = int(f)-1 #account for the fact that facets start at 1, not 0
				pts.append(points[fint])

			c = color(random(), random(), random())

			face = facet(pts[0], pts[1], pts[2], c)
			facets.append(face)

		elif line.startswith('#'): continue
		else: continue 
	objFile.close()
	return facets


def main(argc, argv):
	#write some generic objects to test .obj file formats
	writeObj("cylinder", 15)
	writeObj("cube")
	writeObj("sphere", 15)
	writeObj("torus", 15)



if __name__ == '__main__': main(len(sys.argv),sys.argv)