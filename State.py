import os

import Events
import Graphics
import GUI
import StickMan
import Sensors

pathAvatars = "States/Avatars/"
pathPostures = "States/Postures/"
pathGroups = "States/Groups/"
pathTemplates = "States/Templates/"
pathUserSettings = "States/UserSettings/"
pathZoi = "States/Zoi/"
extension = ".txt"
currentPostureFile = 0
postureFileName = []
currentSensorFile = 0
saveGroupFile = ''
sensorFileName = []

def importUserSettings():
    file = open(pathUserSettings + "Resolution.txt", 'r')
    line = file.readline()
    x, y = line.split(' ')
    GUI.display[0] = int(x)
    GUI.display[1] = int(y)

def renameFile(key):
    try:
        newName = Events.rename

        # define new name
        if key == 'backspace' and len(newName) >= 5:
            newName = newName[:-5] + extension
        elif key == 'space':
            key = '_'
        if Events.caps == True:
            key = key.upper()
        if len(key) == 1:
            newName = newName[:-4] + key + extension


        if newName != Events.rename:
            # rename files
            if Events.renameType == GUI.guiTemplate:
                os.rename(pathTemplates + Events.rename, pathTemplates + newName)
                os.rename(pathZoi + Events.rename, pathZoi + newName)
                # change sensor name in group files to match with new template name
                for fileName in sensorFileName:
                    # read file
                    file = open(pathGroups + fileName[0] + extension, 'r')
                    fileData = []
                    while True:
                        line = file.readline() # read sensor data
                        if line == "":
                            break
                        parent, type, x, t, s = line.split(' ')
                        if type == Events.rename[:-4]:
                            type = newName[:-4]
                        fileData = fileData + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
                    file.close()
                    # rewrite file
                    file = open(pathGroups + fileName[0] + extension, 'w')
                    for sensor in fileData:
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
                for i in range(0, len(Sensors.sensorGraphics)):
                    if Sensors.sensorGraphics[i][0] == Events.rename[:-4]:
                        print(Sensors.sensorGraphics[i][0], Events.rename[:-4])
                        Sensors.sensorGraphics[i][0] = newName[:-4]
                        break
                loadGroups()
            elif Events.renameType == GUI.guiGroup:
                os.rename(pathGroups + Events.rename, pathGroups + newName)

            Events.rename = newName
    except:
        pass


"""
    Generate lists of files for postures / groups / templates
"""
def updateFilesLists():
    global postureFileName
    global sensorFileName


    """ Update list of postures files """
    postureFileName = os.listdir(pathPostures)
    

    """ Update list of groupe files """
    listFiles = os.listdir(pathGroups)
    tempList = []
    for file in listFiles:
        tempList = tempList + [[file[:-4], False]]
    for fileName in sensorFileName:
        for i in range(0,len(tempList)):
            if fileName[0] == tempList[i][0]:
                tempList[i][1] = fileName[1]
    sensorFileName = tempList
    

    """ Update list of template files """
    templateFileName = os.listdir(pathTemplates)
    Sensors.sensorGraphics = []
    for template in templateFileName:
        file = open(pathTemplates + template, 'r')
        line = file.readline()
        if line == "":
            continue
        r, g, b, a, shape, scale = line.split(' ')
        Sensors.sensorGraphics = Sensors.sensorGraphics + [[template[:-len(extension)], (int(r),int(g),int(b),int(a)), int(shape), float(scale)]]
        file.close()


"""
    Human postures files
"""
def savePosture(entity):
    file = open(pathPostures + postureFileName[currentPostureFile], 'w')

    for part in entity.parts:
        file.write(part.tag)
        file.write("\n")
        angle = " ".join(str(e) for e in part.angle)
        file.write(angle)
        file.write("\n")
        swing = " ".join(str(e) for e in part.swing)
        file.write(swing)
        file.write("\n")
        twist = " ".join(str(e) for e in part.twist)
        file.write(twist)
        file.write("\n")
    file.close()

    
def loadPosture(entity):
    file = open(pathPostures + postureFileName[currentPostureFile], 'r')

    while True:
        ID = file.readline() # read part name
        if ID == "":
            break
        ID = ID[:-1] # remove end of line character
        line = file.readline() # read part orientations
        angle = map(float, line.split())
        line = file.readline() # read part orientations
        swing = map(float, line.split())
        line = file.readline() # read part orientations
        twist = map(float, line.split())
        for part in entity.parts:
            if part.tag == ID:
                part.angle = angle
                part.swing = swing
                part.twist = twist
                break
    file.close()

"""
    Template files
"""
def saveTemplates(template):
    file = open(pathTemplates + template[0] + extension, 'w')

    file.write(str(template[1][0]))
    file.write(" ")
    file.write(str(template[1][1]))
    file.write(" ")
    file.write(str(template[1][2]))
    file.write(" ")
    file.write(str(template[1][3]))
    file.write(" ")
    file.write(str(template[2]))
    file.write(" ")
    file.write(str(template[3]))

    file.close()

"""
    Sensors files
"""
def saveGroups():
    file = open(pathGroups + saveGroupFile + extension, 'w')

    for sensor in Sensors.virtuSens:
        file.write(sensor.tag)
        file.write(" ")
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

def loadGroups():
    Sensors.virtuSens = []

    for file in sensorFileName:
        if file[1] == True:
            file = open(pathGroups + file[0] + extension, 'r')
    
            while True:
                line = file.readline() # read sensor data
                if line == "":
                    break
                name, parent, type, x, t, s = line.split(' ')
                Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
                Sensors.virtuSens[len(Sensors.virtuSens)-1].tag = name
            file.close()


"""
    Zones of interest files
"""

def loadZOI(zoiFileName):
    Sensors.zoiSens = []

    if zoiFileName[0] == "":
        return

    file = open(pathZoi + zoiFileName[0] + '.txt', 'r')
    
    color = (0.5,0.5,0.5,1)
    type = zoiFileName[0]
    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        name, parent, x, t, s = line.split(' ')
        Sensors.zoiSens = Sensors.zoiSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)), color)]
        Sensors.zoiSens[len(Sensors.zoiSens)-1].tag = name
        Sensors.zoiSens[len(Sensors.zoiSens)-1].zoi = True
    file.close()


"""
    Avatars files
"""
def saveAvatar():
    file = open(pathAvatars + 'Human' + extension, 'w')

    for limb in StickMan.virtuMan.parts:
        
        file.write(str(limb[StickMan.Data_layer]))
        file.write(" ")

        file.write(limb[StickMan.Data_id])
        file.write(" ")

        values = " ".join(str(e) for e in limb[StickMan.Data_offset])
        file.write(values)
        file.write(" ")

        values = " ".join(str(e) for e in limb[StickMan.Data_dimensions])
        file.write(values)
        file.write(" ")

        values = " ".join(str(e) for e in limb[StickMan.Data_saturation])
        file.write(values)
        file.write(" ")

        values = " ".join(str(e) for e in limb[StickMan.Data_angleRepos])
        file.write(values)

        file.write("\n")

    file.close()

def loadAvatar(entity):

    file = open(pathAvatars + 'Human' + extension, 'r')

    entity.parts = []
    
    while True:
        line = file.readline()
        if line == "":
            break

        l, t, o1, o2, o3, d1, d2, d3, s1, s2, s3, s4, s5, s6, r1, r2, r3 = line.split(' ')
        newLimb = StickMan.limbs()
        newLimb.layer = int(l)
        newLimb.tag = t
        newLimb.offset = [float(o1), float(o2), float(o3)]
        newLimb.dimensions = [float(d1), float(d2), float(d3)]
        newLimb.saturations = [float(s1), float(s2), float(s3), float(s4), float(s5), float(s6)]
        newLimb.angleRepos = [float(r1), float(r2), float(r3)]
        entity.parts = entity.parts + [newLimb]

    file.close()
