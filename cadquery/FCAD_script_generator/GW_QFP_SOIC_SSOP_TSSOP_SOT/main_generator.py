# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This is derived from a cadquery script for generating QFP models in X3D format.
#
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
#
# Dimensions are from Jedec MS-026D document.

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

__title__ = "make GullWings ICs 3D models"
__author__ = "maurice and hyOzd"
__Comment__ = 'make GullWings ICs 3D models exported to STEP and VRML for Kicad StepUP script'

___ver___ = "1.3.9 14/02/2017"

# thanks to Frank Severinsen Shack for including vrml materials

import argparse
global save_memory
save_memory=False #reducing memory consuming for all generation params
footprints_dir=None

from math import tan, radians, sqrt
from collections import namedtuple

import sys, os
import datetime
from datetime import datetime
sys.path.append("../_tools")
import exportPartToVRML as expVRML
import shaderColors

body_color_key = "black body"
body_color = shaderColors.named_colors[body_color_key].getDiffuseFloat()
pins_color_key = "metal grey pins"
pins_color = shaderColors.named_colors[pins_color_key].getDiffuseFloat()
mark_color_key = "light brown label"
mark_color = shaderColors.named_colors[mark_color_key].getDiffuseFloat()


# maui start
import FreeCAD, Draft, FreeCADGui
import ImportGui
import FreeCADGui as Gui
#from Gui.Command import *

import logging
logging.getLogger('builder').addHandler(logging.NullHandler())
#logger = logging.getLogger('builder')
#logging.info("Begin")

outdir=os.path.dirname(os.path.realpath(__file__)+"/../_3Dmodels")
scriptdir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(outdir)
sys.path.append(scriptdir)

#import PySide
#from PySide import QtGui, QtCore
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
 CutObjs_wColors, checkRequirements, closeCurrentDoc

try:
    # Gui.SendMsgToActiveView("Run")
    from Gui.Command import *
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

import cq_parameters_soic  # modules parameters
from cq_parameters_soic import *


import cq_parameters_qfp  # modules parameters
from cq_parameters_qfp import *

footprints_dir_SSOP=None
import cq_parameters_ssop  # modules parameters
from cq_parameters_ssop import *

import cq_parameters_tssop  # modules parameters
from cq_parameters_tssop import *

import cq_parameters_sot  # modules parameters
from cq_parameters_sot import *

footprints_dir_diodes=None
import cq_parameters_diode  # modules parameters
from cq_parameters_diode import *

# all_params= all_params_soic.copy()
# all_params.update(all_params_qfp)

# all_params1= all_params_soic.copy()
# all_params1.update(all_params_qfp)
# all_params= all_params1.copy()
# all_params.update(all_params_ssop)

all_params= kicad_naming_params_soic.copy()
all_params.update(kicad_naming_params_qfp)
all_params.update(kicad_naming_params_ssop)
all_params.update(all_params_tssop)
all_params.update(kicad_naming_params_sot)  
all_params.update(kicad_naming_params_diode)  


# all_params = dict(all_params1.items() | all_params2.items())

def make_gw(params):

    c  = params.c
    the  = params.the
    tb_s  = params.tb_s
    ef  = params.ef
    cc1 = params.cc1
    fp_s = params.fp_s
    fp_r  = params.fp_r
    fp_d  = params.fp_d
    fp_z  = params.fp_z
    R1  = params.R1
    R2  = params.R2
    S  = params.S
# automatically calculated    L  = params.L
    D1  = params.D1
    E1  = params.E1
    E   = params.E
    A1  = params.A1
    A2  = params.A2
    b   = params.b
    e   = params.e
    npx = params.npx
    npy = params.npy
    mN  = params.modelName
    rot = params.rotation
    dest_dir_pref = params.dest_dir_prefix
    if params.excluded_pins:
        excluded_pins = params.excluded_pins
    else:
        excluded_pins=() ##no pin excluded 

    A = A1 + A2
    A2_t = (A2-c)/2 # body top part height
    A2_b = A2_t     # body bottom part height
    D1_b = D1-2*tan(radians(the))*A2_b # bottom width
    E1_b = E1-2*tan(radians(the))*A2_b # bottom length
    D1_t1 = D1-tb_s # top part bottom width
    E1_t1 = E1-tb_s # top part bottom length
    D1_t2 = D1_t1-2*tan(radians(the))*A2_t # top part upper width
    E1_t2 = E1_t1-2*tan(radians(the))*A2_t # top part upper length

    epad_rotation = 0.0
    epad_offset_x = 0.0
    epad_offset_y = 0.0

    if params.epad:
        #if isinstance(params.epad, float):
        if not isinstance(params.epad, tuple):                                              
            sq_epad = False
            epad_r = params.epad
        else:
            sq_epad = True
            D2 = params.epad[0]
            E2 = params.epad[1]
            if len(params.epad) > 2:
                epad_rotation = params.epad[2]
            if len(params.epad) > 3:
                if isinstance (params.epad[3], str):
                    if params.epad[3] == '-topin':
                        epad_offset_x = (D1_b/2-D2/2) * -1
                    elif params.epad[3] == '+topin':
                        epad_offset_x = D1_b/2-D2/2
                else:
                    epad_offset_x = params.epad[3]
            if len(params.epad) > 4:
                if isinstance (params.epad[4], str):
                    if params.epad[4] == '-topin':
                        epad_offset_y = (E1_b/2-E2/2) * -1
                    elif params.epad[4] == '+topin':
                        epad_offset_y = E1_b/2-E2/2
                else:
                    epad_offset_y = params.epad[4]

    # calculated dimensions for body    
    # checking pin lenght compared to overall width
    # d=(E-E1 -2*(S+L)-2*(R1))
    L=(E-E1-2*(S+R1))/2
    FreeCAD.Console.PrintMessage('E='+str(E)+';E1='+str(E1)+';S='+str(S)+';L='+str(L)+'\r\n')

    ## d=(E-E1 -2*(S+L)-2*(R1))
    ## FreeCAD.Console.PrintMessage('E='+str(E)+';E1='+str(E1)+';S='+str(S)+';L='+str(L)+';d='+str(d)+'\r\n')
    ## #if (d > 0):
    ## if (d > c/10):  #tolerance
    ##     L=L+d/2
    ##     FreeCAD.Console.PrintMessage(str(E-E1-2*(S+L))+'\r\nincreasing pin lenght\r\n')
    ## if (d < -c/10):  #tolerance
    ##     L=L+d/2
    ##     FreeCAD.Console.PrintMessage(str(E-E1-2*(S+L))+'\r\ntrimming pin lenght\r\n')


    # FreeCAD.Console.PrintMessage('\r\n'+str(A1)+';'+str(D1_b)+';'+str(E1_b)+'\r\n')
    # FreeCAD.Console.PrintMessage('\r\n'+str(A2_b)+';'+str(D1)+';'+str(E1)+';'+str(c)+'\r\n')
    # FreeCAD.Console.PrintMessage('\r\n'+str(D1_t1)+';'+str(E1_t1)+';'+str(A2_t)+'\r\n')
    # FreeCAD.Console.PrintMessage('\r\n'+str(D1_t2)+';'+str(E1_t2)+';'+str(ef)+'\r\n')
    # sleep
    ## if ef!=0:
    ##     case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
    ##          workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
    ##          rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
    ##          loft(ruled=True).faces(">Z").fillet(ef)
    ## else:
    ##     case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
    ##          workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
    ##          rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
    ##          loft(ruled=True).faces(">Z")
    ##
    ## # fillet the corners
    ## if ef!=0:
    ##     BS = cq.selectors.BoxSelector    
    ##     case = case.edges(BS((D1_t2/2, E1_t2/2, 0), (D1/2+0.1, E1/2+0.1, A2))).fillet(ef)
    ##     case = case.edges(BS((-D1_t2/2, E1_t2/2, 0), (-D1/2-0.1, E1/2+0.1, A2))).fillet(ef)
    ##     case = case.edges(BS((-D1_t2/2, -E1_t2/2, 0), (-D1/2-0.1, -E1/2-0.1, A2))).fillet(ef)
    ##     case = case.edges(BS((D1_t2/2, -E1_t2/2, 0), (D1/2+0.1, -E1/2-0.1, A2))).fillet(ef)

    ## cc1 = 0.25 #0.45 chamfer of the 1st pin corner
    ## cc = 0.25  # chamfer of the other corners

    # calculate chamfers
    totpinwidthx = (npx-1)*e+b # total width of all pins on the X side
    totpinwidthy = (npy-1)*e+b # total width of all pins on the Y side

    if cc1!=0:
        cc1 = abs(min((D1-totpinwidthx)/2., (E1-totpinwidthy)/2.,cc1) - 0.5*tb_s)
        cc1 = min(cc1, max_cc1)
    # cc = cc1/2.
    cc=cc1

    def crect(wp, rw, rh, cv1, cv):
        """
        Creates a rectangle with chamfered corners.
        wp: workplane object
        rw: rectangle width
        rh: rectangle height
        cv1: chamfer value for 1st corner (lower left)
        cv: chamfer value for other corners
        """
        points = [
        #    (-rw/2., -rh/2.+cv1),
            (-rw/2., rh/2.-cv),
            (-rw/2.+cv, rh/2.),
            (rw/2.-cv, rh/2.),
            (rw/2., rh/2.-cv),
            (rw/2., -rh/2.+cv),
            (rw/2.-cv, -rh/2.),
            (-rw/2.+cv1, -rh/2.),
            (-rw/2., -rh/2.+cv1)
        ]
        #return wp.polyline(points)
        return wp.polyline(points).wire() #, forConstruction=True)
     
    def crect_old(wp, rw, rh, cv1, cv):
        """
        Creates a rectangle with chamfered corners.
        wp: workplane object
        rw: rectangle width
        rh: rectangle height
        cv1: chamfer value for 1st corner (lower left)
        cv: chamfer value for other corners
        """
        
        points = [
            (-rw/2., -rh/2.+cv1),
            (-rw/2., rh/2.-cv),
            (-rw/2.+cv, rh/2.),
            (rw/2.-cv, rh/2.),
            (rw/2., rh/2.-cv),
            (rw/2., -rh/2.+cv),
            (rw/2.-cv, -rh/2.),
            (-rw/2.+cv1, -rh/2.),
            (-rw/2., -rh/2.+cv1)
        ]
        #print(points)
        #vecs = [wp for p in points]
        #w = Wire.makePolygon(vecs)
        return wp.polyline(points).wire() #, forConstruction=True)
        #return w

    if cc1!=0:
        case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).moveTo(-D1_b/2., -E1_b/2.+(cc1-(D1-D1_b)/4.))
        case = crect(case, D1_b, E1_b, cc1-(D1-D1_b)/4., cc-(D1-D1_b)/4.)  # bottom edges
        #show(case)
        case = case.pushPoints([(0,0)]).workplane(offset=A2_b).moveTo(-D1/2, -E1/2+cc1)
        case = crect(case, D1, E1, cc1, cc)     # center (lower) outer edges
        #show(case)
        case = case.pushPoints([(0,0)]).workplane(offset=c).moveTo(-D1/2,-E1/2+cc1)
        case = crect(case, D1,E1,cc1, cc)       # center (upper) outer edges
        #show(case)
        #case=cq.Workplane(cq.Plane.XY()).workplane(offset=c).moveTo(-D1_t1/2,-E1_t1/2+cc1-(D1-D1_t1)/4.)
        case=case.pushPoints([(0,0)]).workplane(offset=0).moveTo(-D1_t1/2,-E1_t1/2+cc1-(D1-D1_t1)/4.)
        case = crect(case, D1_t1,E1_t1, cc1-(D1-D1_t1)/4., cc-(D1-D1_t1)/4.) # center (upper) inner edges
        #show(case)
        #stop
        cc1_t = cc1-(D1-D1_t2)/4. # this one is defined because we use it later
        case = case.pushPoints([(0,0)]).workplane(offset=A2_t).moveTo(-D1_t2/2,-E1_t2/2+cc1_t)
        #cc1_t = cc1-(D1-D1_t2)/4. # this one is defined because we use it later
        case = crect(case, D1_t2,E1_t2, cc1_t, cc-(D1-D1_t2)/4.) # top edges
        #show(case)
        if ef!=0:
            case = case.loft(ruled=True).faces(">Z").fillet(ef)
        else:
            case = case.loft(ruled=True).faces(">Z")
    else:
        if ef!=0:
            case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
                workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
                rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
                loft(ruled=True).faces(">Z").fillet(ef)
        else:
            case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
                workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
                rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
                loft(ruled=True).faces(">Z")
        # fillet the corners
        if ef!=0:
            BS = cq.selectors.BoxSelector
            case = case.edges(BS((D1_t2/2, E1_t2/2, 0), (D1/2+0.1, E1/2+0.1, A2))).fillet(ef)
            case = case.edges(BS((-D1_t2/2, E1_t2/2, 0), (-D1/2-0.1, E1/2+0.1, A2))).fillet(ef)
            case = case.edges(BS((-D1_t2/2, -E1_t2/2, 0), (-D1/2-0.1, -E1/2-0.1, A2))).fillet(ef)
            case = case.edges(BS((D1_t2/2, -E1_t2/2, 0), (D1/2+0.1, -E1/2-0.1, A2))).fillet(ef)    
    #fp_s = True
    if fp_r == 0:
            global place_pinMark
            place_pinMark=False
            fp_r = 0.1
    if fp_s == False:
        pinmark = cq.Workplane(cq.Plane.XY()).workplane(offset=A).box(fp_r, E1_t2-fp_d, fp_z*2) #.translate((E1/2,0,A1)).rotate((0,0,0), (0,0,1), 90)
        #translate the object  
        pinmark=pinmark.translate((-D1_t2/2+fp_r/2.+fp_d/2,0,0)) #.rotate((0,0,0), (0,1,0), 0)
    else:
        # first pin indicator is created with a spherical pocket
        
        sphere_r = (fp_r*fp_r/2 + fp_z*fp_z) / (2*fp_z)
        sphere_z = A + sphere_r * 2 - fp_z - sphere_r
        # Revolve a cylinder from a rectangle
        # Switch comments around in this section to try the revolve operation with different parameters
        ##cylinder =
        #pinmark=cq.Workplane("XZ", (-D1_t2/2+fp_d+fp_r, -E1_t2/2+fp_d+fp_r, A)).rect(sphere_r/2, -fp_z, False).revolve()
        pinmark=cq.Workplane("XZ", (-D1_t2/2+fp_d+fp_r, -E1_t2/2+fp_d+fp_r, A)).rect(fp_r/2, -fp_z, False).revolve()
    
    

    #result = cadquery.Workplane("XY").rect(rectangle_width, rectangle_length, False).revolve(angle_degrees)
    #result = cadquery.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5,-5))
    #result = cadquery.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5, -5),(-5, 5))
    #result = cadquery.Workplane("XY").rect(rectangle_width, rectangle_length).revolve(angle_degrees,(-5,-5),(-5,5), False)
    
    ## color_attr=(255,255,255,0)
    ## show(pinmark, color_attr)
    ##sphere = cq.Workplane("XY", (-D1_t2/2+fp_d+fp_r, -E1_t2/2+fp_d+fp_r, sphere_z)). \
    ##         sphere(sphere_r)
    # color_attr=(255,255,255,0)
    # show(sphere, color_attr)
    #case = case.cut(sphere)
    if (color_pin_mark==False) and (place_pinMark==True):
        case = case.cut(pinmark)

    # calculated dimensions for pin
    R1_o = R1+c # pin upper corner, outer radius
    R2_o = R2+c # pin lower corner, outer radius

    # Create a pin object at the center of top side.
    bpin = cq.Workplane("YZ", (0,E1/2,0,)). \
        moveTo(-tb_s, A1+A2_b). \
        line(S+tb_s, 0). \
        threePointArc((S+R1/sqrt(2), A1+A2_b-R1*(1-1/sqrt(2))),
                      (S+R1, A1+A2_b-R1)). \
        line(0, -(A1+A2_b-R1-R2_o)). \
        threePointArc((S+R1+R2_o*(1-1/sqrt(2)), R2_o*(1-1/sqrt(2))),
                      (S+R1+R2_o, 0)). \
        line(L-R2_o, 0). \
        line(0, c). \
        line(-(L-R2_o), 0). \
        threePointArc((S+R1+R2_o-R2/sqrt(2), c+R2*(1-1/sqrt(2))),
                      (S+R1+R2_o-R1, c+R2)). \
        lineTo(S+R1+c, A1+A2_b-R1). \
        threePointArc((S+R1_o/sqrt(2), A1+A2_b+c-R1_o*(1-1/sqrt(2))),
                      (S, A1+A2_b+c)). \
        line(-S-tb_s, 0).close().extrude(b).translate((-b/2,0,0))

    pins = []
    pincounter = 1
    first_pos_x = (npx-1)*e/2
    for i in range(npx):
        if pincounter not in excluded_pins:
            pin = bpin.translate((first_pos_x-i*e, 0, 0)).\
                rotate((0,0,0), (0,0,1), 180)
            pins.append(pin)
        pincounter += 1
    
    first_pos_y = (npy-1)*e/2
    for i in range(npy):
        if pincounter not in excluded_pins:
            pin = bpin.translate((first_pos_y-i*e, (D1-E1)/2, 0)).\
                rotate((0,0,0), (0,0,1), 270)
            pins.append(pin)
        pincounter += 1

    for i in range(npx):
        if pincounter not in excluded_pins:
            pin = bpin.translate((first_pos_x-i*e, 0, 0))
            pins.append(pin)
        pincounter += 1
    
    for i in range(npy):
        if pincounter not in excluded_pins:
            pin = bpin.translate((first_pos_y-i*e, (D1-E1)/2, 0)).\
                rotate((0,0,0), (0,0,1), 90)
            pins.append(pin)
        pincounter += 1

    # create exposed thermal pad if requested
    if params.epad:
        if sq_epad:
            pins.append(cq.Workplane("XY").box(D2, E2, A1).translate((epad_offset_x,epad_offset_y,A1/2)).rotate((0,0,0), (0,0,1), epad_rotation))
        else:
            #epad = cq.Workplane("XY", (0,0,A1/2)). \
            epad = cq.Workplane("XY"). \
            circle(epad_r). \
            extrude(A1)#.translate((0,0,A1/2))
            #extrude(A1+A1/10)
            pins.append(epad)
    # merge all pins to a single object
    merged_pins = pins[0]
    for p in pins[1:]:
        merged_pins = merged_pins.union(p)
    pins = merged_pins

    # extract pins from case
    case = case.cut(pins)
    #show(case)
    #show(pinmark)
    #show(pins)
    #stop
    return (case, pins, pinmark)

#################################################
import add_license as Lic

# when run from command line
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
    
    color_pin_mark=True
    if len(sys.argv) < 3:
        FreeCAD.Console.PrintMessage('No variant name is given! building SOIC-8_3.9x4.9mm_Pitch1.27mm')
        model_to_build='SOIC-8_3.9x4.9mm_Pitch1.27mm'
    else:
        model_to_build=sys.argv[2]
        if len(sys.argv)==4:
            FreeCAD.Console.PrintMessage(sys.argv[3]+'\r\n')
            if (sys.argv[3].find('no-pinmark-color')!=-1):
                color_pin_mark=False
            else:
                color_pin_mark=True
    save_memory=False #reducing memory consuming for all generation params
    if model_to_build == "all":
        #expVRML.sayerr("'all' is not supported for this families\nuse 'allSOIC' or 'allSSOP' or 'allSOT' or 'allQFP' or 'allTSSOP' instead")
        variants = all_params.keys()
        save_memory=True
    #elif model_to_build == "SOIC":
    elif model_to_build == "allSOIC":
        variants = kicad_naming_params_soic.keys()
        save_memory=True
    elif model_to_build == "allQFP":
        variants = kicad_naming_params_qfp.keys()
        save_memory=True
    elif model_to_build == "allSSOP":
        variants = kicad_naming_params_ssop.keys()
        #variants = all_params_ssop.keys()
        footprints_dir=footprints_dir_SSOP
        save_memory=True
    elif model_to_build == "allTSSOP":
        variants = all_params_tssop.keys()
        save_memory=True
    elif model_to_build == "allSOT":
        variants = kicad_naming_params_sot.keys() 
        save_memory=True
    elif model_to_build == "allDiodes":
        variants = kicad_naming_params_diode.keys()  
        footprints_dir=footprints_dir_diodes
        save_memory=True
    else:
        variants = [model_to_build]

    for variant in variants:
        place_pinMark=True ##default =True used to exclude pin mark to build sot23-3; sot23-5; sc70 (asimmetrical pins, no pinmark)

        FreeCAD.Console.PrintMessage('\r\n'+variant)
        if not variant in all_params:
            print("Parameters for %s doesn't exist in 'all_params', skipping." % variant)
            continue
        ModelName = all_params[variant].modelName
        CheckedModelName = ModelName.replace('.', '').replace('-', '_').replace('(', '').replace(')', '')
        Newdoc = App.newDocument(CheckedModelName)
        App.setActiveDocument(CheckedModelName)
        Gui.ActiveDocument=Gui.getDocument(CheckedModelName)
        body, pins, mark = make_gw(all_params[variant])

        show(body)
        show(pins)
        show(mark)
        
        doc = FreeCAD.ActiveDocument
        objs = GetListOfObjects(FreeCAD, doc)

        Color_Objects(Gui,objs[0],body_color)
        Color_Objects(Gui,objs[1],pins_color)
        Color_Objects(Gui,objs[2],mark_color)

        col_body=Gui.ActiveDocument.getObject(objs[0].Name).DiffuseColor[0]
        col_pin=Gui.ActiveDocument.getObject(objs[1].Name).DiffuseColor[0]
        col_mark=Gui.ActiveDocument.getObject(objs[2].Name).DiffuseColor[0]
        material_substitutions={
            col_body[:-1]:body_color_key,
            col_pin[:-1]:pins_color_key,
            col_mark[:-1]:mark_color_key
        }
        expVRML.say(material_substitutions)
        del objs
        objs=GetListOfObjects(FreeCAD, doc)
        if (color_pin_mark==True) and (place_pinMark==True):
            CutObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[2].Name)
        else:
            #removing pinMark
            App.getDocument(doc.Name).removeObject(objs[2].Name)
        del objs
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        doc.Label=CheckedModelName
        objs=GetListOfObjects(FreeCAD, doc)
        objs[0].Label=CheckedModelName
        restore_Main_Tools()
        #rotate if required
        if (all_params[variant].rotation!=0):
            rot= all_params[variant].rotation
            z_RotateObject(doc, rot)
        #out_dir=destination_dir+all_params[variant].dest_dir_prefix+'/'
        script_dir=os.path.dirname(os.path.realpath(__file__))
        ## models_dir=script_dir+"/../_3Dmodels"
        expVRML.say(models_dir)
        out_dir=models_dir+destination_dir+os.sep+all_params[variant].dest_dir_prefix
        #out_dir=script_dir+os.sep+destination_dir
        #out_dir=script_dir+os.sep+destination_dir+os.sep+all_params[variant].dest_dir_prefix
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
        if footprints_dir is not None and os.path.isdir(footprints_dir):
            #expVRML.say (ModelName)
            #stop
            sys.argv = ["fc", "dummy", footprints_dir+os.sep+ModelName, "savememory"]
            #setup = get_setup_file()  # << You need the parentheses
            expVRML.say(sys.argv[2])
            ksu_already_loaded=False
            ksu_present=False
            for i in QtGui.qApp.topLevelWidgets():
                if i.objectName() == "kicadStepUp":
                    ksu_already_loaded=True
            ksu_tab = FreeCADGui.getMainWindow().findChild(QtGui.QDockWidget, "kicadStepUp") #"kicad StepUp 3D tools")
            if ksu_tab:
                ksu_already_loaded=True
            if ksu_already_loaded!=True:
                try:
                    import kicadStepUptools
                    ksu_present=True
                    ksu_already_loaded=True
                    kicadStepUptools.KSUWidget.close()
                    #kicadStepUptools.KSUWidget.setWindowState(QtCore.Qt.WindowMinimized)
                    #kicadStepUptools.KSUWidget.destroy()
                    #for i in QtGui.qApp.topLevelWidgets():
                    #    if i.objectName() == "kicadStepUp":
                    #        i.deleteLater()
                    kicadStepUptools.KSUWidget.close()
                except:
                    ksu_present=False
                    expVRML.say("ksu not present")
            else:
                kicadStepUptools.KSUWidget.close()
                reload(kicadStepUptools)
                kicadStepUptools.KSUWidget.close()
                #kicadStepUptools.KSUWidget.setWindowState(QtCore.Qt.WindowMinimized)
                #kicadStepUptools.KSUWidget.destroy()
            
        #FreeCADGui.insert(u"C:\Temp\FCAD_sg\QFN_packages\QFN-12-1EP_3x3mm_Pitch0_5mm.kicad_mod")
        #FreeCADGui.insert(script_dir+os.sep+"ModelName.kicad_mod")
        if save_memory == False:
            Gui.activateWorkbench("PartWorkbench")
            Gui.SendMsgToActiveView("ViewFit")
            Gui.activeDocument().activeView().viewBottom()
            #Gui.activeDocument().activeView().viewAxometric()
        saveFCdoc(App, Gui, doc, ModelName,out_dir)
        if save_memory == True:
            closeCurrentDoc(doc.Label)
        #sys.argv = ["fc", "dummy", all]

        #saveFCdoc(App, Gui, doc, ModelName,out_dir)
        ##display BBox
        ##FreeCADGui.ActiveDocument.getObject("Part__Feature").BoundingBox = True
        #
        #if close_doc: #closing doc to avoid memory leak
        #    expVRML.say("closing doc to save memory")
        #    App.closeDocument(doc.Name)
        #    App.setActiveDocument("")
        #    App.ActiveDocument=None
        #    Gui.ActiveDocument=None#else:
        #    Gui.activateWorkbench("PartWorkbench")
        #    Gui.SendMsgToActiveView("ViewFit")
        #    Gui.activeDocument().activeView().viewAxometric()
        
        
    #sys.exit()  #to create model and exit