import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import *
from objgen import *
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

def main():
	print('testing?')
	cyl = surface()
	cyl.readObjFile('sphere5.obj')
	cyl.createHalfEdges()
	print(cyl.HEDict.items())
