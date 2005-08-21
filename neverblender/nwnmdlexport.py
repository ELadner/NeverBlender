#!BPY
""" Registration info for Blender menus
Name:    'Bioware NWN, ASCII (.mdl)...'
Blender: 233
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

print "Warning: Python brain damage: No way to figure out current file (cannot fix)" + "\n"

# Now, let's get back to our regular every-day library requesting.
import Blender
from Blender import Scene, Object, Armature
from Blender.Armature import NLA

import Props
import SceneHelpers
import NBLog
from NBLog import openlogfile, closelogfile, putlog
from ModelFile import ModelFile
from Dummy import Dummy
from Trimesh import Trimesh
from Animation import Animation, AnimationNode

from string import join
from re import match

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

# Get properties from the 'nwnprops' text.
Props.parse()

# Get logging.
logfile = Props.getlogfile()
if logfile:
	openlogfile(logfile)

# Some banner stuff right here...
putlog(NBLog.SPAM, "NeverBlender Blender->MDL export script")
putlog(NBLog.SPAM, "by Urpo Lankinen, 2003")

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


# Mess around with Animations
# (Note: doc says GetActions returns a  "PyList", but in fact, it's a dict.
# Blender has some funny nomenclature.)
# (Also, it's not getAllChannelIpo(), it's getAllChannelIpos().)
# The 2.33 Action API rules. Docs have typos though. =)
mfile._animations = []

actions = NLA.GetActions()

arms = Armature.Get()
#for a in arms:
#	putlog(NBLog.DEBUG,
#	       "Armature %s bones %s, children %s"
#	       % (a, str(a.getBones()), scnobjchilds[a.getName()]))

#test = Object.Get('cone2')
#p = test.getParent();
#putlog(NBLog.DEBUG, "cone2 is parented to %s" % p.getName())

#putlog(NBLog.DEBUG, "Actionlist: %s" % repr(actions))
for a in actions:

	# Let's skip this animation bullshit. (For those who just
	# checked out the code and can't get the bloody thing to
	# work!)
	continue
	
	bonemap = Props.getanimbonemap(a)
	
	# FIXME: if action in props.whatever.don't-do-this: next
	
	putlog(NBLog.INFO, "Processing animation %s" % a)
	action = actions[a]

	ipos = action.getAllChannelIpos()
	putlog(NBLog.DEBUG, "BoneIpos: %s" % ipos.keys())
	# NOTE: Channel names != bone names. Fuck.

	anim = Animation()
	anim.setName(a)
	anim.setModelName(model)

	# Note: we're iterating Bones instead of Objects.
	# Thus, the goddamn Objects have to have same name as
	# their controlling Bones. (NOTE: this comment has no bearing
	# whatsoever to the reality. Reality is MUCH WORSE.)
	for boneipo in ipos:
		anode = AnimationNode()
		
		# The Theory: Now we're fucking with the Ipo channel here.
		# We figure out what object the channel corresponds to.
		# (that seems to be the REALLY DAMN DIFFICULT part right now.)
		# Then, we just eval the ipo on keyframes OR at set intervals
		# (depending on what mode we're working on)
		# and stick those in the Animation's OrientationList and
		# PositionList. Which is even easier because orientations
		# are stored in Blender in quaternions already in this case.
		# And now: How the FUCK do we figure out what object the
		# damn ipo moves?
		
		anode.setName(boneipo) # WRONG! DEAD WRONG!

		print "Getting %s\n" % bone
		aob = Object.Get(bone)
		# That dies because the fucking animation channel names
		# do NOT correspond with the fucking bone names and there's
		# NO fucking way to find 'em out. (brought to you by Amuse the Greppers, inc)
		aobtype = aob.getType()
		if aobtype == 'Empty':
			anode.setType('dummy')
		elif aobtype == 'Mesh':
			anode.setType('trimesh')
		else:
			putlog(NBLog.WARNING,
			       "%s is unknown object type (%s), assuming dummy"
			       % (aob, aobtype))
			anode.setType('dummy')		

		# Insert code that actually does something with the
		# channel Ipos here.

		anim.addNode(anode)

	# Set the animation length. Obviously, this is a bogus value
	# for now.
	anim.setLength(1.0)

	mfile.addAnimation(anim)

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

if logfile:
	closelogfile()
	putlog(NBLog.INFO, "Log file written to %s" % logfile)
else:
	print("Logfile: %s\n" % logfile)
