import math

import Muscles
import Sensors
import StickMan

NONE = 0
LIMB = 1
MUSCLE = 2
SENSOR = 3
ZOI = 4

overGuiId = 0

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