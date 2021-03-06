# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This was originaly derived from a cadquery script for generating PDIP models in X3D format
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
#
# Adapted by easyw for step and vrlm export
# See https://github.com/easyw/kicad-3d-models-in-freecad

## requirements
## cadquery FreeCAD plugin
##   https://github.com/jmwright/cadquery-freecad-module

## to run the script just do: freecad scriptName modelName
## e.g. FreeCAD export_conn_jst_xh.py all

## the script will generate STEP and VRML parametric models
## to be used with kicad StepUp script

#* These are FreeCAD & cadquery tools                                       *
#* to export generated models in STEP & VRML format.                        *
#*                                                                          *
#* cadquery script for generating JST-XH models in STEP AP214               *
#*   Copyright (c) 2016                                                     *
#* Rene Poeschl https://github.com/poeschlr                                 *
#* All trademarks within this guide belong to their legitimate owners.      *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU General Public License (GPL)             *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc.,                                                      *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA           *
#*                                                                          *
#****************************************************************************

__title__ = "make 3D models of JST-PH-Connectors."
__author__ = "scripts: maurice and hyOzd; models: poeschlr"
__Comment__ = '''make 3D models of JST-PH-Connectors types B??B-PH-K. (THT Top entry),
                S??B-PH-K (THT Side entry)'''

___ver___ = "1.1 10/04/2016"

import sys, os
import datetime
from datetime import datetime
sys.path.append("../_tools")
import exportPartToVRML as expVRML
import shaderColors
import re, fnmatch

# Licence information of the generated models.
#################################################################################################
STR_licAuthor = "Rene Poeschl"
STR_licEmail = "poeschlr@gmail.com"
STR_licOrgSys = ""
STR_licPreProc = ""

LIST_license = ["Copyright (C) "+datetime.now().strftime("%Y")+", " + STR_licAuthor,
                "",
                "This program is free software: you can redistribute it and/or modify",
                "it under the terms of the GNU General Public License (GPL)",
                "as published by the Free Software Foundation, either version 2 of",
                "the License, or any later version.",
                "",
                "As a special exception, if you create a design which uses this 3d model",
                "and embed this 3d model or unaltered portions of this 3d model into the",
                "design, this 3d model does not by itself cause the resulting design to",
                "be covered by the GNU General Public License. This exception does not",
                "however invalidate any other reasons why the design itself might be",
                "covered by the GNU General Public License. If you modify this",
                "3d model, you may extend this exception to your version of the",
                "3d model, but you are not obligated to do so. If you do not",
                "wish to do so, delete this exception statement from your version.",
                "",
                "This program is distributed in the hope that it will be useful,",
                "but WITHOUT ANY WARRANTY; without even the implied warranty of",
                "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the",
                "GNU General Public License for more details.",
                "",
                "You should have received a copy of the GNU General Public License",
                "along with this program.  If not, see http://www.gnu.org/licenses/.",
                ""
                ]
#################################################################################################

body_color_key = "white body"
body_color = shaderColors.named_colors[body_color_key].getDiffuseInt()
pins_color_key = "metal grey pins"
pins_color = shaderColors.named_colors[pins_color_key].getDiffuseInt()

destination_dir="Connectors_JST.3dshapes"

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui

#checking requirements
#######################################################################
FreeCAD.Console.PrintMessage("FC Version \r\n")
FreeCAD.Console.PrintMessage(FreeCAD.Version())
FC_majorV=FreeCAD.Version()[0];FC_minorV=FreeCAD.Version()[1]
FreeCAD.Console.PrintMessage('FC Version '+FC_majorV+FC_minorV+'\r\n')

if int(FC_majorV) <= 0:
    if int(FC_minorV) < 15:
        reply = QtGui.QMessageBox.information(None,"Warning! ...","use FreeCAD version >= "+FC_majorV+"."+FC_minorV+"\r\n")


# FreeCAD.Console.PrintMessage(M.all_params_soic)
FreeCAD.Console.PrintMessage(FreeCAD.ConfigGet("AppHomePath")+'Mod/')
file_path_cq=FreeCAD.ConfigGet("AppHomePath")+'Mod/CadQuery'
if os.path.exists(file_path_cq):
    FreeCAD.Console.PrintMessage('CadQuery exists\r\n')
else:
    msg="missing CadQuery Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki"
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)

#######################################################################
from Gui.Command import *

outdir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(outdir)

# Import cad_tools
#sys.path.append("../")
import cq_cad_tools
# Reload tools
reload(cq_cad_tools)
# Explicitly load all needed functions
from cq_cad_tools import FuseObjs_wColors, GetListOfObjects, restore_Main_Tools, \
 exportSTEP, close_CQ_Example, saveFCdoc, z_RotateObject

# Gui.SendMsgToActiveView("Run")
Gui.activateWorkbench("CadQueryWorkbench")
import FreeCADGui as Gui

try:
    close_CQ_Example(App, Gui)
except: # catch *all* exceptions
    print "CQ 030 doesn't open example file"


import cadquery as cq

#check version
cqv=cq.__version__.split(".")
#say2(cqv)
if int(cqv[0])==0 and int(cqv[1])<3:
    msg = "CadQuery Module needs to be at least 0.3.0!\r\n\r\n"
    reply = QtGui.QMessageBox.information(None, "Info ...", msg)
    say("cq needs to be at least 0.3.0")
    stop

from math import sqrt
from Helpers import show
from collections import namedtuple
import FreeCAD, Draft, FreeCADGui
import ImportGui
sys.path.append("cq_models")
import conn_jst_ph_models as ModelPH
import conn_jst_eh_models as ModelEH
import conn_jst_xh_models as ModelXH
import step_license as L

if float(cq.__version__[:-2]) < 0.3:
    msg="missing CadQuery 0.3.0 or later Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki\n"
    msg+="actual CQ version "+cq.__version__
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)


def export_one_part(params, series):
    FreeCAD.Console.PrintMessage('\r\n'+params.model_name)
    ModelName = params.model_name
    FileName = params.file_name
    Newdoc = FreeCAD.newDocument(ModelName)
    App.setActiveDocument(ModelName)
    Gui.ActiveDocument=Gui.getDocument(ModelName)
    (pins, body) = series.generate_part(params)

    color_attr = body_color + (0,)
    show(body, color_attr)

    color_attr = pins_color + (0,)
    show(pins, color_attr)

    doc = FreeCAD.ActiveDocument
    doc.Label=ModelName
    objs=GetListOfObjects(FreeCAD, doc)
    objs[0].Label = ModelName + "__body"
    objs[1].Label = ModelName + "__pins"

    restore_Main_Tools()

    out_dir=destination_dir


    used_color_keys = [body_color_key, pins_color_key]
    export_file_name=destination_dir+os.sep+FileName+'.wrl'

    export_objects = []
    export_objects.append(expVRML.exportObject(freecad_object = objs[0],
            shape_color=body_color_key,
            face_colors=None))
    export_objects.append(expVRML.exportObject(freecad_object = objs[1],
            shape_color=pins_color_key,
            face_colors=None))

    scale=1/2.54
    colored_meshes = expVRML.getColoredMesh(Gui, export_objects , scale)
    expVRML.writeVRMLFile(colored_meshes, export_file_name, used_color_keys, LIST_license)

    fusion = FuseObjs_wColors(FreeCAD, FreeCADGui,
                    ModelName, objs[0].Name, objs[1].Name, keepOriginals=True)
    exportSTEP(doc,FileName,out_dir,fusion)
    L.addLicenseToStep(out_dir+'/', FileName+".step", LIST_license,\
        STR_licAuthor, STR_licEmail, STR_licOrgSys, STR_licPreProc)


    FreeCAD.activeDocument().recompute()
    #FreeCADGui.activateWorkbench("PartWorkbench")
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.activeDocument().activeView().viewAxometric()

    saveFCdoc(App, Gui, doc, FileName,out_dir)

def exportSeries(series_params, model_filter_regobj, series):
    for key in series_params.keys():
        if model_filter_regobj.match(key):
            FreeCAD.Console.PrintMessage('Current Model: '+str(key)+'\r\n')
            export_one_part(series_params[key], series)


if __name__ == "__main__":
    FreeCAD.Console.PrintMessage('\r\nRunning...\r\n')
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    series_to_build = []
    modelfilter = "*"


    for arg in sys.argv[2:]:
        if arg.startswith("series="):
            series_to_build += arg[len("series="):].lower().split(',')
        elif arg.startswith("filter="):
            modelfilter = arg[len("filter="):]
        elif len(sys.argv) == 3:
            #fallback mode: only one parameter. This parameter is either all or the name of the model to build.
            if sys.argv[2] == "all":
                series_to_build = ['xh', 'eh', 'ph']
                modelfilter = "*"
            elif not '=' in sys.argv[2]:
                modelfilter = sys.argv[2]



    if len(series_to_build) == 0:
        series_to_build = ['xh', 'eh', 'ph']

    series = []
    if 'xh' in series_to_build:
        series += [ModelXH]
    if 'eh' in series_to_build:
        series += [ModelEH]
    if 'ph' in series_to_build:
        series += [ModelPH]

    model_filter_regobj=re.compile(fnmatch.translate(modelfilter))
    for current_series in series:
        exportSeries(current_series.all_params, model_filter_regobj, current_series)

    FreeCAD.Console.PrintMessage('\r\nDone\r\n')
