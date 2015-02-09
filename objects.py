#
# objects,py
#
# Defines an RGB struct 'class color'.
# Defines a three-vertex struct 'class facet', that also has a color attribute.
#

class color:
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

class facet:

    def __init__(self, _p0,_p1,_p2, _m):
        self.vertices = [_p0,_p1,_p2]
        self.material = _m

    def __getitem__(self,i):
        return self.vertices[i]

class vertex:
	def __init__(self, heh):
		self.hedge = heh

	def vertex_edges(self):
		h = self.hedge
		edges = [h]
		while h.pair.next != self.hedge:
			h = h.pair.next
			edges.append(h)
		return edges

class half-edge:
	def __init__(self, hetwin, henxt, v, f):
		self.twin = hetwin
		self.next = henxt
		self.vertex = v
		self.face = f


class face:
	def __init__(self, heh):
		self.hedge = heh

	def face_edges(self):
		h = self.hedge
		edges = [h]
		while h.next != self.hedge:
			h = h.next
			edges.append(h)
		return edges

	def with_ray(self, ray):
		h = self.hedge
		hnxt = self.hedge.next
		hnxtnxt = hnxt.next

		#find the vector purpendicular to facet
		n = cross(h, hnxt)
		if dot(ray, n) is 0:
			return 'NONE'
		else:
			v1 = h.vertex
			v2 = hnxt.vertex
			v3 = hnxtnxt.vertex



