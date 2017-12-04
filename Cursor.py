import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import Definitions
import Events
import Graphics
import GUI
import ID
import Limbs
import Muscles
import Sensors
import State
import StickMan

mouse = [0,0]
parent = -1
overID = 0
name = ''
info = []
def mouseManage():
    global overID
    global parent
    global name
    global info
    
    color = glReadPixels( mouse[0] , GUI.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_FLOAT )
    r,g,b,a = 255*color[0][0]
    r = int(r)
    g = int(g)
    b = int(b)
    a = int(a)
    overID = ID.color2id(r,g,b)
    name = ''
    info = []

    parent = -1
    if ID.idCategory(overID) == ID.LIMB:
        parent = 0
    elif ID.idCategory(overID) == ID.MUSCLE:
        parent = 3
    elif ID.idCategory(overID) == ID.SENSOR or ID.idCategory(overID) == ID.ZOI:
        parent = 1
    elif ID.idCategory(overID) != 0:
        parent = 2
        
    if Events.setLookAt == True:
        if parent == -1:
            Limbs.lookingAtID = 0
        elif parent == 0:
            Limbs.lookingAtID = overID
    # select part
    GUI.overGuiId = 0
    Limbs.overLimbId = 0
    Sensors.overSensId = 0
    Muscles.OverMuscId = 0

    if parent == 0:
        Limbs.overLimbId = overID
        if Events.mouse_click == True:
            # place sensor on body
            if GUI.selectedTemplate != "":
                for sensorData in Sensors.sensorGraphics:
                    if GUI.selectedTemplate == sensorData.type:
                        r,g,b,a = sensorData.color
                        color = (r/255., g/255., b/255.)
                        Sensors.newSens = [Sensors.sensors(StickMan.virtuMan.limbs[overID - ID.offsetId(ID.LIMB)].tag, sensorData.type, (0.,90,90), color)]
            # select limb
            else:
                Select = True
                for part in StickMan.selectedLimbs:
                    if part == StickMan.virtuMan.limbs[overID-1].tag:
                        Select = False
                        StickMan.selectedLimbs.remove(part)
                        break
                if Select == True:
                    StickMan.selectedLimbs += [StickMan.virtuMan.limbs[overID - ID.offsetId(ID.LIMB)].tag,]

        name = ' (' + StickMan.virtuMan.limbs[overID-1].tag + ')'
    elif parent == 1:
        Sensors.overSensId = overID
        if Events.mouse_click == True:
            if Sensors.selectedSens == overID:
                Sensors.selectedSens = 0
            else:
                Sensors.selectedSens = overID

            
        for sensor in Sensors.virtuSens + Sensors.zoiSens:
            if sensor.id == Sensors.overSensId:
                if Events.mouse_click == True:
                    if GUI.selectedTemplate != "" and ID.idCategory(sensor.id) == ID.ZOI:
                        for sensorData in Sensors.sensorGraphics:
                            if GUI.selectedTemplate == sensorData.type:
                                r,g,b,a = sensorData.color
                                color = (r/255., g/255., b/255.)
                                Sensors.newSens = [Sensors.sensors(sensor.attach, sensorData.type, (sensor.x,sensor.t,sensor.s), color)]
                                Sensors.newSens[0].tag = sensor.tag

                if Events.deleteSens == True:
                    if ID.idCategory(sensor.id) == ID.SENSOR:
                        del Sensors.virtuSens[sensor.id - ID.offsetId(ID.SENSOR)]

                name = ' (' + sensor.type + ')'
                info = [str(sensor.x) + ' ' + str(sensor.t) + ' ' + str(sensor.s), str(sensor.id), str(sensor.tag)]
                break
        
    if parent == 2:
        GUI.overGuiId = overID

        # windows
        if ID.idCategory(GUI.overGuiId) == ID.PANNEL:
            if Events.mouse_click == True:
                if GUI.selectedWindow != overID - ID.offsetId(ID.PANNEL):
                    GUI.selectedWindow = overID - ID.offsetId(ID.PANNEL)
                else:
                    GUI.selectedWindow = 0
               
        # groupes
        if ID.idCategory(GUI.overGuiId) == ID.GROUPE:
            if Events.mouse_click == True:
                State.groupFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][1] = not State.groupFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][1]
                Events.loadGroup = True
                if GUI.selectedGroup != overID:
                    GUI.selectedGroup = overID
                else:
                    GUI.selectedGroup = 0
            elif Events.setLookAt == True:
                Events.rename = State.groupFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][0]
                Events.renameType = ID.GROUPE

        # templates
        if ID.idCategory(GUI.overGuiId) == ID.TEMPLATE:
            if Events.mouse_click == True:
                if GUI.selectedTemplate != Sensors.sensorGraphics[overID-1 - ID.offsetId(ID.TEMPLATE)].type:
                    GUI.selectedTemplate = Sensors.sensorGraphics[overID-1 - ID.offsetId(ID.TEMPLATE)].type
                else:
                    GUI.selectedTemplate = ""
                GUI.selectedZoi = ""
                Events.loadZoi = True
            elif Events.setLookAt == True:
                Events.rename = Sensors.sensorGraphics[GUI.overGuiId-1 - ID.offsetId(ID.TEMPLATE)].type
                Events.renameType = ID.TEMPLATE

        # zoi
        if ID.idCategory(GUI.overGuiId) == ID.ZOILIST:
            if Events.mouse_click == True:
                if GUI.selectedZoi != State.zoiFileName[overID-1 - ID.offsetId(ID.ZOILIST)]:
                    GUI.selectedZoi = State.zoiFileName[overID-1 - ID.offsetId(ID.ZOILIST)]
                else:
                    GUI.selectedZoi = ""
                Events.loadZoi = True
            elif Events.setLookAt == True:
                Events.rename = GUI.selectedZoi
                Events.renameType = ID.ZOILIST
        

    if parent == 3:
        Muscles.OverMuscId = overID
        name = ' (' + StickMan.virtuMan.muscles[overID - ID.offsetId(ID.MUSCLE)].tag + ')'
        if Events.mouse_click == True:
            # place sensor on body
            if GUI.selectedTemplate != "":
                for sensorData in Sensors.sensorGraphics:
                    if GUI.selectedTemplate == sensorData.type:
                        r,g,b,a = sensorData.color
                        color = (r/255., g/255., b/255.)
                        Sensors.newSens = [Sensors.sensors(StickMan.virtuMan.muscles[Muscles.OverMuscId - ID.offsetId(ID.MUSCLE)].tag, sensorData.type, (0.,90,90), color)]
            # select limb
            else:
                if Muscles.SelectedMuscId != overID:
                    Muscles.SelectedMuscId = overID
                else:
                    Muscles.SelectedMuscId = 0
    else:
        pass
    
    Events.mouse_click = False
    Events.setLookAt = False