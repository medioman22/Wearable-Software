import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import Definitions
import Events
import Graphics
import GUI
import Sensors
import State
import StickMan

mouse = [0,0]
parent = -1
ID = 0
name = ''
info = []
def mouseManage():
    global ID
    global parent
    global name
    global info

    color = glReadPixels( mouse[0] , GUI.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_FLOAT )
    ID = 0
    parent = -1
    name = ''
    info = []
    if color[0][0][0] != 0: # RED channel for parts ID
        parent = 0
        ID = color[0][0][0]*(len(StickMan.parts)-1)
    elif color[0][0][1] != 0: # GREEN channel for sensors ID
        parent = 1
        ID = color[0][0][1]*Sensors.countID
    elif color[0][0][2] != 0: # BLUE channel for gui ID
        parent = 2
        ID = color[0][0][2]*GUI.lenGui()
        name = ' (gui)'
        
    #convert float to int with errors management
    if ID - int(ID) >= 0.5:
        ID = int(ID + 0.5)
    else:
        ID = int(ID)
    
    if Events.setLookAt == True:
        if parent == 0 or parent == -1:
            StickMan.lookingAtID = ID
    # select part
    GUI.overGuiId = 0
    StickMan.overPartId = 0
    Sensors.overSensId = 0
    if parent == 0:
        StickMan.overPartId = ID
        if Events.mouse_click == True:
            # place sensor on body
            if GUI.guiType(GUI.selectedTemplate) == GUI.guiTemplate:
                color = Sensors.sensorGraphics[GUI.selectedTemplate-1][1]
                color = (color[0]/255., color[1]/255., color[2]/255.)
                Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(StickMan.parts[ID][StickMan.Data_id], Sensors.sensorGraphics[GUI.selectedTemplate-1][0], (0.,90,90), color)]
            # select limb
            else:
                Select = True
                for part in StickMan.selectedParts:
                    if part == StickMan.parts[ID][StickMan.Data_id]:
                        Select = False
                        StickMan.selectedParts.remove(part)
                        break
                if Select == True:
                    StickMan.selectedParts += [StickMan.parts[ID][StickMan.Data_id],]

        name = ' (' + StickMan.parts[ID][StickMan.Data_id] + ')'
    elif parent == 1:
        Sensors.overSensId = ID
        if Events.mouse_click == True:
            if Sensors.selectedSens == ID:
                Sensors.selectedSens = 0
            else:
                Sensors.selectedSens = ID

            
        for indices in Definitions.packageIndices[2]:
            pack = Definitions.packagePreprocess[indices[0]][indices[1]]
            if pack[Definitions.packID] == Sensors.overSensId:
                
                if Events.mouse_click == True:
                    if GUI.guiType(GUI.selectedTemplate) == GUI.guiTemplate:
                        color = Sensors.sensorGraphics[GUI.selectedTemplate-1][1]
                        color = (color[0]/255., color[1]/255., color[2]/255.)
                        Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(pack[Definitions.entity].attach, Sensors.sensorGraphics[GUI.selectedTemplate-1][0], (pack[Definitions.entity].x,pack[Definitions.entity].t,pack[Definitions.entity].s), color)]


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
        GUI.overGuiId = ID
        if Events.mouse_click == True:

            # windows
            if GUI.guiType(GUI.overGuiId) == GUI.guiWindow:
                if GUI.selectedWindow != ID - GUI.guiOffsetId(GUI.guiWindow):
                    GUI.selectedWindow = ID - GUI.guiOffsetId(GUI.guiWindow)
                else:
                    GUI.selectedWindow = 0
               
            # groupes
            if GUI.guiType(GUI.overGuiId) == GUI.guiGroup:
                if State.sensorFileName[GUI.overGuiId-1 - GUI.guiOffsetId(GUI.guiGroup)][1] == False:
                    State.sensorFileName[GUI.overGuiId-1 - GUI.guiOffsetId(GUI.guiGroup)][1] = True
                else:
                    State.sensorFileName[GUI.overGuiId-1 - GUI.guiOffsetId(GUI.guiGroup)][1] = False
                State.loadSensors()
                if GUI.selectedGroup != ID:
                    GUI.selectedGroup = ID
                else:
                    GUI.selectedGroup = 0

            # templates
            if GUI.guiType(GUI.overGuiId) == GUI.guiTemplate:
                if GUI.selectedTemplate != ID:
                    GUI.selectedTemplate = ID
                    State.loadZOI(Sensors.sensorGraphics[GUI.selectedTemplate-1])
                else:
                    State.loadZOI([""])
                    GUI.selectedTemplate = 0
    else:
        pass