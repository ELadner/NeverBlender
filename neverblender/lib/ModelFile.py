#################################################################
#
# ModelFile.py
# Class for writing stuff to a model file.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import Props
import os
import os.path
from os import fsync, remove
from os.path import normpath, join, exists
from time import asctime
import NBLog
from NBLog import putlog
from Model import Model

class ModelFile(Model):

	def __init__(self, name="unnamedmodel", classification="Item",
				 fileformat="mdl", *pargs, **kargs):

		super(ModelFile, self).__init__(name, classification, *pargs, **kargs)

		self.FileDependancy = "NULL"
		self.FileFormat = fileformat
		self.OutputDirectory = None

	def writeToFile(self):
		"""
		The actual work of exporting Blender data to MDL data is done
		in the Model superclass.  Here we just deal with getting the
		string given to us by Model into a file.  This really should
		know virtually nothing about the MDL format and absolutely
		nothing about Blender.
		"""
		
		odir = self.OutputDirectory or Props.getoutputdirectory()
		ofile = self.Name + '.' + self.FileFormat
		outfile = normpath(join(odir,ofile))

		if exists(outfile):
			# Delete existing file
			try:
				remove(outfile)
			except:
				putlog(NBLog.WARNING, 
					   "Couldn't remove existing file %s." +
					   "Can only hope we'll clobber it properly now..."
					   % outfile, "File")

		of = file(outfile, "w")
		putlog(NBLog.INFO, 
			   "Writing '%s' to file %s." % (self.Name,
											 outfile), "File")

		of.write("""\
# Model written by NeverBlender MDL Export Script
# File name: %s
# Built on: %s
filedependancy %s
""" % (outfile, asctime(), self.FileDependancy))

		# The conversion of a model to a string is defined in the Model class
		of.write(str(self))

		# "...and STAY down!!!" - Warrior, Myth III
		# FIXME: Apparently sometimes the file doesn't close properly?
		of.flush()
		fsync(of.fileno())
		of.close()
		of = 0

	# Here's a bunch of accessors to provide backward compatibility
	# New code should just use the properties directly - we can use
	# descriptors if we want to control access.  Eventually I'd like
	# to see these dissapear entirely, but for now I'll be kind and
	# leave them here.
	def setModelName(self,modelname=None):
		if modelname:
			self.Name = modelname
		return self.Name
	getModelName=setModelName
	def setSuperModelName(self,supermodelname):
		self.SuperModel = supermodelname
	def getSuperModelName(self):
		return self.SuperModel
	def setAnimationScale(self,animationscale):
		self.AnimationScale = animationscale
	def getAnimationScale(self):
		return self.AnimationScale
	def setFileFormat(self,format):
		self.FileFormat = format
	def getFileFormat(self):
		return self.FileFormat
	def setFileDependancy(self,filename):
		self.FileDependancy = filename
	def getFileDependancy(self):
		return self.FileDependancy
