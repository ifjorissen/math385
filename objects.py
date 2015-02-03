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

