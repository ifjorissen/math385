

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import facet, color
from random import random
from math import sin, cos, acos, pi, sqrt

def genCubePoints():
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
	return points;

def genCubeFacets():
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
	return facets

def genSphere():
	smoothness = 10
	radius = 2
	numPoints = 2*pi/smoothness
	points=[]
	facets=[]

	#generate the points of the sphere
	for i in range(0, smoothness):
		#latitude (goes from (pi/2) to (-pi/2))
		theta = i*numPoints - pi/2

		for j in range(0, smoothness):
			#longitude (goes from -pi to pi)
			phi = j*numPoints - pi
			print (str(theta) + " " + str(phi))

			# convert into spherical coordinates
			x=radius*cos(theta)*cos(phi)
			y=radius*cos(theta)*sin(phi)
			z=radius*sin(theta)
			points.append(point(x,y,z))

	#generate the facets of the sphere
	#rows
	for row in range(0, smoothness):
		for p in range(0, smoothness):
			k = (p+2)%(smoothness)
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

# def genTorusPoints():


# def genCylinderPoints():

def writeCube():
	cube = open('cube.obj', 'w')
	cube.truncate()

	points = genCubePoints()
	facets = genCubeFacets()

	print ("I'm going to write these to the file.")
	for point in points:
		p = 'v {: f} {: f} {: f}\n'.format(point[0], point[1], point[2])
		cube.write(p)
	cube.write("\n")
	for facet in facets:
		f = 'f {} {} {}\n'.format(facet[0], facet[1], facet[2])
		cube.write(f)

	cube.close()


def writeSphere():
	sphere = open('sphere.obj', 'w')
	sphere.truncate()

	res =  genSphere()
	points = res[0]
	facets = res[1]

	print ("I'm going to write these to the file.")
	for point in points:
		p = 'v {: f} {: f} {: f}\n'.format(point[0], point[1], point[2])
		sphere.write(p)
	sphere.write("\n")
	for facet in facets:
		f = 'f {} {} {}\n'.format(facet[0], facet[1], facet[2])
		sphere.write(f)

	sphere.close()

def main(argc, argv):
	writeCube()
	writeSphere()



if __name__ == '__main__': main(len(sys.argv),sys.argv)