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
	_name = "untitleddummy"
	_parent = "NULL"
	_position = [0.0, 0.0, 0.0]
	_orientation = [0.0, 0.0, 0.0, 0.0]

	# The arsenal is bloody narrow due to the fact that I
	# just discovered this advanced programming language
	# doesn't have this "method overloading" stuff.
	def setName(self, name):
		self._name = name
	def setParent(self, parent):
		self._parent = parent
	
	def setPosition(self, loclist):
		self._position = loclist
	def setOrientation(self, poslist):
		self._position = poslist
	
	def __str__(self):
		o = "node dummy %s\n" % self._name + \
			"  parent %s\n" % self._parent + \
			"  position %f %f %f\n" % tuple(self._position) + \
			"  orientation %f %f %f %f\n" % tuple(self._orientation) + \
			"endnode\n"
		return o


