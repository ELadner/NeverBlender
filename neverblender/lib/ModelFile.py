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

class ModelFile:
    #_modelname = "unnamedmodel"
    #_supermodelname = 0
    #_classification = 'Item'
    #_fileformat = 'mdl'
    #_objects = []

    def __init__(self, name="unnamedmodel", classification="Item",
                 fileformat="mdl", supermodel=None, objects=[],
                 animationscale=1.0, animations=[]):
        self._modelname = name
        self._supermodelname = supermodel
        self._animationscale = animationscale
        self._filedependancy = "NULL"
        self._classification = classification
        self._fileformat = fileformat
        self._objects = objects
        self._animations = animations

    def setModelName(self,modelname=None):
        if modelname:
          self._modelname = modelname
        return self._modelname
    getModelName=setModelName
    def setSuperModelName(self,supermodelname):
        self._supermodelname = supermodelname
    def getSuperModelName(self):
        return self._supermodelname
    def setClassification(self,classification):
        if classification != 'Character' and \
           classification != 'Tile' and \
           classification != 'Effects' and \
           classification != 'Item':
            putlog(NBLog.WARNING, 
                   "Unknown classification \"%s\", assuming \"Item\"."
                   % classification, "File")
            self._classification = 'Item'
        else:
            self._classification = classification
    def getClassification(self):
        return self._classification
    def setAnimationScale(self,animationscale):
        self._animationscale = animationscale
    def getAnimationScale(self):
        return self._animationscale
    def setFileFormat(self,format):
        self._fileformat = format
    def getFileFormat(self):
        return self._fileformat
    def setFileDependancy(self,filename):
        self._filedependancy = filename
    def getFileDependancy(self):
        return self._filedependancy

    def addObject(self,object):
        self._objects.append(object)

    def addAnimation(self,animation):
        self._animations.append(animation)
    
    def writeToFile(self):
        odir = Props.getoutputdirectory()
        ofile = self.getModelName() + '.' + self.getFileFormat()
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
               "Writing '%s' to file %s." % (self.getModelName(),
                                             outfile), "File")

        # Begin of model file.
        of.write("# Model written by NeverBlender MDL Export Script\n")
        of.write("# File name: %s\n" % outfile)
        of.write("# Built on: %s\n" % asctime())
        of.write("filedependancy %s\n" % self.getFileDependancy())
        of.write("newmodel %s\n"  % self.getModelName())
        # FIXME: Any way to get the current .blend file name? Would rule.

        # Model parameters =====

        # FIXME: Supermodelling in general is Not Tested. Reports appreciated.
        if self.getSuperModelName():
            of.write("setsupermodel %s %s\n" % (self.getModelName(),
                                                self.getSuperModelName()))
        of.write("classification %s\n" % self.getClassification())

        if self.getClassification() == 'Character' or \
           self.getClassification() == 'Effect':
            of.write("setanimationscale %f\n" % self.getAnimationScale())

        # Model's scene graph =====
        of.write("beginmodelgeom %s\n" % self.getModelName())

        putlog(NBLog.INFO,
               "Total %d objects" % len(self._objects), "File")
        if len(self._objects) == 0:
            putlog(NBLog.WARNING, 
                   "...hrm, did I just say 0 objects?", "File")
            of.write("# No objects?\n");
        else:
            for obj in self._objects:
                objtxt = str(obj)
                if objtxt != "None":
                    of.write(objtxt)
                else:
                    putlog(NBLog.CRITICAL, 
                           "Internal error: Couldn't serialize an object",
                           "File")
                    of.write("# Excuse me, some interpretive problem...")

        of.write("endmodelgeom %s\n" % self.getModelName())

        # Model's animations =====

        putlog(NBLog.INFO,
               "Total %d animations" % len(self._animations), "File")
        if len(self._objects) == 0:
            of.write("# No animations\n");
        else:
            for anim in self._animations:
                animtxt = str(anim)
                if animtxt != "None":
                    of.write(animtxt)
                else:
                    putlog(NBLog.CRITICAL, 
                           "Internal error: Couldn't serialize an animation",
                           "File")
                    of.write("# Excuse me, some interpretive problem...")

        # ... which are undone as of yet.

        # End of model file.
        of.write("donemodel %s\n" % self.getModelName())
        # "...and STAY down!!!" - Warrior, Myth III
        of.flush()
        fsync(of.fileno())
        of.close()
        of = 0
        # nuke(of)
        # destroy(of)
        # torture_until_dies(of)
        # shoot(of)
        # annihilate(of)
        # obliterate(of)

