# Isabella Jorissen
# Math 385
# Hw 1A
# shapes.py

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import *
from objgen import *
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

trackball = None
light = None
facets = None
xStart = 0
yStart = 0
width = 360
height = 360
scale = 1.0/360.0
cam = None
radius = 0.0


# def matInv(mat):

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
			glColor4f(f.material.red, f.material.green, f.material.blue, f.material.alpha)
			# glColor4f(0.0, 0.0, 0.0, 0.0)
			glVertex3fv(f.vertices[0].point.components()) 
			glVertex3fv(f.vertices[1].point.components()) 
			glVertex3fv(f.vertices[2].point.components()) 
	glEnd()
	for f in facets:
		glBegin(GL_LINES)
		for hedge in f.edges:
			glColor4f(.8, .0, .2, 1.0)
			dest = hedge.next.vsource.point
			glVertex3fv(hedge.vsource.point.components()) 
			glVertex3fv(dest.components()) 
		glEnd()


	# Render the scene.
	glFlush()


def myKeyFunc(key, x, y):
	""" Handle a "normal" keypress. """
	# Handle ESC key.
	if key == b'\033':	
# "\033" is the Escape key
			sys.exit(1)

def facetSelect(btn, state, x, y):
	global facets, cam
	#get the transformation matrices
	proj = glGetDoublev(GL_PROJECTION_MATRIX)
	model = glGetDoublev(GL_MODELVIEW_MATRIX)
	cam.updateCam(proj, model, x, y, width, height)
	clickray = cam.getRay()

	#for every facet, check to see if there's an intersection
	for facet in facets:
		res = facet.intersect_ray(clickray)
		if res is not None:
			print("res: " + str(res))
			#only color the facet closest to ray.source
			#to do: make this the min of all res[1]
			if res[1] <= radius:
				c = color(.8, .4, 0.8, 0.7)
				facet.material = c
				facet.findNeighbors()
	glutPostRedisplay()

# def processMouse(btn, state, x, y):
def sliceDir(x, y):
	print('slice dir called')

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


def resize(w, h):
    """ Register a window resize by changing the viewport.  """
    global width, height, scale
    glViewport(0, 0, w, h)
    width = w
    height = h
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    r = radius
    print("resize called")
    if w > h:
        glOrtho(-w/h*r, w/h*r, -r, r, -r, r)
        scale = 2.0 * r / h 
    else:
        glOrtho(-r, r, -h/w * r, h/w * r, -r, r)
        scale = 2.0 * r / w 


def main(argc, argv):
	global trackball, facets, cam, radius

	#read in input
	if argc is 3:
		shape = argv[1]
		smoothness = argv[2]
	elif argc is 2:
		shape = argv[1]
		smoothness = 10
	else:
		shape = "bunny"
		smoothness = 15

	#generate the .obj shapefile, and read it
	shapeFile = shape + str(smoothness) + ".obj"
	writeObj(str(shape), smoothness)
	s = surface()
	s.readObjFile(shapeFile)
	s.createHalfEdges()

	facets = s.faces
	radius = 2.0
	cam = camera()

	#you can even extend facets to see the shapes overlaid
	#facets.extend(readObjFile'torus.obj')

	trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))

	glutInit(argv)
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowPosition(0, 20)
	glutInitWindowSize(width, height)
	glutCreateWindow( 'shapes - Press ESC to quit' )
	initRendering()

	# Register interaction callbacks.
	glutKeyboardFunc(myKeyFunc)
	glutSpecialFunc(myArrowFunc)
	glutMouseFunc(facetSelect)
	glutMotionFunc(sliceDir)
	glutReshapeFunc(resize)
	glutDisplayFunc(drawScene)

	print()
	print('Press the arrow keys rotate the object.')
	print('Press ESC to quit.\n')
	print()

	glutMainLoop()

	return 0

if __name__ == '__main__': main(len(sys.argv),sys.argv)
