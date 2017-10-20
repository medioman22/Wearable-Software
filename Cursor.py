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
import StickMan

mouse = [0,0]
parent = -1
ID = 0
name = ''
def mouseManage():
    global ID
    global parent
    global name

    color = glReadPixels( mouse[0] , Events.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_FLOAT )
    ID = 0
    parent = -1
    name = ''
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
    if parent == 0:
        if Events.mouse_click == True:
            Select = True
            for part in StickMan.selectedParts:
                if part == StickMan.parts[ID][StickMan.Data_id]:
                    Select = False
                    StickMan.selectedParts.remove(part)
                    break
            if Select == True:
                StickMan.selectedParts += [StickMan.parts[ID][StickMan.Data_id],]
        #Definitions.packagePreprocess[Graphics.vboCube][ID][1] = True
        name = ' (' + StickMan.parts[ID][StickMan.Data_id] + ')'
    elif parent == 1:
        if Events.mouse_click == True:
            if Sensors.selectedSens == ID:
                Sensors.selectedSens = 0
            else:
                Sensors.selectedSens = ID
        name = ' (' + 'sensor' + ')'
    if parent == 2:
        GUI.selectedGuiId = ID
    else:
        GUI.selectedGuiId = 0