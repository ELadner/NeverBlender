#################################################################
#
# Trimesh.py
# A class for easy manipulation of Bioware Trimesh objects.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

from NwnMath import euler2nwn
from string import join
import NBLog
from NBLog import putlog

class Trimesh:
	# Can be set
	#_name = "untitledtrimesh"
	#_parent = "NULL"
	
	# Cannot be set at the moment!
	# (Could be, but what are the corresponding material props??)
	#_ambient = [1.0, 1.0, 1.0]
	#_diffuse = [1.0, 1.0, 1.0]
	#_shininess = 0.25

	# Can be set.
	#_position = [0.0, 0.0, 0.0]
	#_orientation = [0.0, 0.0, 0.0]         # stored in euler format!
	#_scale = 1.0
	#_texture = ""
	#_wirecolor = [0.6, 0.6, 0.6]
	#_specular = [0.05, 0.05, 0.05]
	#_tilefade = 0
	# Private data.
	#_verts = []
	#_faces = []
	#_texverts = []

	def __init__(self, object=None):
		if object==None:
			self._name = "untitledtrimesh"
			self._parent = "NULL"
			self._position = [0.0, 0.0, 0.0]
			self._orientation = [0.0, 0.0, 0.0]
			self._scale = 1.0
		else:
			# Beginnings of construction from Blender Object
			self._name = object.name
			if object.parent!=None:
				self._parent = object.parent.name
			else:
				self._parent = "NULL"
			self._position = object.pos
			self._orientation = object.rot
			# This one does averaging..
			self.setScale(object.size)
	
		# These can be set in Material...
		self._wirecolor = [0.6, 0.6, 0.6]
		self._specular = [0.05, 0.05, 0.05]
		# ...but these cannot.
		self._ambient = [1.0, 1.0, 1.0]
		self._diffuse = [1.0, 1.0, 1.0]
		self._shininess = 0.25

		# Can be set.
		self._texture = ""
		self._tilefade = 0
		# Private data.
		self._verts = []
		self._faces = []
		self._texverts = []

	# Basic stuff.
	def setName(self, name):
		self._name = name
	def setParent(self, parent):
		self._parent = parent

	def setPosition(self, poslist):
		assert len(poslist) == 3
		self._position = poslist
	def setOrientation(self, orilist):
		assert len(orilist) == 3
		if orilist[0] != 0.0 or orilist[1] != 0.0 or orilist[2] != 0.0:
			putlog(NBLog.SPAM, 
			       "Object %s is rotated." % self._name,
			       "Trimesh")
		else:
			putlog(NBLog.SPAM, 
			       "Object %s isn't rotated." % self._name,
			       "Trimesh")
		self._orientation = orilist

	def setWireColor(self, color):
		assert len(color) == 3
		self._wirecolor = color
	def setSpecularColor(self, color):
		assert len(color) == 3
		self._specular = color

	def setScale(self, scalelist):
		assert len(scalelist) == 3
		if scalelist[0] != scalelist[1] or \
		  scalelist[1] != scalelist[2] or \
		  scalelist[0] != scalelist[2]:
			self._scale = \
			      (scalelist[0]+scalelist[1]+scalelist[2]) / 3
			putlog(NBLog.WARNING, 
			       "Object %s scale not uniform! " +
			       "x = %f, y = %f, z = %f "+
			       "Using avg scale as uniform scale: %f" %
			       (self._name,
				scalelist[0], scalelist[1], scalelist[2],
				self._scale), "Trimesh")
		else:
			putlog(NBLog.SPAM, 
			       "Object %s has uniform scale %f." % 
			       (self._name,self._scale), "Trimesh")
			self._scale = scalelist[0]
	def setTexture(self, texture):
		self._texture = texture
	def setTileFade(self, tilefade):
		self._tilefade= tilefade


	def setVerts(self, vertlist):
		self._verts = vertlist
	def _addFaceData(self, vert1, vert2, vert3, uv1, uv2, uv3, smooth):
		# This is probably unnecessary, but we're very paranoid.
		if smooth:
			smooth = 1
		else:
			smooth = 0

		# Construct the data.
		currface = map(self._verts.index, (vert1,vert2,vert3))
		currface.extend([smooth, uv1, uv2, uv3])
		self._faces.append(currface)
	def addTexVert(self, uv):
		"""Adds a texture vertex to the _texverts if not there already.
		returns index to the added item (or item already on list)."""
		try:
			return self._texverts.index(uv)
		except ValueError:
			self._texverts.append(uv)
			return len(self._texverts)-1

	def _addTriangleFace(self,f):
		"""Takes a triangle NMFace and puts its information
		to a Trimesh."""
		assert len(f.v) == 3
		# Face corner vertices and UV coordinates.
		# These are all tuples.
		v1, v2, v3 = f.v
		if self._texture:
			u1, u2, u3 = f.uv
			
		# Store UV coordinates to the list.
		# We get their indexes from tvertlist.
		if self._texture:
			(u1i, u2i, u3i) = (self.addTexVert(u1),
				self.addTexVert(u2),
				self.addTexVert(u3))
		else:
			(u1i, u2i, u3i) = (0,0,0)
		# Store face to the face list.
		self._addFaceData(v1, v2, v3, u1i, u2i, u3i, f.smooth)

	def _addQuadFace(self, f):
		"""Takes a quad NMFace and puts its information
		to a Trimesh."""
		assert len(f.v) == 4
		# This is same as the triangle case, except that it does
		# two triangles, (v1,v2,v3) and (v3, v4, v1), with uv
		# coordinates handled with care.
		v1, v2, v3, v4 = f.v
		if self._texture:
			u1, u2, u3, u4 = f.uv
			u1i, u2i, u3i, u4i = (self.addTexVert(u1),
				self.addTexVert(u2),
				self.addTexVert(u3),
				self.addTexVert(u4))
		else:
			(u1i, u2i, u3i, u4i) = (0,0,0,0)
		self._addFaceData(v1, v2, v3, u1i, u2i, u3i, f.smooth)
		self._addFaceData(v3, v4, v1, u3i, u4i, u1i, f.smooth)
	

	def addFace(self, f):
		"""Takes a NMFace and puts its information to Trimesh."""
		# reminder: f is of type NMFace (NMesh Face).
		verts = len(f.v)
		if verts < 2:
			putlog(NBLog.WARNING, 
			       "Found a face with one or " +
			       "less vertices. I'd call that patently " +
			       "ridiculous.", "Trimesh")
		if verts == 2:
			putlog(NBLog.WARNING, 
			       "Object has a face has 2 vertices." +
			       "That's an odd one! It won't be added.",
			       "Trimesh")
		elif verts == 3:
			self._addTriangleFace(f)
		elif verts == 4:
			self._addQuadFace(f)
		else:
			putlog(NBLog.WARNING, 
			       "Can't add face with %d verts! " +
			       "You need to divide this face manually."
			       % verts, "Trimesh")

	def __str__(self):
		o = ("node trimesh %s\n" % self._name) + \
			("  parent %s\n" % self._parent) + \
			("  wirecolor %f %f %f\n" % tuple(self._wirecolor)) + \
			("  ambient %f %f %f\n" % tuple(self._ambient)) + \
			("  diffuse %f %f %f\n" % tuple(self._diffuse)) + \
			("  specular %f %f %f\n" % tuple(self._specular)) + \
			("  shininess %f\n" % self._shininess) + \
			("  position %f %f %f\n" % tuple(self._position)) + \
			self._orientation_as_string() + \
			("  scale %f\n" % self._scale) + \
			self._texture_as_string() + \
			self._verts_as_string() + \
			self._faces_as_string() + \
			self._texverts_as_string() + \
			"endnode\n"
		return o
	def _orientation_as_string(self):
		o = self._orientation
		if o[0]==0.0 and o[1]==0.0 and o[2]==0.0:
			return ""
		return "  orientation %f %f %f %f\n" % \
		       euler2nwn(self._orientation)
	def _texture_as_string(self):
		if self._texture:
			return "  bitmap %s\n" % self._texture
		return "  # No texture\n"
	def _verts_as_string(self):
		o = ("  verts %d\n" % len(self._verts))
		o+= ''.join(map(lambda v: "    %f %f %f\n" % tuple(v),
			self._verts))
		return o
	def _faces_as_string(self):
		o = ("  faces %d\n" % len(self._faces))
		o += join(map(
			lambda f: "    %d %d %d %d %d %d %d 1\n" % tuple(f),
			self._faces))
		return o
	def _texverts_as_string(self):
		if self._texture:
			o = ("  tverts %d\n" % len(self._texverts))
			o += join(map(lambda tv: "    %f %f 0\n" % tuple(tv),
				     self._texverts))
		else:
			o = "  tverts 1\n    0 0 0\n"
		return o
	
	def stat(self):
		"""Returns a 3-element tuple that has count of data in
		the trimesh: count of vertices, faces and texverts,
		respectively."""
		stat = ( len(self._verts), \
			 len(self._faces), \
			 len(self._texverts) )
		return stat
