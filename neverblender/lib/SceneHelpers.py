#################################################################
#
# SceneHelpers.py
# Finding items from the scene. Helpers. I suppose.
#
# part of the NeverBlender project
# (c) Urpo Lankinen 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice. No warranty expressed or implied.
# $Id$
#
#################################################################

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

