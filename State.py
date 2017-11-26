import os
#import csv

import Events
import Graphics
import GUI
import ID
import Limbs
import Muscles
import Sensors

pathUserSettings = "States/UserSettings/"
extension = ".csv"

pathAvatars = "States/Avatars/"
currentAvatarFile = 0
avatarFileName = []

pathPostures = "Postures/"
postureFileName = []

pathGroups = "States/Groups/"
saveGroupFile = ''

pathTemplates = "States/Templates/"
currentSensorFile = 0
sensorFileName = []

def importUserSettings():
    file = open(pathUserSettings + "Resolution" + extension, 'r')
    line = file.readline()
    x, y = line.split(';')
    GUI.display[0] = int(x)
    GUI.display[1] = int(y)

def renameFile(key):
    try:
        newName = Events.rename
        # define new name
        if key == 'backspace' and len(newName) >= 1:
            newName = newName[:-1]
        elif key == 'space':
            key = ' '
        if Events.caps == True:
            key = key.upper()
        if len(key) == 1:
            newName = newName + key
            

        if newName != Events.rename:
            # rename files
            if Events.renameType == ID.TEMPLATE:
                os.rename(pathTemplates + Events.rename, pathTemplates + newName)
                # change sensor name in group files to match with new template name
                for fileName in sensorFileName:
                    # read file
                    file = open(pathGroups + fileName[0] + extension, 'r')
                    fileData = []
                    while True:
                        line = file.readline() # read sensor data
                        if line == "":
                            break
                        tag, parent, type, x, t, s = line.split(';')
                        if type == Events.rename:
                            type = newName
                        fileData = fileData + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
                        fileData[len(fileData)-1].tag = tag
                    file.close()
                    
                    # rewrite file
                    file = open(pathGroups + fileName[0] + extension, 'w')
                    for sensor in fileData:
                        file.write(sensor.tag)
                        file.write(";")
                        file.write(sensor.attach)
                        file.write(";")
                        file.write(sensor.type)
                        file.write(";")
                        file.write(str(sensor.x))
                        file.write(";")
                        file.write(str(sensor.t))
                        file.write(";")
                        file.write(str(sensor.s))
                        file.write("\n")
                    file.close()
                for sensorData in Sensors.sensorGraphics:
                    if Events.rename == sensorData.type:
                        sensorData.type = newName
                        break
                
                loadGroups()
            elif Events.renameType == ID.GROUPE:
                os.rename(pathGroups + Events.rename + extension, pathGroups + newName + extension)
            elif Events.renameType == ID.POSTURE:
                os.rename(pathAvatars + avatarFileName[currentAvatarFile] + '/' + pathPostures + Events.rename + extension, pathAvatars + avatarFileName[currentAvatarFile] + '/' + pathPostures + newName + extension)

            Events.rename = newName
    except:
        pass


"""
    Generate lists of files for avatar / postures / groups / templates
"""
def updateFilesLists():
    global avatarFileName
    global postureFileName
    global sensorFileName

    
    """ Update list of avatar files """
    avatarFileName = os.listdir(pathAvatars)

    """ Update list of posture files """
    postureFileName = os.listdir(pathAvatars + avatarFileName[currentAvatarFile] + '/' + pathPostures)
    for i in range(0,len(postureFileName)):
        postureFileName[i] = postureFileName[i][:-len(extension)]

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
        file = open(pathTemplates + template + '/' + 'Template' + extension, 'r')
        line = file.readline()
        if line == "":
            continue
        r, g, b, a, shape, scale = line.split(';')
        Sensors.sensorGraphics = Sensors.sensorGraphics + [Sensors.templates(template, [int(r),int(g),int(b),int(a)], int(shape), float(scale))]
        file.close()





"""
    Limbs files
"""
def loadLimbs(entity):

    file = open(pathAvatars + avatarFileName[currentAvatarFile] + '/' + 'Limbs' + extension, 'r')

    entity.limbs = []
    
    while True:
        line = file.readline()
        if line == "":
            break

        l, t, o1, o2, o3, d1, d2, d3, s1, s2, s3, s4, s5, s6, r1, r2, r3 = line.split(';')
        newLimb = Limbs.limb()
        newLimb.layer = int(l)
        newLimb.tag = t
        newLimb.offset = [float(o1), float(o2), float(o3)]
        newLimb.dimensions = [float(d1), float(d2), float(d3)]
        newLimb.saturations = [float(s1), float(s2), float(s3), float(s4), float(s5), float(s6)]
        newLimb.angleRepos = [float(r1), float(r2), float(r3)]
        entity.limbs = entity.limbs + [newLimb]

    file.close()


"""
    Muscles files
"""
def loadMuscles(entity):

    file = open(pathAvatars + avatarFileName[currentAvatarFile] + '/' + 'Muscles' + extension, 'r')

    entity.muscles = []
    
    while True:
        line = file.readline()
        if line == "":
            break

        tag, A, Al1, Al2, Al3, B, Bl1, Bl2, Bl3 = line.split(';')
        newMuscle = Muscles.muscle()
        newMuscle.tag = tag
        newMuscle.A = A
        newMuscle.Alocal = [float(Al1), float(Al2), float(Al3), 1]
        newMuscle.B = B
        newMuscle.Blocal = [float(Bl1), float(Bl2), float(Bl3), 1]
        entity.muscles = entity.muscles + [newMuscle]

    file.close()

"""
    Postures files
"""
def savePosture(entity):
    if GUI.selectedPosture != 0:
        file = open(pathAvatars + avatarFileName[currentAvatarFile] + '/' + pathPostures + postureFileName[GUI.selectedPosture-1] + extension, 'w')

        for part in entity.limbs:
            file.write(part.tag)
            file.write("\n")
            angle = ";".join(str(e) for e in part.angle)
            file.write(angle)
            file.write("\n")
            swing = ";".join(str(e) for e in part.swing)
            file.write(swing)
            file.write("\n")
            twist = ";".join(str(e) for e in part.twist)
            file.write(twist)
            file.write("\n")
        file.close()

    
def loadPosture(entity):
    if GUI.selectedPosture != 0:
        file = open(pathAvatars + avatarFileName[currentAvatarFile] + '/' + pathPostures + postureFileName[GUI.selectedPosture-1] + extension, 'r')
        while True:
            ID = file.readline() # read part name
            if ID == "":
                break
            ID = ID[:-1] # remove end of line character
            line = file.readline() # read part orientations
            angle = map(float, line.split(";"))
            line = file.readline() # read part orientations
            swing = map(float, line.split(";"))
            line = file.readline() # read part orientations
            twist = map(float, line.split(";"))
            for part in entity.limbs:
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
    file = open(pathTemplates + template.type + '/' + 'Template' + extension, 'w')

    file.write(str(template.color[0]))
    file.write(";")
    file.write(str(template.color[1]))
    file.write(";")
    file.write(str(template.color[2]))
    file.write(";")
    file.write(str(template.color[3]))
    file.write(";")
    file.write(str(template.shape))
    file.write(";")
    file.write(str(template.scale))

    file.close()

"""
    Sensors files
"""
def saveGroups():
    file = open(pathGroups + saveGroupFile + extension, 'w')

    for sensor in Sensors.virtuSens:
        file.write(sensor.tag)
        file.write(";")
        file.write(sensor.attach)
        file.write(";")
        file.write(sensor.type)
        file.write(";")
        file.write(str(sensor.x))
        file.write(";")
        file.write(str(sensor.t))
        file.write(";")
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
                name, parent, type, x, t, s = line.split(';')
                Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
                Sensors.virtuSens[len(Sensors.virtuSens)-1].tag = name
            file.close()


"""
    Zones of interest files
"""

def loadZOI(zoiFileName):
    Sensors.zoiSens = []

    if zoiFileName == "":
        return

    file = open(pathTemplates + zoiFileName + '/' + 'ZOI' + extension, 'r')
    
    color = (0.5,0.5,0.5,1)
    type = zoiFileName
    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        name, parent, x, t, s = line.split(';')
        Sensors.zoiSens = Sensors.zoiSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)), color)]
        Sensors.zoiSens[len(Sensors.zoiSens)-1].tag = name
    file.close()


