#################################################################
#
# NBLog.py
# Functions for outputting messages.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2003
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$ 
#
#################################################################

# The log levels should be specified in order of importance.
SPAM = 0
INFO = 1
WARNING = 2
CRITICAL = 3
DEBUG = 4

def putlog(sev, message):
    "Output a console message with specified message class/severity."
    if sev == SPAM:
        print "    " + message
    elif sev == INFO:
        print "[*] " + message
    elif sev == WARNING:
        print "[!] WARNING: " + message
    elif sev == CRITICAL:
        print "<!> CRITICAL ERROR: " + message
    elif sev == DEBUG:
        print "    " + message
    else:
        print "    " + message

