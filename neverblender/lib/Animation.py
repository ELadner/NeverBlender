#################################################################
#
# Animation.py
# Containing and outputting the Animation data.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003,2004
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import Blender
from Blender import Mathutils
from Blender.Mathutils import *

from string import join
import NBLog
from NBLog import putlog

class Animation:
    def __init__(self, object=None):
        self._name = "untitledrawanim"
        self._modelname = "nomodel"
        self._length = 1.0
        self._transtime = 1.0
        self._animnodes = []
        
    def __str__(self):
        o = ("newanim %s %s\n" % (self._name, self._modelname)) + \
                ("  length %f\n" % self._length) + \
                ("  transtime %f\n" % self._transtime) + \
                self._nodes_as_string() + \
                ("doneanim %s %s\n" % (self._name, self._modelname))
        return o
    def _nodes_as_string(self):
        return ""

    def setName(self,name):
        self._name = name
    def setModelName(self,name):
        self._modelname = name
    def setLength(self,length):
        self._length = length
    def settransTime(self,length):
        self._transtime = length

    def addNode(self,node):
        self._animnodes.append(node)


class AnimationNode:
    # _type = "undefined"
    # _name = ""
    # _parent = ""
    # _position = [0.0, 0.0, 0.0]
    # _orientation = [0.0, 0.0, 0.0]
    # _scale = 1.0
    
    # _orientationlist = []
    # _positionlist = []

    def __init__(self, object=None):
        self._type = "undefined"
        self._name = "untitlednode"
        self._parent = "NULL"
        self._position = [0.0, 0.0, 0.0]
        self._orientation = [0.0, 0.0, 0.0]
        self._scale = 1.0

        # Private data.
        self._orientationlist = []
        self._positionlist = []

    # Basic stuff.
    def setName(self, name):
        self._name = name
    def setParent(self, parent):
        self._parent = parent
    def setPosition(self, poslist):
        assert len(poslist) == 3
        self._position = poslist
    def setOrientation(self, orientation):
        # Would be nice to check, but I'm a peabrain and can't
        # figure out why this won't work.
        #assert isinstance(orientation, Euler)
        self._orientation = orientation

    def addOrientationKey(self, time, x, y, z, r):
        self._animnodes.append(tuple(time,x,y,z,r))
    def addPositionKey(self, time, x, y, z):
        self._animnodes.append(tuple(time,x,y,z))


    def __str__(self):
        # NB: indent down two spaces!
        o = ("  node %s %s\n" % (self._type, self._name)) + \
                ("    parent %s\n" % self._parent) + \
                ("    position %f %f %f\n" % tuple(self._position)) + \
                self._orientation_as_string() + \
                ("    scale %f\n" % self._scale) + \
                self._orientationlist_as_string() + \
                self._positionlist_as_string() + \
                "  endnode\n"
        return o

    def _orientation_as_string(self):
        # indent down four spaces
        o = self._orientation
        q = o.toQuat()
        if o.x == 0.0 and o.y == 0.0 and o.z == 0.0:
            return ""
        return "    orientation %f %f %f %f\n" % \
               (q.x, q.y, q.z, q.w)

    def _orientationlist_as_string(self):
        o = "    orientationkey\n"
        for item in self._orientationlist:
            o += "      %f %f %f %f %f\n" % item
        o += "    endlist\n"
        return o
            
    def _positionlist_as_string(self):
        o = "    positionkeykey\n"
        for item in self._positionlist:
            o += "      %f %f %f %f\n" % item
        o += "    endlist\n"
        return o
