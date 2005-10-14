#!BPY
""" Registration info for Blender menus
Name:    'Bioware NWN, ASCII (.mdl)...'
Blender: 233
Group:   'Export'
Tip:     'Export in Neverwinter Nights format ASCII model'
"""
#################################################################
#
# nwnmdlexporthook.py
# Menu hook for Neverwinter Nights ASCII .mdl export script for Blender.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

# Really this file just locates NeverBlender, adds it to the
# pythonpath, and executes it.

# This is a severely ugly hack to get the path access working
# in a sane way. Goddamn Blender won't honor the Ordinary Python
# Library Path.
import Blender
import os.path
import sys
from os import access, X_OK
# If you put neverblender somewhere else, add it to the candidates
# list.  This script searches the candidates for 'neverblender/lib' in
# order, so the order of the list matters if and only if you have
# multiple instances of neverblender/lib.
candidates = [Blender.Get('scriptsdir'), Blender.Get('uscriptsdir'), '/usr/local/lib', 'c:/msys/local/lib', '.']
for d in candidates:
    if d:
        d = os.path.join(d, 'neverblender/lib')
        if access(d, X_OK) == 1:
            sys.path.append(d)
			
import nwnmdlexport
