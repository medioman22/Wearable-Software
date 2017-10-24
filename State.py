import os

import StickMan
import Sensors

path = "States/"
pathSensors = "Sensors/"
currentFile = 0
fileName = []
currentSensorFile = 0
sensorFileName = []

def createList():
    global fileName
    global sensorFileName
    print(" - creating list of models - ")
    fileName = os.listdir(path)
    print(fileName)
    print(" - creating list of sensor groups - ")
    sensorFileName = os.listdir(pathSensors)
    print(sensorFileName)

def save(entity):
    print("save model : {}".format(fileName[currentFile]))

    file = open(path + fileName[currentFile], 'w')

    for part in entity.parts:
        file.write(part[StickMan.Data_id])
        file.write("\n")
        wat = " ".join(str(e) for e in part[StickMan.Data_angle])
        file.write(wat)
        file.write("\n")
    file.close()

    
def load(entity):
    print("load model : {}".format(fileName[currentFile]))

    file = open(path + fileName[currentFile], 'r')

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
        file.write(" ")
        file.write(str(sensor.color[0]))
        file.write(" ")
        file.write(str(sensor.color[1]))
        file.write(" ")
        file.write(str(sensor.color[2]))
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
        parent, type, x, t, s, r, g, b = line.split(' ')
        Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)), (float(r), float(g), float(b)))]
    file.close()