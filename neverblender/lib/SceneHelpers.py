#################################################################
#
# SceneHelpers.py
# Finding items from the scene. Helpers. I suppose.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import string
from string import split
import Blender
from Blender import Ipo
import NBLog
from NBLog import putlog


def scenechildren(scene):
	"Builds a hash of the children of each object's children."
	r = dict()
	objs = scene.getChildren();
	for obj in objs:
		parent = obj.getParent()
		if parent:
			try:
				r[parent.name].append(obj.name)
			except KeyError:
				r[parent.name] = [obj.name]
	return r

def uniq(list):
	"Finds all unique elements of list."
	x = dict()
	for i in list:
		x[i] = 1
	return x.keys()

# What an unbearable swamp of savages this Python be...
# there's map but no grep... or is there?
def grep(f, l):
	"Returns a list of elements from l where function f is true."
	if not l or l == None or l == []:
		return []
	results = map(f, l)
	found = []
	for res in range(len(results)):
		if results[res]:
			found.append(l[res])
	return found

# There's probably a global list of these things somewhere. Nobody
# told me where. So I did this the hard way. (Where's my Blender.Action?)
def actionlist():
	"Returns a list of actions in the scene."
	ipos = Ipo.Get()
	iponames = map(lambda x: x.getName(), ipos)
	iporoots = uniq(map(lambda x: split(x, '.')[0], iponames))
	iporoots = grep(lambda x: x != 'ObIpo', iporoots)
	return iporoots


# Returns index of "what" on the list "list".
def atwhatpoint(list,what):
	try:
		return list.index(what)
	except ValueError:
		return -1

# Finds triangle's vertices "v1","v2","v3" from vertex (tuple) list "list".
# Returns list.
def findtriangleverts(list,v1,v2,v3):
	return [ atwhatpoint(list,v1),
		atwhatpoint(list,v2),
		atwhatpoint(list,v3) ]

