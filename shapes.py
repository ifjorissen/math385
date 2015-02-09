# Isabella Jorissen
# Math 385
# Hw 1A
# shapes.py

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import facet, color
from objgen import *
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

trackball = None
facets = None


def drawScene():
	""" Issue GL calls to draw the scene. """

	# Clear the rendering information.
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# Clear the transformation stack.
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	# # Transform the objects drawn below by a rotation.
	trackball.glRotate()
	
	# Draw the light source "pixel"
	glColor(1.0,1.0,1.0)
	glPointSize(20)
	#
	glBegin(GL_POINTS)
	point(0.0,0.0, 4.0).glVertex3()
	glEnd()

	# Draw all the triangular facets.
	glBegin(GL_TRIANGLES)
	for f in facets:
			glColor3f(f.material.red, f.material.green, f.material.blue)
			glVertex3fv(f[0].components()) 
			glVertex3fv(f[1].components()) 
			glVertex3fv(f[2].components()) 
	glEnd()

	# Render the scene.
	glFlush()


def myKeyFunc(key, x, y):
	""" Handle a "normal" keypress. """
	# Handle ESC key.
	if key == b'\033':	
# "\033" is the Escape key
			sys.exit(1)


def myArrowFunc(key, x, y):
	""" Handle a "special" keypress. """
	global trackball

	x_axis = vector(1.0,0.0,0.0)
	y_axis = vector(0.0,1.0,0.0)

	# Apply an adjustment to the overall rotation.
	if key == GLUT_KEY_DOWN:
		# Transform the objects drawn below by a rotation.
		trackball = quat.for_rotation( pi/12.0,x_axis) * trackball
	if key == GLUT_KEY_UP:
		trackball = quat.for_rotation(-pi/12.0,x_axis) * trackball
	if key == GLUT_KEY_LEFT:
		trackball = quat.for_rotation(-pi/12.0,y_axis) * trackball
	if key == GLUT_KEY_RIGHT:
		trackball = quat.for_rotation( pi/12.0,y_axis) * trackball

	# Redraw.
	glutPostRedisplay()


def initRendering():
	""" Initialize aspects of the GL scene rendering.  """
	glEnable (GL_DEPTH_TEST)


def resizeWindow(w, h):
	""" Register a window resize by changing the viewport.  """
	glViewport(0, 0, w, h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	if w > h:
			glOrtho(-w/h*2.0, w/h*5.0, -5.0, 5.0, -5.0, 5.0)
	else:
			glOrtho(-.2, .2, -h/w * .2, h/w * .2, -.2, .2)


def main(argc, argv):
	global trackball, facets

	#read in input
	if argc is 3:
		shape = argv[1]
		smoothness = argv[2]
	elif argc is 2:
		shape = argv[1]
		smoothness = 10
	else:
		shape = "torus"
		smoothness = 10

	#generate the .obj shapefile, and read it
	shapeFile = shape + str(smoothness) + ".obj"
	writeObj(str(shape), smoothness)
	facets = readObjFile('lamp.obj')


	#you can even extend facets to see the shapes overlaid
	#facets.extend(readObjFile'torus.obj')

	trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))

	glutInit(argv)
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowPosition(0, 20)
	glutInitWindowSize(500, 500)
	glutCreateWindow( 'shapes - Press ESC to quit' )
	initRendering()

	# Register interaction callbacks.
	glutKeyboardFunc(myKeyFunc)
	glutSpecialFunc(myArrowFunc)
	glutReshapeFunc(resizeWindow)
	glutDisplayFunc(drawScene)

	print()
	print('Press the arrow keys rotate the object.')
	print('Press ESC to quit.\n')
	print()

	glutMainLoop()

	return 0

if __name__ == '__main__': main(len(sys.argv),sys.argv)
