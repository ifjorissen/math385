#
# objects,py
#
# Defines an RGB struct 'class color'.
# Defines a three-vertex struct 'class facet', that also has a color attribute.
#
import sys
import numpy
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
	def __init__(self, source, sourceid, edge):
		self.twin  = None
		self.next  = None
		self.sid = sourceid
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

	def findNeighbors(self):
		neighbors = []
		for edge in self.edges:
			c = color(0.2, 0.8, 0.2, 0.7);
			if edge.twin is not None:
				edge.twin.face.material = c 
				neighbors.append(edge.twin.face)
		return neighbors

	def normal(self):
		h = self.edges[0]
		if h.vedge.norm() < EPSILON:
			h = self.edges[1]
		h2 = h.next

		if h.next.vedge.norm()<EPSILON:
			h2 = h.next.next
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
		self.origin = [ORIGIN]
		self.ray = None

	def updateCam(self, proj, model, x, y, width, height):
		#normalize coordinates
		xnew = (2*x/width) - 1.0
		ynew = 1.0 - (2*y/height)

		#inverse projection matrix
		iproj = numpy.linalg.inv(proj)

		#convert near pt to worldspace(?) coordinates with iproj
		#and apply the modelview transforms 
		src = numpy.dot(iproj, [xnew, ynew, -1.0, 0.0])
		src = numpy.dot(model, src)

		#find the direction of the ray (originally going in the pure z direction)
							 #after we apply the modelview matrix
		comp = [0.0, 0.0, -1.0, 0.0]
		vdir = numpy.dot(model, comp)
							 
		#update camera properties
		#note that since it's an ortho projection the ray direction is the same regardless
		#of where the click is (or, for that matter the cam origin)
		src = point(src[0], src[1], src[2])
		vdir = vector(vdir[0], vdir[1], vdir[2]).unit()
		self.ray = ray(src, vdir)

	def getRay(self):
		return self.ray 

class surface:
	def __init__(self):
		self.HEDict = {}
		self.facets = []
		self.faces = []
		self.radius = 0.0
		self.vertices = []
		self.filename = None

	def twinEdges(self):
		for key in self.HEDict.keys():
			revkey = key[::-1]
			vid1 = key[0]
			vid2 = key[1]
			he1 = self.HEDict[key]
			if (vid2, vid1) in self.HEDict.keys():
				he2 = self.HEDict[(vid2, vid1)]
				he1.twin = he2
				he2.twin = he1
			# 	print("twins!" + str(key) + str(revkey))
			# else:
			# 	print("key pair not found for " + str(key))

	def addToDict(self, vida, vidb, face):
		verta = self.vertices[vida]
		vertb = self.vertices[vidb]

		#create vector going from verta to vertb
		vab = verta.point.minus(vertb.point)

		#make a halfedge
		e = half_edge(verta, vida, vab)

		#assign the current face to e
		e.face = face

		if vertb.hedge is None:
			vertb.hedge = e

		#add the edge to the dictionary
		self.HEDict[(vida, vidb)] = e

	def updateDict(self, face, i):
		vid1 = face.verts[0]
		vid2 = face.verts[1]
		vid3 = face.verts[2]
		#this is an even face, and a top face
		#so we go counter clockwise
		if i % 2 is 0:
			if (vid1, vid2) not in self.HEDict.keys():
				self.addToDict(vid1, vid2, face) 

			if (vid2, vid3) not in self.HEDict.keys():
				self.addToDict(vid2, vid3, face)

			if (vid3, vid1) not in self.HEDict.keys():
				self.addToDict(vid3, vid1, face)

			#set all of the .next attributes of each half edge
			self.HEDict[(vid1, vid2)].next = self.HEDict[(vid2, vid3)]
			self.HEDict[(vid2, vid3)].next = self.HEDict[(vid3, vid1)]
			self.HEDict[(vid3, vid1)].next = self.HEDict[(vid1, vid2)]

			if face.hedge is None:
				face.hedge = self.HEDict[(vid1, vid2)]

		#odd face, we want to go clockwise with edges
		else:
			if (vid2, vid1) not in self.HEDict.keys():
				self.addToDict(vid2, vid1, face) 

			if (vid3, vid2) not in self.HEDict.keys():
				self.addToDict(vid3, vid2, face)

			if (vid1, vid3) not in self.HEDict.keys():
				self.addToDict(vid1, vid3, face)

			#set all of the .next attributes of each half edge
			self.HEDict[(vid2, vid1)].next = self.HEDict[(vid3, vid2)]
			self.HEDict[(vid3, vid2)].next = self.HEDict[(vid1, vid3)]
			self.HEDict[(vid1, vid3)].next = self.HEDict[(vid2, vid1)]

			if face.hedge is None:
				face.hedge = self.HEDict[(vid2, vid1)]

		return 

	def createHalfEdges(self):
		#creates every half edge 
		for i in range(0, len(self.faces)):
			self.updateDict(self.faces[i], i)

		self.twinEdges()

		for face in self.faces:
			face.get_edges()

	def test(self):
		for key in self.HEDict.keys():
			print("key: " + str(key) + " val: " + str(self.HEDict[key]))
		return

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
				self.faces.append(f)

			elif line.startswith('#'): continue
			else: continue 
		objFile.close()
		return









