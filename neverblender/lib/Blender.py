#################################################################
#
# Blender.py
# Fake Blender module for import testing
#
# Written by Yann Vernier.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
##############################################################

class Scene:
  def getCurrent():
    return None

class Object:
  def get(x):
    return None

Text=Object
