#
#   File : Cursor.py
#   
#   Code written by : Johann Heches
#
#   Description : Manage mouse events by checking the ID buffer values.
#   


import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import Definitions
import Events
import Graphics
import ID
import Limbs
import Muscles
import Sensors
import State
import Avatar
import UI

mouse = [0,0]
parent = -1
overID = 0
def mouseManage():
    global overID
    global parent
    
    color = glReadPixels( mouse[0] , Graphics.display[1] - mouse[1] - 1 , 1 , 1 , GL_RGBA , GL_FLOAT )
    r,g,b,a = 255*color[0][0]
    r = int(r)
    g = int(g)
    b = int(b)
    a = int(a)
    overID = ID.color2id(r,g,b)

    parent = -1
    if ID.idCategory(overID) == ID.LIMB:
        parent = 0
    elif ID.idCategory(overID) == ID.MUSCLE:
        parent = 1
    elif ID.idCategory(overID) == ID.SENSOR or ID.idCategory(overID) == ID.ZOI:
        parent = 2
        
    if Events.setLookAt == True:
        if parent == -1:
            Limbs.lookingAtID = 0
        elif parent == 0:
            Limbs.lookingAtID = overID
    # select part
    ID.overGuiId = 0
    Limbs.overLimbId = 0
    Sensors.overSensId = 0
    Muscles.OverMuscId = 0

    if parent == 0:
        Limbs.overLimbId = overID
        if Events.mouse_click == True:
            # place sensor on limb
            if Sensors.selectedTemplate != "":
                for sensorData in Sensors.sensorGraphics:
                    if Sensors.selectedTemplate == sensorData.type:
                        r,g,b,a = sensorData.color
                        color = (r/255., g/255., b/255.)
                        Sensors.newSens = [Sensors.sensors(Avatar.virtuMan.limbs[overID - ID.offsetId(ID.LIMB)].tag, sensorData.type, (0.,90,90), color)]
            # select limb
            else:
                Select = True
                for part in Avatar.selectedLimbs:
                    if part == Avatar.virtuMan.limbs[overID-1].tag:
                        Select = False
                        Avatar.selectedLimbs.remove(part)
                        break
                if Select == True:
                    Avatar.selectedLimbs += [Avatar.virtuMan.limbs[overID - ID.offsetId(ID.LIMB)].tag,]

    elif parent == 1:
        Muscles.OverMuscId = overID
        if Events.mouse_click == True:
            # place sensor on muscle
            if Sensors.selectedTemplate != "":
                for sensorData in Sensors.sensorGraphics:
                    if Sensors.selectedTemplate == sensorData.type:
                        r,g,b,a = sensorData.color
                        color = (r/255., g/255., b/255.)
                        Sensors.newSens = [Sensors.sensors(Avatar.virtuMan.muscles[Muscles.OverMuscId - ID.offsetId(ID.MUSCLE)].tag, sensorData.type, (0.,90,90), color)]
            # select muscle
            else:
                if Muscles.SelectedMuscId != overID:
                    Muscles.SelectedMuscId = overID
                else:
                    Muscles.SelectedMuscId = 0

    elif parent == 2:
        Sensors.overSensId = overID
        # select / deselect sensor
        if Events.mouse_click == True:
            if Sensors.selectedSens == overID:
                UI.uiSensor.table.clearSelection()
                Sensors.selectedSens = 0
            else:
                Sensors.selectedSens = overID
                try:
                    UI.uiSensor.table.selectRow(Sensors.selectedSens - ID.offsetId(ID.SENSOR))
                except:
                    pass
    
        # place sensor on zoi
        if Events.mouse_click == True and Sensors.selectedTemplate != "":
            for sensor in Sensors.zoiSens:
                if sensor.id == Sensors.overSensId:
                    for sensorData in Sensors.sensorGraphics:
                        if Sensors.selectedTemplate == sensorData.type:
                            r,g,b,a = sensorData.color
                            color = (r/255., g/255., b/255.)
                            Sensors.newSens = [Sensors.sensors(sensor.attach, sensorData.type, (sensor.x,sensor.t,sensor.s), color)]
                            Sensors.newSens[0].tag = sensor.tag
                            UI.uiSensor.table.clearSelection()
                            Sensors.selectedSens = 0
                            break
                    break

    # delete selected sensor
    if Events.deleteSens == True:
        for sensor in Sensors.virtuSens:
            if sensor.id == Sensors.selectedSens:
                UI.uiSensor.table.clearSelection()
                del Sensors.virtuSens[sensor.id - ID.offsetId(ID.SENSOR)]
                Sensors.selectedSens = 0
                UI.uiSensor.updateTable()
                break
        

    Events.mouse_click = False
    Events.setLookAt = False