import math

import GUI
import Muscles
import Sensors
import StickMan

NONE = 0
LIMB = 1
MUSCLE = 2
SENSOR = 3
ZOI = 4
PANNEL = 5
TEMPLATE = 6
ZOILIST = 7
GROUPE = 8
POSTURE = 9


def setId(list):
    id = 0
    for entity in list:
        for part in entity:
            id += 1
            part.id = id

def id2color(ID):
    r = math.floor(ID/math.pow(2,16))
    g = math.floor((ID%math.pow(2,16))/math.pow(2,8))
    b = ID%math.pow(2,8)
    return [r,g,b]

def color2id(r,g,b):
    return int(r*math.pow(2,16) + g*math.pow(2,8) + b)

def idCategory(ID):
    if StickMan.virtuMan.limbs != [] and\
        ID >= StickMan.virtuMan.limbs[0].id and\
        ID <= StickMan.virtuMan.limbs[len(StickMan.virtuMan.limbs)-1].id:
            return LIMB
    if StickMan.virtuMan.muscles != [] and\
        ID >= StickMan.virtuMan.muscles[0].id and\
        ID <= StickMan.virtuMan.muscles[len(StickMan.virtuMan.muscles)-1].id:
            return MUSCLE
    if Sensors.virtuSens != [] and\
        ID >= Sensors.virtuSens[0].id and\
        ID <= Sensors.virtuSens[len(Sensors.virtuSens)-1].id:
            return SENSOR
    if Sensors.zoiSens != [] and\
        ID >= Sensors.zoiSens[0].id and\
        ID <= Sensors.zoiSens[len(Sensors.zoiSens)-1].id:
            return ZOI
    if GUI.guiPannel != [] and\
        ID >= GUI.guiPannel[0].id and\
        ID <= GUI.guiPannel[len(GUI.guiPannel)-1].id:
            return PANNEL
    if GUI.guiSensorTypes != [] and\
        ID >= GUI.guiSensorTypes[0].id and\
        ID <= GUI.guiSensorTypes[len(GUI.guiSensorTypes)-1].id:
            return TEMPLATE
    if GUI.guiSensorZoi != [] and\
        ID >= GUI.guiSensorZoi[0].id and\
        ID <= GUI.guiSensorZoi[len(GUI.guiSensorZoi)-1].id:
            return ZOILIST
    if GUI.guiSensorGroups != [] and\
        ID >= GUI.guiSensorGroups[0].id and\
        ID <= GUI.guiSensorGroups[len(GUI.guiSensorGroups)-1].id:
            return GROUPE
    if GUI.guiPostures != [] and\
        ID >= GUI.guiPostures[0].id and\
        ID <= GUI.guiPostures[len(GUI.guiPostures)-1].id:
            return POSTURE
    return NONE

def offsetId(type):
    if type == LIMB:
        return StickMan.virtuMan.limbs[0].id
    if type == MUSCLE:
        return StickMan.virtuMan.muscles[0].id
    if type == SENSOR:
        return Sensors.virtuSens[0].id
    if type == ZOI:
        return Sensors.zoiSens[0].id
    if type == PANNEL:
        return GUI.guiPannel[0].id -1
    if type == TEMPLATE:
        return GUI.guiSensorTypes[0].id -1
    if type == ZOILIST:
        return GUI.guiSensorZoi[0].id -1
    if type == GROUPE:
        return GUI.guiSensorGroups[0].id -1
    if type == POSTURE:
        return GUI.guiPostures[0].id -1