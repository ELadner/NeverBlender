#################################################################
#
# nwnmdlimport.py
# Neverwinter Nights ASCII .mdl import script for Blender.
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

# Blender Python script for reading NWN models.
# Does not attempt to read walkmeshes or particles.
# Animations should perhaps be reordered to work right; close2open of the chest,
# for instance, goes from open to closed to open...

from Blender import Scene, Object, NMesh, Image, Text, Ipo, Window
from math import sin, atan2, asin, cos, acos, pi
from types import FileType

filename='plc_a08.mdl.ascii'

class ExitLineReader(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def linereaderbreak(file, words, data):
  raise ExitLineReader(words)

class linereader:
  def progress(self, message=None):
    if message==None:
      message=self.status
    Window.drawProgressBar(1.0-len(self.lines)/self.length, message)
  def __init__(self, file, dict, data=None, significant=True):
    if hasattr(file, 'readlines'):
      # File, let's preload it
      self.lines=file.readlines()
      self.length=float(len(self.lines))
      self.status='loading file'
    else:
      # Inherit from parent linereader
      self.lines=file.lines
      self.length=file.length
      if significant:
        self.status=file.lastline
      else:
        self.status=file.status
    while len(self.lines):
      self.progress()
      self.lastline=self.lines[0]
      del self.lines[0]
      words=self.lastline.split()
      if len(words) and dict.has_key(words[0]):
        try:
          dict[words[0]](self, words, data)
        except ExitLineReader:
          return
  def readline(self):
    self.progress()
    self.lastline=self.lines[0]
    del self.lines[0]
    return self.lastline

def rad2decadeg(x):
  # Yep. Blender's ipos store rotation in tens of degrees.
  return x*18/pi

# THANK YOU for intern/python/modules/util/quat.py (from Blender source)
# Unfortunately this is still pretty slow. Someone who knows the math please help?
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

#def euler2nwn(eul):
#  # Euler to quaternion
#  e=eul[0]/2.0
#  cx=cos(e)
#  sx=sin(e)
#  e=eul[1]/2.0
#  cy=cos(e)
#  sy=sin(e)
#  e=eul[2]/2.0
#  cz=cos(e)
#  sz=sin(e)
#  w=cx*cy*cz-sx*sy*sz
#  x=sx*cy*cz-cx*sy*sz
#  y=cx*sy*cz+sx*cy*sz
#  z=cx*cy*sz+sx*sy*cz
#  # quaternion to axis/angle
#  phi2=acos(w)
#  if phi2==0.0:
#    return 0.0, 0.0, 0.0, 0.0
#  s=1/sin(phi2)
#  return s*x, s*y, s*z, 2.0*phi2

def loadgeomnode(file, words, pdata):
  def objprop(file, words, data):
    data['nwnprops'].write('%s.%s=%s\n'%(data['object'].name, words[0], words[1]))
  def parent(file, words, data):
    if words[1]=='NULL':
      data['nwnprops'].write('SCENE.baseobjectname=%s\n'%data['object'].name)
    else:
      p=Object.get(words[1])
      p.makeParent([data['object']])
  def position(file, words, data):
    data['object'].setLocation(map(float, words[1:4]))
  def orientation(file, words, data):
    data['object'].setEuler(nwn2euler(map(float, words[1:5])))
  def bitmap(file, words, data):
    image=Image.get(words[1]+'.tga')
    if image==None:
      try:
	image=Image.Load(words[1]+'.tga')
      except IOError:
        pass
    data['nwnprops'].write('%s.texture=%s\n'%(data['object'].name, words[1]))
    data['texture']=image
  def verts(file, words, data):
    vertexcount=int(words[1])
    while vertexcount>0:
      data['mesh'].verts.append(apply(NMesh.Vert, map(float, file.readline().split())))
      vertexcount-=1
  # Well, Torlack's NWN model decompiler puts faces after tverts.
  # NWN's sample file had it the other way around, so we support both.
  def fixuvs(data):
    mesh=data['mesh']
    uvi=data['uvi']
    uvc=data['uvc']
    for fi in range(len(uvi)):
      face=mesh.faces[fi]
      face.uv=map(lambda x: uvc[x], uvi[fi])
      face.mode=NMesh.FaceModes.TEX
    # TODO: recalculate the normals. They're all random, and PutRaw cancels transforms.
    #NMesh.PutRaw(mesh, data['object'].name)
    mesh.update()
  def faces(file, words, data):
    uvi=[]
    mesh=data['mesh']
    facecount=int(words[1])
    while facecount>0:
      f=NMesh.Face()
      line=map(int, file.readline().split())
      f.image=data['texture']
      for v in line[0:3]:
        f.v.append(mesh.verts[v])
      f.smooth=line[3]
      mesh.faces.append(f)
      uvi.append(line[4:7])
      facecount-=1
    data['uvi']=uvi
    if data.has_key('uvc'):
      fixuvs(data)
  def tverts(file, words, data):
    mesh=data['mesh']
    uvc=[]
    uvcount=int(words[1])
    while uvcount>0:
      uvc.append(tuple(map(float, file.readline().split()[0:2])))
      uvcount-=1
    data['uvc']=uvc
    if data.has_key('uvi'):
      fixuvs(data)
  nodedict={'parent': parent, 'position': position, 'bitmap': bitmap,
        'verts': verts, 'faces': faces, 'endnode': linereaderbreak,
        'tverts': tverts, 'orientation': orientation, 'tilefade': objprop}
  data=None
  if words[1]=='dummy':
    data={'object': Object.New('Empty')}
  elif words[1]=='trimesh':
    data={'object': Object.New('Mesh'), 'mesh': NMesh.New(words[2])}
    data['object'].link(data['mesh'])
  else:
    return	# unsupported node type
  # Note: Blender 2.27, New(type, name) didn't work. object.name worked.
  data['object'].name=words[2]
  data['nwnprops']=pdata['nwnprops']
  linereader(file, nodedict, data)
  pdata['scene'].link(data['object'])

def loadgeometry(file, words, data):
  geomdict={'node': loadgeomnode, 'endmodelgeom': linereaderbreak}
  linereader(file, geomdict, data)

def loadanimnode(file, words, data):
  def getipo(object):
    ipo=Ipo.get(object.name)
    if ipo==None:
      ipo=Ipo.New('Object', object.name)
      object.link(ipo)
    return ipo
  def getcurves(ipo, list):
    retlist=[]
    for curvename in list:
      curve=ipo.get(curvename)
      if curve==None:
        curve=ipo.addCurve(curvename)
        curve.setInterpolation('Linear')
      retlist.append(curve)
    return retlist
  def getfloatlines(file, words):
    retlist=[]
    # Another inconsistency between Torlack's and BioWare's model files
    # Torlack's decompiler writes the count as with vertices and faces
    if len(words)==2:
      count=int(words[1])
      while count>0:
        retlist.append(map(float, file.readline().split()))
        count-=1
    else:
      line=file.readline().split()
      while line[0]!='endlist':
        retlist.append(map(float, line))
        line=file.readline().split()
    return retlist
  def positionkey(file, words, data):
    positions=getfloatlines(file, words)
    if len(positions):
      ipo=getipo(data['node'])
      loc=getcurves(ipo, ['LocX', 'LocY', 'LocZ'])
      if len(loc[0])==0:
        origloc=data['node'].loc
        for i in range(3):
          loc[i].addBezier((1.0, origloc[i]))
      for point in positions:
        time=data['fps']*point[0]+data['animnextframe']
        for i in range(3):
          loc[i].addBezier((time, point[i+1]))
      for curve in loc:
        curve.update()
  def orientationkey(file, words, data):
    orientations=getfloatlines(file, words)
    if len(orientations):
      ipo=getipo(data['node'])
      rot=getcurves(ipo, ['RotX', 'RotY', 'RotZ'])
      if len(rot[0])==0:
        origrot=map(rad2decadeg, data['node'].getEuler())
        for i in range(3):
          rot[i].addBezier((1.0, origrot[i]))
      for point in orientations:
        time=data['fps']*point[0]+data['animnextframe']
        prot=map(rad2decadeg, nwn2euler(point[1:5]))
        for i in range(3):
          rot[i].addBezier((time, prot[i]))
      for curve in rot:
        # This flag tells that we do NOT want radian->degree conversion.
        # Skipping it breaks the curves since we're adding new points to
        # existing curves.
        curve.update(1)
  data['node']=Object.get(words[2])
  animnodedict={'positionkey': positionkey, 'orientationkey': orientationkey,
          'endnode': linereaderbreak}
  linereader(file, animnodedict, data, False)

def loadanim(file, words, data):
  def animpropfloat(file, words, data):
    data[words[0]]=float(words[1])
  animdict={'length': animpropfloat, 'transtime': animpropfloat, 'transtime': animpropfloat,
          'node': loadanimnode, 'doneanim': linereaderbreak}
  linereader(file, animdict, data)
  end=data['animnextframe']+data['fps']*data['length']
  data['nwnanims'].write('anim %s start %d end %d fps %d transtime %f\n'%
          (words[1], data['animnextframe'], end, data['fps'], data['transtime']))
  data['animnextframe']=end+1
  #raise ExitLineReader('Stop after one animation')

def loadmodel(file, words, data):
  def nwprop(file, words, data):
    data['nwnprops'].write('SCENE.%s=%s\n'%(words[0], words[1]))
  modeldict={'beginmodelgeom': loadgeometry, 'donemodel': linereaderbreak,
        'classification': nwprop, 'supermodel': nwprop, 'newanim': loadanim}
  data={'scene': Scene.getCurrent(), 'nwnprops': Text.New('nwnprops'),
          'animnextframe': 2, 'nwnanims': Text.New('nwnanims'), 'fps': 30}
  raise ExitLineReader(linereader(file, modeldict, data))
  # Seems I can't modify the frame settings.
  #data['scene'].startFrame(1)
  #data['scene'].currentFrame(1)
  #data['scene'].endFrame(data['animnextframe']-1)
  data['scene'].update()

file=open(filename)
filedict={'newmodel': loadmodel}
linereader(file, filedict)

