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

from Blender import Scene, Object

import Props
import SceneHelpers
from ModelFile import ModelFile
from Dummy import Dummy
from Trimesh import Trimesh


#################################################################

def processobject(sobj, details):
	"""Process the Object named sobj and return a Trimesh. If
	details is true, also generates texture and such, otherwise
	just location, scale and orientation."""

	# Get the Object block of the current object.
	obj = Object.Get(sobj)
	print " ** Processing %s (%s)" % (sobj, obj.getType())
	if obj.getType() != 'Mesh':
		print " ** Can only deal with meshes!"
		return

	# get the Mesh block of the Object.
	mesh = obj.getData()
	if not mesh:
		print "  * Can't get the corresponding mesh. This is strange!"
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
			print "  * Object has material(s)."
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
	print "  * Done: %d vertices, %d faces, %d texverts" % trimesh.stat()
	return trimesh

#################################################################

print "*** NeverBlender Blender->MDL export script"
print "*** by Urpo Lankinen, 2003"

# Get properties from the 'nwnprops' text.
Props.parse()

# Get the scene, and figure out which objects are whose children.
scn = Scene.getCurrent()
scnobjchilds = SceneHelpers.scenechildren(scn)

# Get the base object name.
model = Props.getbaseobjectname()
print "*** Base object: %s" % model
# Some sanity checking...
if not scnobjchilds.has_key(model):
	print " ** Error: %s doesn't exist." % model
	exit
if len(scnobjchilds[model]) <= 0:
	print " ** Error: %s has no sibling objects." % model
	exit
print "*** Meshes to be included in the object: ", scnobjchilds[model]

# Let's open the file.
mfile = ModelFile()
mfile.setModelName(model)
mfile.setClassification(Props.getclassification())

# Supermodel?
supermodel = Props.getsupermodel()
if supermodel != 0:
	print "*** Super model: %s" % supermodel
	mfile.setSuperModelName(supermodel)

# The base object.
base = Dummy()
base.setName(model)
baseobj = Object.Get(model)
baseobjloc = baseobj.getLocation()
base.setPosition(baseobjloc)

mfile.addObject(base)

# Process each child of the baseobj...
for sobj in scnobjchilds[model]:
	trimesh = processobject(sobj, 1)
	mfile.addObject(trimesh)

# Write the object to file.
mfile.writeToFile()

# Create PWKs.
pwkname = Props.getpwk()
if pwkname:
	print "*** Creating placeable walk data (PWK file)"

	pwkobj = Object.Get(pwkname)
	if pwkobj.getType() != 'Mesh':
		print " ** PWK must be a Mesh!"
	else:
		pwkfile = ModelFile()
		
		# Set the name and type
		pwkfile.setModelName(model)
		pwkfile.setFileFormat('pwk')

		pwkmesh = processobject(pwkname, 0)

		pwkfile._objects = []
		pwkfile.addObject(pwkmesh)

		# Write out the PWK.
		pwkfile.writeToFile()

