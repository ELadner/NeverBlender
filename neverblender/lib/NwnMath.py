#################################################################
#
# NwnMath.py
# Mathematics routines for converting values between NWN and Blender.
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

from math import sin, atan2, asin, cos, acos, pi

def rad2decadeg(x):
    # Yep. Blender's ipos store rotation in tens of degrees.
    return x*18/pi

# THANK YOU for intern/python/modules/util/quat.py (from Blender
# source). Unfortunately this is still pretty slow. Someone who knows
# the math please help?
# (Would love to help, but math is all greek to me, too... -W4)
# (Just tried this myself. Jesus, this is dog slow. Anyone? Please? -W4)
def nwn2euler(nwn):
    # axis/angle to quaternion
    phi2=0.5*nwn[3]
    s=sin(phi2)
    w=cos(phi2)
    x=nwn[0]*s
    y=nwn[1]*s
    z=nwn[2]*s
    # quaternion to euler
    x2=x*x
    z2=z*z
    tmp=x2-z2
    r=(w*w+tmp-y*y)
    phi_z=atan2(2.0*(x*y+w*z), r)
    phi_y=asin(2.0*(w*y-x*z))
    phi_x=atan2(2.0*(w*x+y*z), r-2.0*tmp)
    return phi_x, phi_y, phi_z

def euler2nwn(eul):
    # Euler to quaternion
    e=eul[0]/2.0
    cx=cos(e)
    sx=sin(e)
    e=eul[1]/2.0
    cy=cos(e)
    sy=sin(e)
    e=eul[2]/2.0
    cz=cos(e)
    sz=sin(e)
    w=cx*cy*cz-sx*sy*sz
    x=sx*cy*cz-cx*sy*sz
    y=cx*sy*cz+sx*cy*sz
    z=cx*cy*sz+sx*sy*cz
    # quaternion to axis/angle
    phi2=acos(w)
    if phi2==0.0:
        return 0.0, 0.0, 0.0, 0.0
    s=1/sin(phi2)
    return s*x, s*y, s*z, 2.0*phi2
