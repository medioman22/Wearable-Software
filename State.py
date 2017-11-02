import os

import Graphics
import StickMan
import Sensors

pathModels = "States/Models/"
pathSensors = "States/Sensors/"
pathTemplates = "States/Templates/"
pathZoi = "States/Zoi/"
extension = ".txt"
currentModelFile = 0
modelFileName = []
currentSensorFile = 0
sensorFileName = []

def createList():
    global modelFileName
    global sensorFileName

    modelFileName = os.listdir(pathModels)

    sensorFileName = os.listdir(pathSensors)
    
    zoiFileName = os.listdir(pathZoi)
    
def updateTemplateList():
    templateFileName = os.listdir(pathTemplates)
    Sensors.sensorGraphics = []
    for template in templateFileName:
        file = open(pathTemplates + template, 'r')
        line = file.readline()
        if line == "":
            continue
        r, g, b, a, shape = line.split(' ')
        Sensors.sensorGraphics = Sensors.sensorGraphics + [[template[:-len(extension)], (int(r),int(g),int(b),int(a)), int(shape)]]
        file.close()

"""
    Human model files
"""
def saveModel(entity):
    print("save model : {}".format(modelFileName[currentModelFile]))

    file = open(pathModels + modelFileName[currentModelFile], 'w')

    for part in entity.parts:
        file.write(part[StickMan.Data_id])
        file.write("\n")
        wat = " ".join(str(e) for e in part[StickMan.Data_angle])
        file.write(wat)
        file.write("\n")
    file.close()

    
def loadModel(entity):
    print("load model : {}".format(modelFileName[currentModelFile]))

    file = open(pathModels + modelFileName[currentModelFile], 'r')

    while True:
        ID = file.readline() # read part name
        if ID == "":
            break
        ID = ID[:-1] # remove end of line character
        line = file.readline() # read part orientations
        values = map(float, line.split())
        for part in entity.parts:
            #print(part[StickMan.Data_id])
            if part[StickMan.Data_id] == ID:
                part[StickMan.Data_angle] = values
                break
    file.close()

    

"""
    Sensors files
"""
def saveSensors():
    print("save sensor group : {}".format(sensorFileName[currentSensorFile]))

    file = open(pathSensors + sensorFileName[currentSensorFile], 'w')

    for sensor in Sensors.virtuSens:
        file.write(sensor.attach)
        file.write(" ")
        file.write(sensor.type)
        file.write(" ")
        file.write(str(sensor.x))
        file.write(" ")
        file.write(str(sensor.t))
        file.write(" ")
        file.write(str(sensor.s))
        file.write("\n")
    file.close()

def loadSensors():
    print("load sensor group : {}".format(sensorFileName[currentSensorFile]))

    file = open(pathSensors + sensorFileName[currentSensorFile], 'r')
    
    Sensors.virtuSens = []
    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        parent, type, x, t, s = line.split(' ')
        Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
    file.close()


"""
    Zones of interest files
"""
#def saveZoi(sensor):
#    print("save sensor group : {}".format(sensorFileName[currentSensorFile]))
#
#    file = open(pathZoi + sensor.type + extension, 'w')
#    
#    file.write(str(sensor.color[0]))
#    file.write(" ")
#    file.write(str(sensor.color[1]))
#    file.write(" ")
#    file.write(str(sensor.color[2]))
#    file.write(" 255 ")
#    file.write(sensor.type) #string here, int when read. fix it.
#    file.close()

def loadZOI(zoiFileName):
    Sensors.zoiSens = []

    if zoiFileName[0] == "":
        return

    print("load zoi : {}".format(zoiFileName[0]))

    file = open(pathZoi + zoiFileName[0] + '.txt', 'r')
    
    color = (zoiFileName[1][0]/255.,zoiFileName[1][1]/255.,zoiFileName[1][2]/255.,zoiFileName[1][3]/255.)
    type = zoiFileName[0]
    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        parent, x, t, s = line.split(' ')
        Sensors.zoiSens = Sensors.zoiSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)), color)]
    file.close()