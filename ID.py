import math

import GUI
import Muscles
import Sensors
import StickMan

LIMB = 1
MUSCLE = 2
SENSOR = 3
ZOI = 4
PANNEL = 5
TEMPLATE = 6
GROUPE = 7


def setId(list):
    id = 0
    #print(len(list))
    for entity in list:
        #print(len(entity))
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
    if ID >= StickMan.virtuMan.parts[0].id and\
        ID <= StickMan.virtuMan.parts[len(StickMan.virtuMan.parts)-1].id:
            return LIMB
    #if ID >= Muscles.~~~~.id and\
    #    ID <= Muscles.~~~~[len(Muscles.~~~~)-1].id:
    #        return MUSCLE
    if Sensors.virtuSens != [] and\
        ID >= Sensors.virtuSens[0].id and\
        ID <= Sensors.virtuSens[len(Sensors.virtuSens)-1].id:
            return SENSOR
    if Sensors.zoiSens != [] and\
        ID >= Sensors.zoiSens[0].id and\
        ID <= Sensors.zoiSens[len(Sensors.zoiSens)-1].id:
            return ZOI
    if ID >= GUI.guiPannel[0].id and\
        ID <= GUI.guiPannel[len(GUI.guiPannel)-1].id:
            return PANNEL
    if ID >= GUI.guiSensorTypes[0].id and\
        ID <= GUI.guiSensorTypes[len(GUI.guiSensorTypes)-1].id:
            return TEMPLATE
    if ID >= GUI.guiSensorGroups[0].id and\
        ID <= GUI.guiSensorGroups[len(GUI.guiSensorGroups)-1].id:
            return GROUPE

def offsetId(type):
    if type == LIMB:
        return StickMan.virtuMan.parts[0].id
    if type == SENSOR:
        return Sensors.virtuSens[0].id
    if type == ZOI:
        return Sensors.zoiSens[0].id
    if type == PANNEL:
        return GUI.guiPannel[0].id -1
    if type == TEMPLATE:
        return GUI.guiSensorTypes[0].id -1
    if type == GROUPE:
        return GUI.guiSensorGroups[0].id -1