#################################################################
#
# Dummy.py
# A class for easy manipulation of Bioware Dummy objects.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

class Dummy:
	Name = "untitleddummy"
	Parent = "NULL"
	Position = [0.0, 0.0, 0.0]
	Orientation = [0.0, 0.0, 0.0, 0.0]

	# The arsenal is bloody narrow due to the fact that I
	# just discovered this advanced programming language
	# doesn't have this "method overloading" stuff.
	def setName(self, name):
		self.Name = name
	def setParent(self, parent):
		self.Parent = parent
	
	def setPosition(self, loclist):
		self.Position = loclist
	def setOrientation(self, poslist):
		self.Orientation = poslist
	
	def __str__(self):
		o = "node dummy %s\n" % self.Name + \
			"  parent %s\n" % self.Parent + \
			"  position %f %f %f\n" % tuple(self.Position) + \
			"  orientation %f %f %f %f\n" % tuple(self.Orientation) + \
			"endnode\n"
		return o


