#################################################################
#
# Model.py
# Class for serializing a model.
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
from NBLog import putlog

template = """
newmodel %(Name)s
%(Options)s
classification %(Classification)s
  
beginmodelgeom %(Name)s
%(Geometry)s
endmodelgeom %(Name)s

%(Animations)s

donemodel %(Name)s
"""

class Model(object):

	def __init__(self, name=None, classification="Item",
				 supermodel=None, objects=[], animationscale=1.0,
				 animations=[], options=[]):
		self.Name = name
		self.Classification = classification
		self.Options = options
		self.SuperModel = supermodel
		self.AnimationScale = animationscale
		self.Walkmesh = None
		self._objects = objects
		self._animations = animations

	def setClassification(self,classification):
		if not classification in ['Character', 'Tile', 'Effects', 'Item']:
			putlog(NBLog.WARNING, 
				   "Unknown classification \"%s\", assuming \"Item\"."
				   % classification, "File")
			self._classification = 'Item'
		else:
			self._classification = classification
	def getClassification(self):
		return self._classification
	Classification = property(getClassification, setClassification)

	"""
	Objects and animations should be serializable objects.  Objects
	will be placed in the 'geometry' section, while animations will be
	placed after the 'geometry' section.
	"""
	def addObject(self,object):
		self._objects.append(object)
	def addObjects(self, objects):
		self._objects += objects

	def addAnimation(self,animation):
		self._animations.append(animation)

	def addOption(self, option):
		"""
		Options are just text to be placed at the beginning of the
		model body.  Interpolation of Model properties is done on
		options for your convenience.
		"""
		self.Options.append(option)
	
	def __str__(self):
		"""
		Here is where we actually serialize the model.  Most of this
		code is setting up properties on the Model object for
		interpolation with the 'template' defined at the top of this
		file.  Fairly few changes should ever be made to this method
		itself.  Most changes in formatting, etc should be made to the
		template.
		"""

		props = dict(map(lambda x: (x, getattr(self, x)),
						 ['Name', 'Classification', 'Options']))
		
		props['Geometry'] = '\n'.join(map(str, self._objects)) or "# No geometry???"
		NBLog.putlog(NBLog.INFO, "Total %d objects\n" % len(self._objects), "Model")
		if len(self._objects) == 0:
			NBLog.putlog(NBLog.WARNING, "...did I say no objects????\n", "Model")
		
		props['Animations'] = '\n'.join(map(str, self._animations)) or "# No animations"
		NBLog.putlog(NBLog.INFO, "Total %d animations\n" % len(self._animations), "Model")

		if self.SuperModel:
			props['Options'].append("setsupermodel %s %s" % (self.Name, self.SuperModel))
		if self.Classification in ['Character', 'Effects']:
			props['Options'].append("setanimationscale %s" % self.AnimationScale)
		
		props['Options'] = '\n'.join(props['Options']) % props

		return template % props
