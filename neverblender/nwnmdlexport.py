#!BPY
""" Registration info for Blender menus
Name:    'Bioware NWN ASCII MDL'
Blender: 232
Group:   'Export'
Tip:     'Export in Neverwinter Nights format ASCII model'
"""
#################################################################
#
# nwnmdlexport.py
# Neverwinter Nights ASCII .mdl export script for Blender.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################


# This is a severely ugly hack to get the path access working
# in a sane way. Goddamn Blender won't honor the Ordinary Python
# Library Path.
from sys import path
from os import access, X_OK
if access("/usr/local/lib/neverblender/lib", X_OK) == 1:
	path.append("/usr/local/lib/neverblender/lib")

# Now, let's get back to our regular every-day library requesting.
import Blender
from Blender import Scene, Object

import Props
import SceneHelpers
import NBLog
from NBLog import putlog
from ModelFile import ModelFile
from Dummy import Dummy
from Trimesh import Trimesh

from string import join

#################################################################

# The base object.
def processdummy(model,parent):
	d = Object.Get(model)
	dt = d.getType()
	putlog(NBLog.INFO, "Processing %s (%s)" % (model, dt))
	if dt != 'Empty':
		putlog(NBLog.CRITICAL,
		       "Internal error: Can't process this type here!")
		return
	dummy = Dummy()
	if parent != "NULL":
		dummy.setParent(parent)
	dummy.setName(model)
	dummyloc = d.getLocation()
	dummy.setPosition(dummyloc)
	return dummy

def processtrimesh(sobj, parent, details):
	"""Process the Object named sobj and return a Trimesh. If
	details is true, also generates texture and such, otherwise
	just location, scale and orientation."""

	# Get the Object block of the current object.
	obj = Object.Get(sobj)
	putlog(NBLog.INFO,
	       "Processing %s (%s)" % (sobj, obj.getType()))
	if obj.getType() != 'Mesh':
		putlog(NBLog.CRITICAL,
		       "Internal error: can only deal with meshes!")
		return

	# get the Mesh block of the Object.
	mesh = obj.getData()
	if not mesh:
		putlog(NBLog.CRITICAL,
		       "Can't get the corresponding mesh. This is strange!")
		return

	# Create a new Trimesh to be output.
	trimesh = Trimesh()
	trimesh.setParent(model)
	trimesh.setName(sobj)

	# Get the object's information.

	# Location.
	objloc = obj.getLocation()
	trimesh.setPosition(objloc)

	# Rotation
	r = obj.getEuler()
	trimesh.setOrientation(r)

	# Scaling.
	s = obj.size           # Is there a getter for this? Goddamnit.
	trimesh.setScale(s)

	if details:
		# Materials.
		objmats = obj.getMaterials()
		if len(objmats)>=1:
			putlog(NBLog.SPAM,
			       "Object has material(s).")
			# We only take the first material, for now.
			# (We'll do something more elegant later on...)
			m = objmats[0]
			trimesh.setWireColor(m.rgbCol)
			trimesh.setSpecularColor(m.specCol)
		
		# Texture
		texture = Props.getobjecttex(sobj)
		trimesh.setTexture(texture)
		
		# Tilefade
		tilefade = Props.getobjecttilefade(sobj)
		trimesh.setTileFade(tilefade)

	# Get vertex list
	trimesh.setVerts(mesh.verts)
	# Get each Face (and Texvert).
	for f in mesh.faces:
		trimesh.addFace(f)
	# Then return it.
	putlog(NBLog.INFO,
	       "Done: %d vertices, %d faces, %d texverts" % trimesh.stat())
	return trimesh

# For processing object tree recursively.
def processobject(model,parent,mfile):
	global scnobjchilds

	# Process this object
	#putlog(NBLog.DEBUG, "Processing object %s" % model)

	thismod = Object.Get(model)
	mtype = thismod.getType()
	if mtype == 'Empty':
		dummy = processdummy(model, parent)
		mfile.addObject(dummy)
	elif mtype == 'Mesh':
		# FIXME: Parent
		trimesh = processtrimesh(model, parent, 1)
		mfile.addObject(trimesh)
	elif mtype == 'Armature':
		# Special code to handle armature: We process the armature's
		# children "by hand" to make them parent to the armature's
		# parent instead of the armature.
		try:
			childs = scnobjchilds[model]
			putlog(NBLog.DEBUG,
			       "%s armature children: %s" % (model,
						       join(childs, ", ")))
			for mchild in childs:
				processobject(mchild,parent,mfile)
			return
		except KeyError:
			return
	else:
		putlog(NBLog.CRITICAL,
		       "Can't handle object of type %s" % mtype)
	# Process the children
	try:
		children = scnobjchilds[model]
	except KeyError:
		return
	processdownfrom(model,mfile)

def processdownfrom(model,mfile):
	childs = scnobjchilds[model]
	putlog(NBLog.INFO,
	       "%s children: %s" % (model, join(childs, ", ")))

	for mchild in childs:
		processobject(mchild,model,mfile)

#################################################################

putlog(NBLog.SPAM, "NeverBlender Blender->MDL export script")
putlog(NBLog.SPAM, "*** by Urpo Lankinen, 2003")

# Get properties from the 'nwnprops' text.
Props.parse()

# Get the scene, and figure out which objects are whose children.
geometry = Props.getgeometry()
if(not geometry):
	scn = Scene.getCurrent()
else:
	putlog(NBLog.INFO, "Getting geometry from %s" % geometry)
	scn = Scene.Get(geometry)
	if(not scn):
		putlog(NBLog.CRITICAL,
		       "Error: Can't find the scene with the geometry.")
		exit
scnobjchilds = SceneHelpers.scenechildren(scn)

# Get the base object name.
model = Props.getbaseobjectname()
putlog(NBLog.INFO, "Base object: %s" % model)
# Some sanity checking...
if not scnobjchilds.has_key(model):
	putlog(NBLog.CRITICAL, 
	       "%s doesn't exist." % model)
	exit
if len(scnobjchilds[model]) <= 0:
	putlog(NBLog.CRITICAL, 
	       "the base object %s has no sibling objects." % model)
	exit

# Let's open the file.
mfile = ModelFile()
mfile.setModelName(model)
mfile.setClassification(Props.getclassification())
mfile.setFileDependancy(Blender.Get('filename'))

# Supermodel?
supermodel = Props.getsupermodel()
if supermodel != None:
	putlog(NBLog.INFO, 
	       "Super model: %s" % supermodel)
	mfile.setSuperModelName(supermodel)
	
# Process each child of the baseobj...
mfile._objects = []
processobject(model,"NULL",mfile)

# Write the object to file.
mfile.writeToFile()

# Create PWKs.
pwkname = Props.getpwk()
if pwkname:
	putlog(NBLog.INFO, 
	       "Creating placeable walk data (PWK file)")

	pwkobj = Object.Get(pwkname)
	if pwkobj.getType() != 'Mesh':
		putlog(NBLog.CRITICAL, "PWK must be a Mesh!")
		exit

	pwkfile = ModelFile()
		
	# Set the name and type
	pwkfile.setModelName(model)
	pwkfile.setFileFormat('pwk')
		
	pwkmesh = processtrimesh(pwkname, "NULL", 0)

	pwkfile._objects = []
	pwkfile.addObject(pwkmesh)

	# Write out the PWK.
	pwkfile.writeToFile()

