#####Hw 2A Math 385: Computer Graphics
#####Isabella Jorissen
#####2.16.15

##2.19.15:
Half edge structure seems to be implemented correctly. I should probably write some tests for this.
getNeighbors() enabled for neighbors which share an edge. See screencap `sphereNeighbor.png`

##2.18.15:
To do: projection using glFrustum instead of glOrtho
* implement the half edges edge.twin.face & edge.twin.next (done!)
*port this baby over to webGL 


##UPDATES as of 2.16.15:
###Known Bugs:
  
  * If facets start at 1 instead of 0, you need to subtract 1 in the readObjFile function in objects.py
  * The sphere, torus, and cylinder have holes since the range is not inclusive in the outer loop
  * the click event does not correctly find the intersection of the facet and the ray due to improper calculations going into the xscreen, yscreen -> projection
  * Numpy format handler module is not loaded in from opengl accelerate 

###To Do:
  * Fix known bugs
  * Strip out unnecessary surface attributes (probably facets)
  * Testing for the half edges (esp testing twin attributes)
  * Make the vertex and face classes extensions of facet


-RayPicking: this is pretty close:
** problem: clicking outside of circle still leads to res
** if you set ray to self.transloc, this is solved, but the intersections aren't always right
  xnew = ((2*x) / width) - 1.0
  ynew = 1.0 - ((2*y)/height)
  znew = 2.0*z - 1.0
  cxyz = numpy.dot(iprod, [xnew, ynew, znew, 1.0])
  self.transloc = point(cxyz[0], cxyz[1], cxyz[2])
  self.screenproj = point(xnew, ynew, znew)
  self.dir = self.screenproj.minus(self.transloc).neg().unit()
  self.ray = ray(self.screenproj, self.dir)
-
-also works very well:
-  winz = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
-  xnew = (2.0*x / width) - 1.0
-  ynew = 1.0 - (2.0*y /height)
-  znew = 2.0*winz - 1.0
-  #locproj = np.dot(np.dot(proj, model), [xnew, ynew, znew, 1.0])
-  loc = point(xnew, ynew, znew)
-  cxyz = np.dot(iprod, [xnew, ynew, znew, 1.0])
-  camloc = point(cxyz[0], cxyz[1], cxyz[2])
-  vdir = loc.minus(camloc).neg().unit()
-  clickray = ray(loc, vdir)
-
-a third option that is more correct??? but doesn't work as well
-  winz = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
-  # cam.updateCam(iprod, x, y, winz)
-  xnew = (2.0*x / width) - 1.0
-  ynew = 1.0 - (2.0*y /height)
-  znew = 2.0*winz - 1.0
-  # locproj = np.dot(np.dot(proj, model), [xnew, ynew, znew, 1.0])
-  loc = point(xnew, ynew, znew)
-  print("xyz: " + str(xnew) + " " + str(ynew) + " " + str(znew))
-  print("loc: " + str(loc))
-  # print("locproj: \n" + str(locproj))
-  cxyz = np.dot(iprod, [xnew, ynew, -1.0, 1.0/znew])
-  print("cxyz \n" + str(cxyz))
-  camloc = point(cxyz[0], cxyz[1], cxyz[2])
-  vdir = loc.minus(camloc).unit()
-  clickray = ray(camloc, vdir)




Previous Documentation (For HW1)

Used Jim Fix's with_geom code as a base, renames & stripped down half-sphere.py. It has been renamed shapes.py


##To run the program:

`python3 shapes.py <shape> <smoothness>`

where <shape> is one of: 'cylinder', 'cube', 'torus', 'sphere'
where <smoothness> is an integer (recommend > 5)

If neither <shape> nor <smoothness> is not specified, a window will open with a torus shape of smoothness 10. If <smoothness> is omitted, the default value is also 10. Error will result if <shape> is omitted and smoothness is provided.

E.g: `python3 shapes.py cylinder 15` will generate a .obj file called "cylinder15.obj"

## To generate some default .obj files:

`python3 objgen.py`

The screengrabs are all from running:
`python3 shapes.py cylinder 15`
`python3 shapes.py sphere 15`
`python3 shapes.py torus 15`
`python3 shapes.py cube`



##Program structure:

shapes.py is largely Jim's and uses his objects.py, geometry.py code. The interface and interactivity is the same.  The main() function of the program has been modified to (optionally) take in user input. The function generates .obj files using the code in objgen.py.

objgen.py also uses Jim's objects,points/vectors etc. It has a function for each of the four shapes which generates the corresponding facets and points. Currently, there is a bug where the final row of facets is not displayed. This is noticable in the torus (the innermost "row" is missing) and the sphere (the top cap/"row" is also missing). 

running the main() of objgen.py generates a few .obj files to test things out. In the future, shapes.py can leverage this and optionally "load" a file instead of generating it and loading it. (But for now, I thought it was cooler to do the former).

The facet structure is pretty rudimentary. Take the sphere as an example:
We have <smoothness> number of rows and columns. The nested for loops assign angles phi and theta to each entry. Using the parametrization of a sphere in r3, x, y and z are calculated using the radius, theta and phi. 

The facets make use of this stucture. There are two "types" of facets:
  * facets with 2 points on a row and one point at (row-1) 
  * facets with 1 point on a row and two points at (row-1)

I've called these Bottom facets and Top facets, respectively
Top facets:
------ . ------ row r
			/ \
-----.---. ---- row r-1

Bottom facets:
-----.---. ---- row r
			\ /
------ . ------ row r-1