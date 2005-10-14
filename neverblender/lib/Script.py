#################################################################
#
# export.py
# Export a model with settings from "nwnscript" text.
#
# part of the NeverBlender project
# (c) The NeverBlender Contributors 2005
# Distribute, modify and use however you please as long as you
# retain this copyright notice and comply to the terms set forth in the
# file COPYING. No warranty expressed or implied.
# $Id$
#
#################################################################

import Blender
import Blender.Text
import Blender.Object

import NBLog

# Try to find the 'nwnscript' text.  If it doesn't exist, create it,
# populating it with the default script, and inform the user.
template = """
# To export a model in NeverwinterNights .mdl format,
# select the 'Empty' parent of the model, customize the options
# below, and go to File->Export->NeverwinterNights ASCII Model (.mdl)
# The name of the empty parent should be the name you want your
# model to bear.

# Alternatively you can specify the name of the empty parent:
# Model.Name = 'MyBaseObject'

# This line tells the exporter what kind of model you are exporting.
# The options are Character, Tile, Effects, and Item.
Model.Classification = 'Item'

# Use this to tell NeverBlender exactly where you want the output to go.
# Model.OutputDirectory = '/path/to/output'

# Uncomment and customize this if you want to produce a walkmesh.
# Model.Walkmesh = 'MyWalkMesh'

# If you want to export animations you will want to uncomment and
# customize the following commands. (not yet implemented)
# Model.Animation.ExcludeBones = ['bogusbone1', 'bogusbone2']
# Model.Animation.Export('bogusaction1')
# Model.Animation.Export('bogusaction2')
"""
try:
	script = Blender.Text.Get('nwnscript')
except:
	script = Blender.Text.New('nwnscript')
	script.write(template)
	NBLog.report(NBLog.CRITICAL, "Fill in the 'nwnscript' text first - default script loaded")
	exit

# Here we actually execute the script in an environment that includes
# objects to be accessed from the script.  This sets up for a basic
# export script that exports a single Model, possibly with a walkmesh.
from ModelFile import ModelFile
from Trimesh import Trimesh
from Dummy import Dummy
model = ModelFile()
exec '\n'.join(script.asLines()) in {'Model': model}

if model.Name:
	selected = Blender.Object.Get(model.Name)
else:
	selected = Blender.Object.GetSelected()
	if not selected:
		NBLog.Report(NBLog.CRITICAL, "You must select a model to export.")
		return False
	selected = selected[0]
	model.Name = selected.getName()

# TODO: make this use the new Geometry module
model.addObjects(Dummy(selected).getTree())

model.writeToFile():

if model.Walkmesh:
	NBLog.putlog(NBLog.INFO, "Creating placeable walk data (PWK file)")
	pwkobj = Blender.Object.Get(model.Walkmesh)
	if pwkobj.getType() != 'Mesh':
		NBLog.Report(NBLog.CRITICAL, "PWK must be a Mesh!")
		exit
	pwkmesh = Trimesh(model.Walkmesh, "NULL", 0)
	ModelFile(name=model.Name, fileformat="pwk", objects=[pwkmesh]).writeToFile()
	
NBLog.Report(NBLog.INFO, "Export of .mdl completed")
