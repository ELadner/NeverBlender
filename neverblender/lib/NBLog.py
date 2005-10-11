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
# Indexes of this list correspond to above constants...
prefixes = ['   ', '[*]', '[!] WARNING:', '<!> CRITICAL ERROR:', '<?> DEBUG:']

logfile = 0
loggingtofile = 0

def openlogfile(filename, module=""):
    global logfile, loggingtofile
    logfile = file(filename, "w")
    loggingtofile = 1

def closelogfile(module=""):
    global logfile, loggingtofile
    if not loggingtofile:
        putlog(WARNING, "Trying to close a nonexistent", module)
    logfile.close()
    loggingtofile = 0

def putlog(sev, message, module=""):
    "Output a console message with specified message class/severity."
    if not module:
        print prefixes[sev] + " " + message
        if loggingtofile:
            logfile.write(prefixes[sev] + " " + message + "\n")
    else:
        print prefixes[sev] + " [" + module + "] " + message
        if loggingtofile:
            logfile.write(prefixes[sev] + " [" + module + "] " +
                          message + "\n")

import Blender
import Blender.Draw
def Report(sev, message, module=""):
	"Output a console message AND produce a message popup."
	putlog(sev, message, module)
	Blender.Draw.PupMenu(message)
