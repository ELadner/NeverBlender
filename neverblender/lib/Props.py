#################################################################
#
# Props.py
# Module for parsing configuration from Blender 'nwnprops' text block.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$ 
#
#################################################################

import os
from Blender import Text, Object

## Parsing nwnprops and utility funcs for getting the values.

# Parse the NWN scene props text.
# This would be really easy if only Windows Blender had
# 're' module...
nwnprops = {}
def parse():
	proptxt = Text.get('nwnprops')
	if not proptxt:
		print "*** Unable to find the configuration ('nwnprops'.) "+\
		      "Using defaults..."
		return
	print "*** Found configuration, parsing."
	lines = proptxt.asLines()
	for l in lines:
		# Ignore comment lines and empty lines.
		if len(l) == 0:
			continue
		if l[0] == '#':
			continue
		# Find the separators.
		try:
			objectsep=l.index('.')
			valuesep=l.index('=', objectsep)
		except ValueError:
			print "*** Ignoring following conf entry (invalid format):"
			print l
			continue
		object = l[0:objectsep]
		property = l[objectsep+1:valuesep]
		value = l[valuesep+1:]
		if not nwnprops.has_key(object):
			nwnprops[object] = {}
		nwnprops[object][property] = value

# Generic function for getting stuff from nwnprops. If there's no value,
# it returns the "undef" value.
def getValue(object,property,undef=None):
	try:
		return nwnprops[object][property]
	except KeyError:
		return undef

# Scene properties

# Gets the "base object" name. This should be an Empty which is linked to
# the actual object meshes.
def getbaseobjectname():
	v = getValue('SCENE','baseobjectname')
	if v:
		return v
	else:
		# If there's no property, the base object is the active one.
		# Better get that right, then, my dear user.
		sel = Object.getSelected()
		return sel[0].name

# Gets the output directory.
def getoutputdirectory():
	v = getValue('FILES','outputdirectory')
	if v:
		return v
	else:
		# None selected? Let's get it from the system.
		return os.getcwd()
		# If there's no property, the base object is the active one.
		# Better get that right, then, my dear user.
		sel = Object.getSelected()
		return sel[0].name

# Returns the model classification.
# Can be 'Character', 'Tile', 'Effects' or 'Item'.
# Default: 'Item'.
def getclassification():
	return getValue('SCENE','classification','Item')

# Gets supermodel.
def getsupermodel():
	return getValue('SCENE','supermodel')

# Gets the PWK.
def getpwk():
	return getValue('SCENE','pwkobjectname')

# Gets the animation to get the geometry from.
def getgeometry():
	return getValue('SCENE','geometry')

# Object properties

# Finds a texture name for the object from the nwnprops.
def getobjecttex(objname):
	return getValue(objname,'texture')

# Finds tile fade for the object from the nwnprops.
def getobjecttilefade(objname):
	# Hash lookups are faster, and often easier.
	tilefadetypes={'None': 0, 'Fade': 1, 'HBlock': 2, 'VBlock': 3}
	v = getValue(objname,'tilefade','None')
	return tilefadetypes[v]
