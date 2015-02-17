#
# objects,py
#
# Defines an RGB struct 'class color'.
# Defines a three-vertex struct 'class facet', that also has a color attribute.
#

import numpy as np
from constants import *
from random import random
from geometry import vector, point, ORIGIN

class color:
	def __init__(self, r, g, b, a):
		self.red = r
		self.green = g
		self.blue = b
		self.alpha = a

class ray:
	def __init__(self,point,direction):
		self.source = point
		self.towards = direction.unit()

class facet:
	def __init__(self, face, _m):
		self.vertices = face.vertices
		self.material = _m

	def __getitem__(self,i):
		return self.vertices[i]

	def identify(self, i, j, k):
		self.vertids = [i, j, k]

class vertex:
	def __init__(self, _p0, _p1, _p2):
		self.point = point(_p0, _p1, _p2)
		self.hedge = None

	def addHE(self, he):
		self.hedge = he

	def vertex_edges(self):
		h = self.hedge
		edges = [h]
		while h.twin.next != self.hedge:
			h = h.twin.next
			edges.append(h)
		return edges

class half_edge:
	def __init__(self, source, edge):
		self.twin  = None
		self.next  = None
		self.vsource = source
		self.vedge  = edge
		self.face  = None


class face:
	def __init__(self, _p0,_p1, _p2, _m):
		self.vertices = [_p0,_p1,_p2]
		self.material = None
		self.hedge = None
		self.edges = []
		self.material = _m

	def identify(self, i, j, k):
		self.verts = [i, j, k]

	def get_edges(self):
		if self.hedge is not None:
			h = self.hedge
			edges = [h]
			while h.next != self.hedge:
				h = h.next
				edges.append(h)
			self.edges = edges
		else:
			self.edges = []
		return self.edges

	def normal(self):
		h = self.edges[0]
		if h.vedge.norm() < EPSILON:
			h = self.edges[1]
		h2 = h.next

		if h.next.vedge.norm()<EPSILON:
			h2 = h.next.next
		
		# print ("h: " + str(h.vsource.point))
		# print ("h2: " + str(h2.vedge.components()))
		return h.vedge.cross(h2.vedge)

	def intersect_ray(self,obj):
		R = obj.source
		d = obj.towards
		Q1 = self.vertices[0].point
		Q2 = self.vertices[1].point
		Q3 = self.vertices[2].point

		# compute normals to the plane of the facet
		Q = Q1
		v2 = Q2 - Q1
		v3 = Q3 - Q1
		o = v2.cross(v3)
		if abs(o) < EPSILON:
			# the facet is a sliver or a point
			# print("abs o is < epsilon")
			return None

		ell = v2.unit()
		emm = v3.unit()
		enn = ell.cross(emm).unit()
		dist = enn.dot(R - Q)
		if abs(dist) < EPSILON:
			# the ray source R is in the plane of this facet
			# print("abs dist is < epsilon")
			return None

		# flip the orientation of the surface normal to the back face
		if dist < 0:
			enn = -enn
		ratio = -(enn.dot(d))
		if ratio <= 0:
			# print("ratio is <= 0")
			# the ray shoots along or away from the facet's plane
			return None

		# compute where the ray intersects the plane
		scale = abs(dist) / ratio
		P = R + (scale * d)

		# check if P lives within the facet
		w = P-Q
		o3 = v2.cross(w)
		o2 = w.cross(v3)
		if o2.dot(o) < 0 or o3.dot(o) < 0:
			# print("not in the trangle is <= 0")
			# the point P is not in the cone <Q1,v2,v3>
			return None

		a2 = abs(o2)/abs(o)
		a3 = abs(o3)/abs(o)
		a1 = 1.0-a2-a3
		if a1 < 0.0 or a2 < 0.0 or a3 < 0.0:
			# print("point is beyong line")
			# the point P is beyond line <Q2,Q3> in that cone
			return None

		return [[a1,a2,a3],scale,dist]

class camera:
	def __init__(self):
		self.origin = []
		self.screenproj = []
		self.dir = []

	def updateCam(self, mat, x, y, z):
		#normalize coordinates
		xnew = ((2*x) / width) - 1.0
		ynew = 1.0 - ((2*y)/height)
		znew = 2.0*winz - 1.0
		cxyz = np.dot(iprod, [xnew, ynew, -1.0, 1.0/znew])

class surface:
	def __init__(self):
		self.HEDict = {}
		self.facets = []
		self.faces = []
		self.radius = 0.0
		self.vertices = []
		self.filename = None

	def addToDict(self, vida, vidb, face):
		verta = self.vertices[vida]
		vertb = self.vertices[vidb]

		vab = verta.point.minus(vertb.point)
		vba = vertb.point.minus(verta.point)

		e = half_edge(verta, vab)
		etwin = half_edge(vertb, vba)
		e.face = face
		e.twin = etwin

		if verta.hedge is None:
			verta.hedge = etwin
		if vertb.hedge is None:
			vertb.hedge = e

		self.HEDict[(vida, vidb)] = e
		self.HEDict[(vidb, vida)] = etwin

	def updateDict(self, face):
		vid1 = face.verts[0]
		vid2 = face.verts[1]
		vid3 = face.verts[2]
		if (vid1, vid2) in self.HEDict:
			e = self.HEDict[(vid1, vid2)]
			if e.face is None:
				e.face = face

		else:
			self.addToDict(vid1, vid2, face) 

		if (vid2, vid3) in self.HEDict:
			e = self.HEDict[(vid2, vid3)]
			if e.face is None:
				e.face = face
		else: 
			self.addToDict(vid2, vid3, face)

		if (vid3, vid1) in self.HEDict:
			e = self.HEDict[(vid3, vid1)]
			if e.face is None:
				e.face = face
		else:
			#create this he and its twin
			self.addToDict(vid3, vid1, face)

		#set all of the .next attributes of each half edge
		self.HEDict[(vid1, vid2)].next = self.HEDict[(vid2, vid3)]
		self.HEDict[(vid2, vid3)].next = self.HEDict[(vid3, vid1)]
		self.HEDict[(vid3, vid1)].next = self.HEDict[(vid1, vid2)]

		if face.hedge is None:
			face.hedge = self.HEDict[(vid1, vid2)]
			face.get_edges()

		return 

	def createHalfEdges(self):
		for face in self.faces:
			self.updateDict(face)

	def readObjFile(self, fileS):
		self.filename = fileS
		objFile = open(fileS)
		for line in objFile:
			if line.startswith('v'):
				pf = []
				pstr = line.split()
				pstr.pop(0)
				for p in pstr:
					pf.append(float(p))
				# pt = point(pf[0], pf[1], pf[2])
				self.vertices.append(vertex(pf[0], pf[1], pf[2]))
			elif line.startswith('f'):
				pts = []
				ids = []
				fstr = line.split()
				fstr.pop(0)
				for f in fstr:
					fint = int(f) # subtract 1 to account for the fact that facets start at 1, not 0 in other .obj files
					pts.append(self.vertices[fint])
					ids.append(fint)

				c = color(0.0, 0.0, 0.0, 1.0)
				f = face(pts[0], pts[1], pts[2], c)
				f.identify(ids[0], ids[1], ids[2])
				# fac = facet(f, c)
				# self.facets.append(fac)
				self.faces.append(f)

			elif line.startswith('#'): continue
			else: continue 
		objFile.close()
		return









