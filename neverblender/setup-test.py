#!BPY
""" Registration info for Blender menus
Name:    'Python setup information'
Blender: 233
Group:   'Export'
Tip:     'Shows details on how Python is set up.'
"""
#################################################################
#
# setup-test.py
# Shows details on how Python is set up.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

from sys import path

print "\nDetails about your Python setup"
print "===============================\n\n"

print "Directories included in search path:"
for p in path:
    print "    ", p
    
print "\n\n"