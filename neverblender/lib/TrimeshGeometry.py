#################################################################
#
# TrimeshGeometry.py
# A class for easy manipulation of Bioware Trimesh objects.  This will
# eventually replace Trimesh.py.  It derives Trimesh from Geometry.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import NBLog
from Geometry import Geometry, RegisterGeometry
from NMesh import NMesh

class Trimesh(Geometry):
	Type = 'trimesh'

	# TODO: Figure out what to do with these.  Probably should come
	# from the first material on the mesh, assuming it has one.
	# Furthermore, do we set these in __init__, let them be set
	# elsewhere, or give them property descriptors that retrieve them
	# directly from the object?
	Wirecolor = (0.6, 0.6, 0.6)
	Ambient = (1.0, 1.0, 1.0)
	Diffuse = (1.0, 1.0, 1.0)
	Specular = (1.0, 1.0, 1.0)
	Shininess = 0.25

	Texture = None

	
	def __init__(self, obj=None, parent="NULL"):
		super(Trimesh, self).__init__(obj, parent)
		if obj:
			assert obj.getType() == 'Mesh'
			self.ProcessMesh()
		else:
			NBLog.putlog(NBLog.WARNING, "Eh?  A trimesh that doesn't exist?", "Trimesh")
			# What do we want to do in this case?  The reason I
			# include it at all is it could be useful if we ever
			# decide to integrate the importer and exporter.  Also the
			# older nwnmdlexport code seems to want to do this and
			# then set the mesh later.

	def Details(self):
		return (super(Trimesh, self).Details() +
				"  scale %f\n" % self.Scale +
				self.FormatMaterial() +
				self.FormatTexture() +
				self.FormatVertices() +
				self.FormatFaces() +
				self.FormatTexverts())

	def FormatMaterial(self):
		return ("  wirecolor %f %f %f\n" % self.Wirecolor +
				"  ambient %f %f %f\n" % self.Ambient +
				"  diffuse %f %f %f\n" % self.Diffuse +
				"  specular %f %f %f\n" % self.Specular +
				"  shininess %f\n" % self.Shininess)

	def FormatTexture(self):
		if self.Texture:
			return "  bitmap %s\n" % self.Texture
		else:
			return "  # No texture\n"

	def FormatVertices(self):
		verts = map(tuple, self._verts)
		return ("  verts %d\n" % len(verts) +
				''.join(map(lambda v: "    %f %f %f\n" % v,
							verts))
				)
	def FormatFaces(self):
		faces = map(tuple, self._faces)
		return ("  faces %d\n" % len(faces) +
				''.join(map(lambda f: "    %f %f %f %f %f %f %f 1\n" % f,
							faces))
				)
	def FormatTexverts(self):
		if self.Texture:
			texverts = map(tuple, self._texverts)
			return ("  tverts %d\n" % len(texverts) +
					''.join(map(lambda tv: "    %f %f 0\n" % tv,
								texverts))
					)
		else:
			return "  tverts 1\n    0 0 0\n"

	# A lot of the code below this point is taken almost verbatim from
	# Urpo's original Trimesh code.  Some of it should be fixed up to
	# be more Pythonish in style, but this kind of wrangling is an
	# inherently messy process and it works fine as is, so maybe it's
	# best left alone.  Perhaps we want to move it into some helper
	# module where we hide away our dirty little secrets?

	def SetMesh(self, mesh):
		"""
		Here we actually extract and process the mesh data, massaging
		it into an intermediate form before actually dumping it into
		MDL.
		"""
		assert isinstance(mesh, NMesh) # A mesh that isn't a mesh?  Let's hope not.
		self._mesh = mesh

		self._verts = self._mesh._verts
		for face in (self._mesh.faces):
			self._addFace(face) # Hurrah for delegation!
		
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

	def _addTexVert(self, uv):
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
	

	def _addFace(self, f):
		"""Takes a NMFace and puts its information to Trimesh."""
		# reminder: f is of type NMFace (NMesh Face).
		verts = len(f.v)
		if verts == 3:
			self._addTriangleFace(f)
		elif verts == 4:
			self._addQuadFace(f)
		else:
			putlog(NBLog.WARNING, 
			       "Wierd!  This face has %d verts!  " % verts +
				   "I'm going to pretend I didn't see that, but you might want to fix it.",
				   "Trimesh")


RegisterGeometry('Mesh', Trimesh)
