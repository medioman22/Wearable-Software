import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import Events
import Definitions
import GUI
import StickMan

mouse = [0,0]
ID = 0
name = ''
def mouseManage():
    global ID
    global name

    color = glReadPixels( mouse[0] , Events.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_FLOAT )
    ID = 0
    name = ''
    if color[0][0][0] != 0: # RED channel for parts ID
        ID = color[0][0][0]*len(Definitions.packageStickMan)
    elif color[0][0][1] != 0: # GREEN channel for sensors ID
        ID = color[0][0][1]*len(Definitions.packageSensors) + 1
        name = ' (sensor)'
    elif color[0][0][2] != 0: # BLUE channel for gui ID
        ID = color[0][0][2]*GUI.lenGui() + 1
        name = ' (gui)'
        
    #convert float to int with errors management
    if ID < 0.5:
        ID = 0
    elif ID - int(ID) >= 0.5:
        ID = int(ID + 0.5)-1
    else:
        ID = int(ID)-1
            
    # select part
    if color[0][0][0] != 0:
        if Events.mouse_click == True:
            Select = True
            for part in StickMan.selectedParts:
                if part == StickMan.parts[ID][StickMan.Data_id]:
                    Select = False
                    StickMan.selectedParts.remove(part)
                    break
            if Select == True:
                StickMan.selectedParts += [StickMan.parts[ID][StickMan.Data_id],]
        Definitions.packageStickMan[ID][1] = True
        name = ' = ' + StickMan.parts[ID][StickMan.Data_id]
    if color[0][0][2] != 0:
        GUI.selectedGuiId = ID
    else:
        GUI.selectedGuiId = 0