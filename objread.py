#
# half-sphere.py
#
# Author: Jim Fix
# MATH 385, Reed College, Fall 2015
#
# Version: 01.27.15a
#
# This is a sample GLUT program that constructs a hemisphere made 
# up of triangular facets.  It relies heavily on the geometry and
# quaternion packadges.  We'll discuss the design of geometry.py 
# first when we examine affine spaces this and next week.  We'll
# look at using quaternions for specifying rotations, the ideas
# that inform quat.py, in later weeks.
#
# The OpenGL drawing part of the code occurs in drawScene.  The
# building of the geometric model occurs in gen_facet(), and also
# in the main and myKeyFunc procedures.
#
# This code was adapted from Sam Buss' SimpleDraw.py.

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from objects import facet, color
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

trackball = None
facets = None
# rotation = 0.0

def gen_facet_cube():
		""" 
				Generates a random equilateral triangular facet whose center
				is on the unit sphere and whose normal vector is pointing out
				of the sphere.  It only allows triangles to be on the front
				hemisphere.
		"""
		radius = 1.0 # radius of the sphere
		size = 0.7   # scale of the triangle

		# We are observing from above the x-y plane.
		eye = vector(0.0,0.0,1.0)

		
		# Pick three random directions, vectors u,v,w that serve as an 
		# orthonormal basis, to specify a triangular facet that's tangent 
		# to the sphere.

		""" Alternative method that looks less uniform, using quaternions:

		R = quat.for_rotation(2*pi*random(),vector.random_unit()).as_matrix()

		u = R[0]
		v = R[1]
		w = R[2]

		"""

		# Pick a random direction w, but in the +z halfspace
		w = vector.random_unit()
		while w.dot(eye) < 0.0:
				w = vector.random_unit()

		# We will use w to determine the location of the facet.
		# Now pick two more vectors to give the orientation of the facet.

		# We do this by devising vectors u,v,w that serve as a right-handed
		# coordinate system.  In other words, we want
		#
		#   u x v = w
		#   v x w = u
		#   w x u = v
		#

		u_ish = vector.random_unit()
		while abs(w.cross(u_ish)) < EPSILON:
				u_ish = vector.random_unit()
		v = w.cross(u_ish).unit()
		u = v.cross(w)

		#
		# Now describe the three vertices of the facet.
		#
		center = ORIGIN + w * radius 
		a = 1.0 / sqrt(3.0)
		p1 = center + size * a * v
		p2 = center + (-size * (a * v / 2.0 + u / 2.0))
		p3 = center + (-size * (a * v / 2.0 - u / 2.0))

		#
		# Now pick a random color of the facet, shaded by a light in front.
		#
		light = vector(0.0,0.0,1.0)
		shine = max(w.dot(light),0.1 * random() + 0.1)
		c = color(shine*(1.0-random()*0.1),
							shine*(1.0-random()*0.1),
							shine*(1.0-random()*0.1))
		
		#
		# Construct that new facet.
		#
		return facet(p1,p3,p2,c)


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
				glOrtho(-5.0, 5.0, -h/w * 5.0, h/w * 5.0, -5.0, 5.0)


def main(argc, argv):
		global trackball, facets
		facets = []
		points = []

		cube = open('sphere.obj')
		for line in cube:
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
					fint = int(f)
					pts.append(points[fint])
				c = color(random(), random(), random())

				face = facet(pts[0], pts[1], pts[2], c)
				facets.append(face)

			elif line.startswith('#'): continue
			else: continue 


		trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))

		glutInit(argv)
		glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowPosition(0, 20)
		glutInitWindowSize(500, 500)
		glutCreateWindow( 'cube.py - Press ESC to quit' )
		initRendering()

		# Register interaction callbacks.
		glutKeyboardFunc(myKeyFunc)
		glutSpecialFunc(myArrowFunc)
		glutReshapeFunc(resizeWindow)
		glutDisplayFunc(drawScene)

		print()
		# print('Press the arrow keys rotate the object.')
		print('Press SPACE to shuffle its geometry.')
		print('Press ESC to quit.\n')
		print()

		glutMainLoop()

		return 0

if __name__ == '__main__': main(len(sys.argv),sys.argv)
