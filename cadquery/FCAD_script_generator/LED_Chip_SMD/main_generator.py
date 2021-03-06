# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This is derived from a cadquery script for generating PDIP models in X3D format
#
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
# This is a
# Dimensions are from Microchips Packaging Specification document:
# DS00000049BY. Body drawing is the same as QFP generator#

## requirements
## cadquery FreeCAD plugin
##   https://github.com/jmwright/cadquery-freecad-module

## to run the script just do: freecad make_gwexport_fc.py modelName
## e.g. c:\freecad\bin\freecad make_gw_export_fc.py SOIC_8

## the script will generate STEP and VRML parametric models
## to be used with kicad StepUp script

#* These are a FreeCAD & cadquery tools                                     *
#* to export generated models in STEP & VRML format.                        *
#*                                                                          *
#* cadquery script for generating QFP/SOIC/SSOP/TSSOP models in STEP AP214  *
#*   Copyright (c) 2015                                                     *
#* Maurice https://launchpad.net/~easyw                                     *
#* All trademarks within this guide belong to their legitimate owners.      *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
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

__title__ = "make chip capacitors 3D models"
__author__ = "maurice"
__Comment__ = 'make chip capacitos 3D models exported to STEP and VRML for Kicad StepUP script'

___ver___ = "1.3.2 10/02/2017"

# thanks to Frank Severinsen Shack for including vrml materials

# maui import cadquery as cq
# maui from Helpers import show
from math import tan, radians, sqrt
from collections import namedtuple

import sys, os
import datetime
from datetime import datetime
sys.path.append("../_tools")
import exportPartToVRML as expVRML
import shaderColors

body_color_key = "white body"
body_color = shaderColors.named_colors[body_color_key].getDiffuseFloat()
pins_color_key = "gold pins"
pins_color = shaderColors.named_colors[pins_color_key].getDiffuseFloat()
top_color_key = "led white"
top_color = shaderColors.named_colors[top_color_key].getDiffuseFloat()
pinmark_color_key = "green body"
pinmark_color = shaderColors.named_colors[pinmark_color_key].getDiffuseFloat()
die_color_key = "black body"
die_color = shaderColors.named_colors[die_color_key].getDiffuseFloat()


# maui start
import FreeCAD, Draft, FreeCADGui
import ImportGui
import FreeCADGui as Gui
#from Gui.Command import *

cd_new_notfound=False
cd_notfound=False
try:
    from CadQuery.Gui.Command import *
except:
    cd_new_notfound=True
try:
    from Gui.Command import *
except:
    cd_notfound=True
if cd_new_notfound and cd_notfound:
    msg="missing CadQuery 0.3.0 or later Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki\n"
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)


outdir=os.path.dirname(os.path.realpath(__file__)+"/../_3Dmodels")
scriptdir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(outdir)
sys.path.append(scriptdir)

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui

# Licence information of the generated models.
#################################################################################################
STR_licAuthor = "kicad StepUp"
STR_licEmail = "ksu"
STR_licOrgSys = "kicad StepUp"
STR_licPreProc = "OCC"
STR_licOrg = "FreeCAD"   

LIST_license = ["",]
#################################################################################################


# Import cad_tools
import cq_cad_tools
# Reload tools
reload(cq_cad_tools)
# Explicitly load all needed functions
from cq_cad_tools import FuseObjs_wColors, GetListOfObjects, restore_Main_Tools, \
 exportSTEP, close_CQ_Example, exportVRML, saveFCdoc, z_RotateObject, Color_Objects, \
 CutObjs_wColors, checkRequirements

try:
    # Gui.SendMsgToActiveView("Run")
    #from Gui.Command import *
    Gui.activateWorkbench("CadQueryWorkbench")
    import cadquery as cq
    from Helpers import show
    # CadQuery Gui
except: # catch *all* exceptions
    msg="missing CadQuery 0.3.0 or later Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki\n"
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)
    # maui end

#checking requirements
checkRequirements(cq)

try:
    close_CQ_Example(App, Gui)
except: # catch *all* exceptions
    print "CQ 030 doesn't open example file"

import cq_parameters  # modules parameters
from cq_parameters import *

#all_params= all_params_res
all_params= kicad_naming_params_res

def make_chip(params):
    # dimensions for chip capacitors
    L = params.L    # package length
    W = params.W    # package width
    T = params.T    # package height

    pb = params.pb  # pin band
    pt = params.pt  # pin thickness
    ph = params.ph  # pin height

    pintype = params.pintype # 
    ef = params.ef  # fillet of edges
    modelName = params.modelName  # Model Name
    rotation = params.rotation   # rotation
    internals = False
    die = None
    # Create a 3D box based on the dimension variables above and fillet it
    case = cq.Workplane("XY").box(L-2*pt, W, ph-2*pt)
    if pintype == 'concave':
        case = case.workplane(offset=T/2).moveTo(-L/2, -W/4-0.1).threePointArc((-L/2+pb/2+0.1, 0),(-L/2, W/4+0.1),forConstruction=False).close().cutThruAll().moveTo(L/2, -W/4-0.1).threePointArc((L/2-pb/2-0.1, 0),(L/2, W/4+0.1),forConstruction=False).close().cutThruAll()
    # translate the object
    case=case.translate((0,0,ph/2)).rotate((0,0,0), (0,0,1), 0)
    top = cq.Workplane("XZ").workplane(offset=-W/2).moveTo(-(L/2-pb),ph-pt).lineTo((-(L/2-pb))*0.9, T).lineTo((L/2-pb)*0.9, T).lineTo(L/2-pb,ph-pt).close().extrude(W)

    # Create a 3D box based on the dimension variables above and fillet it
    pin1 = cq.Workplane("XY").box(pb, W, ph).edges("|Y").fillet(ef)

    pin1= pin1.translate((-L/2+pb/2,0,ph/2)).rotate((0,0,0), (0,0,1), 0)
    pin2 = cq.Workplane("XY").box(pb, W, ph)
    pin2.edges("|Y").fillet(ef)
    pin2=pin2.translate((L/2-pb/2,0,ph/2)).rotate((0,0,0), (0,0,1), 0)
    pins = pin1.union(pin2)
    if pintype == 'concave':
        pins = pins.workplane(offset=ph).moveTo(-L/2, -W/4).threePointArc((-L/2+pb/2, 0),(-L/2, W/4),forConstruction=False).close().cutThruAll().moveTo(L/2, -W/4).threePointArc((L/2-pb/2, 0),(L/2, W/4),forConstruction=False).close().cutThruAll()
    elif pintype == 'convex':
        pins = pins.workplane(offset=ph).moveTo(0, W/2).rect(L-pb/2, W/4, centered=True).cutThruAll().moveTo(0, -W/2).rect(L-pb/2, W/4, centered=True).cutThruAll()
    if internals:
        F = (L/2-pb)-L/8+W/16
        pins = pins.union(cq.Workplane("XY").workplane(offset=ph-pt).rect(W/2, W/2, centered=True).extrude(pt).moveTo(-F/2 ,0).rect(F, W/8, centered=True).extrude(pt).\
        moveTo((L/2-pb)/2 ,0).rect(L/2-W/4, W/16, centered=True).extrude(pt))
        d = W/32
        F = (L/2-pb)-L/8+W/16
        D = (d*1.5+pt)*2
        lead1 = cq.Workplane("XY").workplane(offset=ph-pt).center(-F/2,0).circle(d/2).extrude(D/2-d)
        lead1 = lead1.union(cq.Workplane("XY").workplane(offset=D/2-d+ph-pt).center(-F/2,0).circle(d/2).center(-F/2+d/2,0).revolve(90,(-F/2+d/2+d,d)))
        lead1 = lead1.rotate((-F/2,0,0), (0,0,1), -90)
        lead2 = lead1.rotate((-F/2,0,0), (0,0,1), 180).translate((F,0,0))
        Hlead = cq.Workplane("YZ").workplane(offset=-F/2+d).center(0,D/2+ph-pt).circle(d/2).extrude(F-d*2)
        leads = lead1.union(lead2).union(Hlead).translate((-F/2,0,0))
        pins = pins.union(leads)

        die = cq.Workplane("XY").workplane(offset=ph).rect(W/4, W/4, centered=True).rect(W/8, W/8, centered=True).extrude(pt)
    #body_copy.ShapeColor=result.ShapeColor
    pinmark_side = W*0.7
    pinmark_length = sqrt(pinmark_side*pinmark_side - pinmark_side/2*pinmark_side/2)
    pinmark = cq.Workplane("XY").workplane(offset=pt/2).moveTo(pinmark_length/2,0).lineTo(-pinmark_length/2,pinmark_side/2).lineTo(-pinmark_length/2,-pinmark_side/2).close().extrude(pt/2)
    # extract case from pins
    # case = case.cut(pins)
    pins = pins.cut(case)

    return (case, top, pins, pinmark, die)

#import step_license as L
import add_license as Lic

if __name__ == "__main__" or __name__ == "main_generator":
    expVRML.say(expVRML.__file__)
    FreeCAD.Console.PrintMessage('\r\nRunning...\r\n')
    
    full_path=os.path.realpath(__file__)
    expVRML.say(full_path)
    scriptdir=os.path.dirname(os.path.realpath(__file__))
    expVRML.say(scriptdir)
    sub_path = full_path.split(scriptdir)
    expVRML.say(sub_path)
    sub_dir_name =full_path.split(os.sep)[-2]
    expVRML.say(sub_dir_name)
    sub_path = full_path.split(sub_dir_name)[0]
    expVRML.say(sub_path)
    models_dir=sub_path+"_3Dmodels"
    #expVRML.say(models_dir)
    #stop

    if len(sys.argv) < 3:
        FreeCAD.Console.PrintMessage('No variant name is given! building R_0402')
        model_to_build='R_0402'
    else:
        model_to_build=sys.argv[2]

    if model_to_build == "all":
        variants = all_params.keys()
    else:
        variants = [model_to_build]

    for variant in variants:
        
        FreeCAD.Console.PrintMessage('\r\n'+variant)
        if not variant in all_params:
            print("Parameters for %s doesn't exist in 'all_params', skipping." % variant)
            continue
        ModelName = all_params[variant].modelName
        CheckedModelName = ModelName.replace('.', '').replace('-', '_').replace('(', '').replace(')', '')
        Newdoc = App.newDocument(CheckedModelName)
        App.setActiveDocument(CheckedModelName)
        Gui.ActiveDocument=Gui.getDocument(CheckedModelName)
        body, pins, top, pinmark, die = make_chip(all_params[variant])

        show(body)
        show(pins)
        show(top)
        show(pinmark)
        if die:
        	show(die)
        
        doc = FreeCAD.ActiveDocument
        objs = GetListOfObjects(FreeCAD, doc)

        Color_Objects(Gui,objs[0],body_color)
        Color_Objects(Gui,objs[1],top_color)
        Color_Objects(Gui,objs[2],pins_color)
        Color_Objects(Gui,objs[3],pinmark_color)
        if die:
        	Color_Objects(Gui,objs[4],die_color)

        col_body=Gui.ActiveDocument.getObject(objs[0].Name).DiffuseColor[0]
        col_top=Gui.ActiveDocument.getObject(objs[1].Name).DiffuseColor[0]
        col_pin=Gui.ActiveDocument.getObject(objs[2].Name).DiffuseColor[0]
        col_pinmark=Gui.ActiveDocument.getObject(objs[3].Name).DiffuseColor[0]
        if die:
        	col_die=Gui.ActiveDocument.getObject(objs[4].Name).DiffuseColor[0]
        	material_substitutions={
        	    col_body[:-1]:body_color_key,
        	    col_pin[:-1]:pins_color_key,
        	    col_top[:-1]:top_color_key,
        	    col_pinmark[:-1]:pinmark_color_key,
        	    col_die[:-1]:die_color_key
        	}
        else:
        	material_substitutions={
        	    col_body[:-1]:body_color_key,
        	    col_pin[:-1]:pins_color_key,
        	    col_top[:-1]:top_color_key,
        	    col_pinmark[:-1]:pinmark_color_key
        	}
        expVRML.say(material_substitutions)
        del objs

        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        if die:
        	objs=GetListOfObjects(FreeCAD, doc)
        	FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        doc.Label = CheckedModelName
        objs=GetListOfObjects(FreeCAD, doc)
        objs[0].Label = CheckedModelName
        restore_Main_Tools()
        #rotate if required
        if (all_params[variant].rotation!=0):
            rot= all_params[variant].rotation
            z_RotateObject(doc, rot)
        #out_dir=destination_dir+all_params[variant].dest_dir_prefix+'/'
        script_dir=os.path.dirname(os.path.realpath(__file__))
        #models_dir=script_dir+"/../_3Dmodels"
        expVRML.say(models_dir)
        out_dir=models_dir+destination_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        #out_dir="./generated_qfp/"
        # export STEP model
        exportSTEP(doc, ModelName, out_dir)
        if LIST_license[0]=="":
            LIST_license=Lic.LIST_int_license
            LIST_license.append("")
        Lic.addLicenseToStep(out_dir+'/', ModelName+".step", LIST_license,\
                           STR_licAuthor, STR_licEmail, STR_licOrgSys, STR_licOrg, STR_licPreProc)

        # scale and export Vrml model
        scale=1/2.54
        #exportVRML(doc,ModelName,scale,out_dir)
        objs=GetListOfObjects(FreeCAD, doc)
        expVRML.say("######################################################################")
        expVRML.say(objs)
        expVRML.say("######################################################################")
        export_objects, used_color_keys = expVRML.determineColors(Gui, objs, material_substitutions)
        export_file_name=out_dir+os.sep+ModelName+'.wrl'
        colored_meshes = expVRML.getColoredMesh(Gui, export_objects , scale)
        expVRML.writeVRMLFile(colored_meshes, export_file_name, used_color_keys, LIST_license)
        # Save the doc in Native FC format
        saveFCdoc(App, Gui, doc, ModelName,out_dir)
        #display BBox
        #FreeCADGui.ActiveDocument.getObject("Part__Feature").BoundingBox = True
        Gui.activateWorkbench("PartWorkbench")
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxometric()