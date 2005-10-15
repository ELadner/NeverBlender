#################################################################
#
# Geometry.py
# Handle conversion of various Blender geometry into MDL format.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import Blender
import Blender.Scene

from Trimesh import Trimesh

BuildChildrenDictionary()

def GetTree(root, parent="NULL"):
	"""Return a list of all Geometry objects (instantiated from the
	correct subclass including and descending from the given root
	object."""

	tree = [GetGeometry(root, parent)]
	i = 0
	while (i < len(tree)):
		tree[i:i] = tree[i].GetChildren()

GeometryHandlers = dict()
def RegisterGeometry(kind, handler):
	"Register a subclass of Geometry for handling the specified 'kind' of Blender object."
	
	GeometryHandlers[kind] = handler

def GetGeometry(obj, parent="NULL"):
	"""
	Instantiate the appropriate Geometry subclass for the given
	Blender object.  If no appropriate subclass is registered then we
	use Geometry itself by default.
	"""
	# Should this do some sort of type-checking?
	return GeometryHandlers.get(obj.getType(), Geometry)(obj, parent)

class Geometry(object):
	Type = 'dummy'
	
	def __init__(self, obj, parent="NULL"):
		self.BlenderObject = obj
		self.Parent = parent

	def GetChildren(self):
		name = self.BlenderObject.getName()
		return map(lambda x: GetGeometry(x, name),
				   Geometry.children[name])

	children = {}
	for kid in Blender.Scene.GetCurrent().getChildren():
		parent = kid.getParent()
		if parent is None: continue
		else: children.setdefault(parent.getName(), []).append(kid)

	def __str__(self):
		"Serialize the object's geometry"
		return "node %(Type)s %(Name)s\n" % self.__dict__ \
			   + self.Details() \
			   + "endnode"

	def Details(self):
		"Serialize basic properties that all geometry should have."
		return ("parent %s\n" % self.Parent	+
				"position %s\n" % self.FormatPosition() +
				"orientation %s\n" % self.FormatOrientation())

	def FormatPosition(self):
		return "%f %f %f" % self.BlenderObject.getLocation()

	def FormatOrientation(self):
		quat = self.BlenderObject.getEuler().toQuat()
		return "%f %f %f %f" % tuple(list(quat.axis) + [quat.angle])

RegisterGeometry('Empty', Geometry)
RegisterGeometry('Armature', Geometry) # for now
RegisterGeometry('Mesh', Trimesh) # for now
