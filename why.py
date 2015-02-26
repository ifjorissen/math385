import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import *
from objgen import *
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

def main(argc, argv):
	print('testing?')
	cyl = surface()
	cyl.readObjFile('sphere5.obj')
	cyl.createHalfEdges()
	print('number of halfedges: ' + str(len(cyl.HEDict)))
	print('number of faces' + str(len(cyl.faces)))
	print('number of facets' + str(len(cyl.facets)))
	print(cyl.HEDict.items())
	print(cyl.HEDict.values())
	firstedge = cyl.HEDict[(8, 13)]
	print('source:' + str(firstedge.vsource))
	print('twin:' + str(firstedge.twin))
	print('next:' + str(firstedge.next))
	print('face:' + str(firstedge.face))
	print('face info' + str(firstedge.face.vertices) + '\nhedge: ' + str(firstedge.face.hedge) + 
		'\n hedge.next' + str(firstedge.face.hedge.next))

	for face in cyl.faces:
		print('face vertices' + str(face.vertices) + 
			'\nhedge: ' + str(face.hedge.vedge) + 
			'\n hedge.next' + str(face.hedge.next.vedge) +
			'\n face edges: ' + str(face.edges))


if __name__ == '__main__': main(len(sys.argv),sys.argv)

