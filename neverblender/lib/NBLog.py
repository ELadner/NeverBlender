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

def putlog(sev, message, module=""):
    "Output a console message with specified message class/severity."
    if not module:
        print prefixes[sev] + " " + message
    else:
        print prefixes[sev] + " [" + module + "] " + message
