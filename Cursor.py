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
    
    #r,g,b,a = glReadPixels( mouse[0] , GUI.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_UNSIGNED_BYTE )
    #print(r,g,b,a)

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
    elif ID.idCategory(overID) == ID.SENSOR or ID.idCategory(overID) == ID.ZOI:
        parent = 1
    elif ID.idCategory(overID) != 0:
        parent = 2
        
    if Events.setLookAt == True:
        if parent == 0 or parent == -1:
            StickMan.lookingAtID = overID
    # select part
    GUI.overGuiId = 0
    StickMan.overPartId = 0
    Sensors.overSensId = 0
    Muscles.OverMuscId = 0

    if parent == 0:
        StickMan.overPartId = overID
        if Events.mouse_click == True:
            # place sensor on body
            if GUI.selectedTemplate != "":
                for sensorData in Sensors.sensorGraphics:
                    if GUI.selectedTemplate == sensorData.type:
                        r,g,b,a = sensorData.color
                        color = (r/255., g/255., b/255.)
                        Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(StickMan.virtuMan.parts[overID-1].tag, sensorData.type, (0.,90,90), color)]
            # select limb
            else:
                Select = True
                for part in StickMan.selectedParts:
                    if part == StickMan.virtuMan.parts[overID-1].tag:
                        Select = False
                        StickMan.selectedParts.remove(part)
                        break
                if Select == True:
                    StickMan.selectedParts += [StickMan.virtuMan.parts[overID-1].tag,]

        name = ' (' + StickMan.virtuMan.parts[overID-1].tag + ')'
    elif parent == 1:
        Sensors.overSensId = overID
        if Events.mouse_click == True:
            if Sensors.selectedSens == overID:
                Sensors.selectedSens = 0
            else:
                Sensors.selectedSens = overID

            
        for indices in Definitions.packageIndices[2]:
            pack = Definitions.packagePreprocess[indices[0]][indices[1]]
            if pack[Definitions.packID] == Sensors.overSensId:
                
                if Events.mouse_click == True:
                    if GUI.selectedTemplate != "":
                        for sensorData in Sensors.sensorGraphics:
                            if GUI.selectedTemplate == sensorData.type:
                                r,g,b,a = sensorData.color
                                color = (r/255., g/255., b/255.)
                                Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(pack[Definitions.entity].attach, sensorData.type, (pack[Definitions.entity].x,pack[Definitions.entity].t,pack[Definitions.entity].s), color)]
                        
                                Sensors.virtuSens[len(Sensors.virtuSens)-1].tag = pack[Definitions.entity].tag

                if Events.deleteSens == True:
                    removeId = pack[Definitions.entity].id
                    if removeId < len(Sensors.virtuSens):
                        del Sensors.virtuSens[removeId]
                    else:
                        del Sensors.zoiSens[removeId - len(Sensors.virtuSens)]

                name = ' (' + pack[Definitions.entity].type + ')'
                info = [str(pack[Definitions.entity].x) + ' ' + str(pack[Definitions.entity].t) + ' ' + str(pack[Definitions.entity].s), str(pack[Definitions.entity].id), str(pack[Definitions.entity].tag)]
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
                State.sensorFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][1] = not State.sensorFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][1]
                State.loadGroups()
                if GUI.selectedGroup != overID:
                    GUI.selectedGroup = overID
                else:
                    GUI.selectedGroup = 0
            elif Events.setLookAt == True:
                Events.rename = State.sensorFileName[GUI.overGuiId-1 - ID.offsetId(ID.GROUPE)][0] + State.extension
                Events.renameType = ID.GROUPE

        # templates
        if ID.idCategory(GUI.overGuiId) == ID.TEMPLATE:
            if Events.mouse_click == True:
                if GUI.selectedTemplate != Sensors.sensorGraphics[overID-1 - ID.offsetId(ID.TEMPLATE)].type:
                    GUI.selectedTemplate = Sensors.sensorGraphics[overID-1 - ID.offsetId(ID.TEMPLATE)].type
                    State.loadZOI(GUI.selectedTemplate)
                else:
                    State.loadZOI("")
                    GUI.selectedTemplate = ""
            elif Events.setLookAt == True:
                #State.loadZOI("")
                #GUI.selectedTemplate = ""
                Events.rename = Sensors.sensorGraphics[GUI.overGuiId-1 - ID.offsetId(ID.TEMPLATE)].type + State.extension
                Events.renameType = ID.TEMPLATE
    if parent == 3:
        Muscles.OverMuscId = overID
        name = ' (' + Muscles.muscles[overID-1][Muscles.Tag] + ')'
        if Events.mouse_click == True:
            # place sensor on body
            for sensorData in sensorGraphics:
                if GUI.selectedTemplate == sensorData.type:
                    r,g,b,a = sensorData.color
                    color = (r/255., g/255., b/255.)
                    Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(Muscles.muscles[Muscles.OverMuscId-1][Muscles.Tag], sensorData.type, (0.,90,90), color)]
            # select limb
            else:
                if Muscles.SelectedMuscId != overID:
                    Muscles.SelectedMuscId = overID
                else:
                    Muscles.SelectedMuscId = 0
    else:
        pass