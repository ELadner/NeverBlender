#################################################################
#
# FindFromList.py
# A class for finding stuff from lists.
#
# part of the NeverBlender project
# (c) Urpo Lankinen 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice. No warranty expressed or implied.
# $Id$
#
#################################################################

## For Locating Stuff.

# Returns index of "what" on the list "list". No idea if Python has this
# function built in. My head hurts more each time I see the Python
# manual.
# (I know there's 'what in list', but what about 'what wherein list'...???)
def atwhatpoint(list,what):
	try:
		return list.index(what)
	except ValueError:
		return -1

# Finds triangle's vertices "v1","v2","v3" from vertex (tuple) list "list".
# Returns list.
def findtriangleverts(list,v1,v2,v3):
	return [ atwhatpoint(list,v1),
		atwhatpoint(list,v2),
		atwhatpoint(list,v3) ]

