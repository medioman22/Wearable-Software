import os
import shutil
#import csv

import Events
import Graphics
import GUI
import ID
import Limbs
import Muscles
import Sensors
import Saturations
import StickMan

extension = ".csv"

pathUserSettings = "States/UserSettings/"

pathAvatars = "States/Avatars/"
avatarFileName = []

pathPostures = "Postures/"
postureFileName = []

pathTemplates = "Templates/"
templateFileName = []

pathZoi = "Zoi/"
zoiFileName = []

pathGroups = "Groups/"
groupFileName = []

def importUserSettings():
    file = open(pathUserSettings + "Resolution" + extension, 'r')
    line = file.readline()
    x, y = line.split(';')
    GUI.display[0] = int(x)
    GUI.display[1] = int(y)


"""
    Avatar files
"""
def updateAvatar():
    global avatarFileName
    
    avatarFileName = os.listdir(pathAvatars)

def loadAvatar(entity, fileName):
    entity.tag = fileName
    loadLimbs(entity)
    loadMuscles(entity)
    updatePosture(entity)
    loadPosture(entity, postureFileName[0])
    updateGroup(entity)
    updateTemplate(entity)
    GUI.selectedTemplate = ""
    updateZoi(entity)
    Saturations.preprocessSaturations(entity)
    
def renameAvatar(entity, oldName, newName):
    try:
        os.rename(pathAvatars + oldName, pathAvatars + newName)
        entity.tag = newName
    except:
        pass



"""
    Limbs files
"""
def loadLimbs(entity):

    file = open(pathAvatars + entity.tag + '/' + 'Limbs' + extension, 'r')

    entity.limbs = []
    
    while True:
        line = file.readline()
        if line == "":
            break

        l, t, o1, o2, o3, d1, d2, d3, s1, s2, s3, s4, s5, s6, r1, r2, r3 = line.split(';')
        newLimb = Limbs.limb()
        newLimb.layer = int(l)
        newLimb.tag = t
        if newLimb.tag == "Head":
            newLimb.vbo = Graphics.vboSphere
        else:
            newLimb.vbo = Graphics.vboCylindre
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

    file = open(pathAvatars + entity.tag + '/' + 'Muscles' + extension, 'r')

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

def updatePosture(entity):
    global postureFileName

    """ Update list of posture files """
    postureFileName = os.listdir(pathAvatars + entity.tag + '/' + pathPostures)
    for i in range(0,len(postureFileName)):
        postureFileName[i] = postureFileName[i][:-len(extension)]
        
def loadPosture(entity, fileName):
    if fileName == "":
        return

    file = open(pathAvatars + entity.tag + '/' + pathPostures + fileName + extension, 'r')
    line = file.readline() # read entity position
    px, py, pz, trash = line.split(";")
    line = file.readline() # read entity position
    orientation = map(float, line.split(";"))
    entity.position = [float(px), float(py), float(pz)]
    entity.orientation = orientation
    while True:
        line = file.readline() # read part name
        if line == "":
            break
        ID, a,b,c = map(str, line.split(";"))
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

def savePosture(entity, fileName):
    file = open(pathAvatars + entity.tag + '/' + pathPostures + fileName + extension, 'w')

    position = ";".join(str(e) for e in entity.position) + ";"
    file.write(position)
    file.write("\n")
    orientation = ";".join(str(e) for e in entity.orientation)
    file.write(orientation)
    file.write("\n")
    for part in entity.limbs:
        file.write(part.tag + ";;;")
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

def removePosture(entity, fileName):
    os.remove(pathAvatars + entity.tag + '/' + pathPostures + fileName + extension)

def renamePosture(entity, oldName, newName):
    try:
        os.rename(pathAvatars + entity.tag + '/' + pathPostures + oldName + extension, pathAvatars + entity.tag + '/' + pathPostures + newName + extension)
    except:
        pass


"""
    Template files
"""

def updateTemplate(entity):
    global templateFileName

    templateFileName = os.listdir(pathAvatars + entity.tag + '/' + pathTemplates)
    Sensors.sensorGraphics = []
    for template in templateFileName:
        file = open(pathAvatars + entity.tag + '/' + pathTemplates + template + '/' + 'Template' + extension, 'r')
        line = file.readline()
        if line == "":
            continue
        r, g, b, a, shape, scale = line.split(';')
        Sensors.sensorGraphics = Sensors.sensorGraphics + [Sensors.templates(template, [int(r),int(g),int(b),int(a)], int(shape), float(scale))]
        file.close()

def saveTemplate(entity, fileName):
    if fileName == "":
        return

    if not os.path.exists(pathAvatars + entity.tag + '/' + pathTemplates + fileName):
        os.makedirs(pathAvatars + entity.tag + '/' + pathTemplates + fileName)
        os.makedirs(pathAvatars + entity.tag + '/' + pathTemplates + fileName + '/' + 'Zoi')

    file = open(pathAvatars + entity.tag + '/' + pathTemplates + fileName + '/' + 'Template' + extension, 'w')

    file.write(str(Sensors.customTemplate.color[0]))
    file.write(";")
    file.write(str(Sensors.customTemplate.color[1]))
    file.write(";")
    file.write(str(Sensors.customTemplate.color[2]))
    file.write(";")
    file.write(str(Sensors.customTemplate.color[3]))
    file.write(";")
    file.write(str(Sensors.customTemplate.shape))
    file.write(";")
    file.write(str(Sensors.customTemplate.scale))

    file.close()

def removeTemplate(entity, fileName):
    shutil.rmtree(pathAvatars + entity.tag + '/' + pathTemplates + fileName)

def renameTemplate(entity, oldName, newName):
    try:
        os.rename(pathAvatars + entity.tag + '/' + pathTemplates + oldName, pathAvatars + entity.tag + '/' + pathTemplates + newName)
        # change sensor name in group files to match with new template name
        for fileName in groupFileName:
            # read file
            file = open(pathAvatars + entity.tag + '/' + pathGroups + fileName + extension, 'r')
            fileData = []
            while True:
                line = file.readline() # read sensor data
                if line == "":
                    break
                tag, parent, type, x, t, s = line.split(';')
                if type == oldName:
                    type = newName
                fileData = fileData + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
                fileData[len(fileData)-1].tag = tag
            file.close()
                    
            # rewrite file
            file = open(pathAvatars + entity.tag + '/' + pathGroups + fileName + extension, 'w')
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
            if sensorData.type == oldName:
                sensorData.type = newName
                break
    except:
        pass


"""
    Zones of interest files
"""

def updateZoi(entity):
    global zoiFileName
    zoiFileName = []

    if GUI.selectedTemplate == "":
        return

    zoiFileName = os.listdir(pathAvatars + entity.tag + '/' + pathTemplates + GUI.selectedTemplate + '/' + pathZoi)
    for i in range(0,len(zoiFileName)):
        zoiFileName[i] = zoiFileName[i][:-len(extension)]


def loadZOI(entity, fileName):
    Sensors.zoiSens = []

    if fileName == "":
        Limbs.setLimbsShow(StickMan.virtuMan, Events.SHOW)
        Muscles.setMusclesShow(StickMan.virtuMan, Events.SHOW)
        return
    
    Limbs.setLimbsShow(StickMan.virtuMan, Events.FADE)
    Muscles.setMusclesShow(StickMan.virtuMan, Events.HIDE)

    file = open(pathAvatars + entity.tag + '/' + pathTemplates + GUI.selectedTemplate + '/' + pathZoi + fileName + extension, 'r')
    
    color = (0.5,0.5,0.5,1)
    type = GUI.selectedTemplate
    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        name, parent, x, t, s = line.split(';')
        Sensors.zoiSens = Sensors.zoiSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)), color)]
        Sensors.zoiSens[len(Sensors.zoiSens)-1].tag = name
        Limbs.showLimb(StickMan.virtuMan, parent)
        Muscles.showMuscle(StickMan.virtuMan, parent)
    file.close()

def renameZoi(entity, oldName, newName):
    try:
        os.rename(pathAvatars + entity.tag + '/' + pathTemplates + GUI.selectedTemplate + '/' + pathZoi + oldName + extension, pathAvatars + entity.tag + '/' + pathTemplates + GUI.selectedTemplate + '/' + pathZoi + newName + extension)
    except:
        pass


"""
    Group files
"""

def updateGroup(entity):
    global groupFileName

    groupFileName = os.listdir(pathAvatars + entity.tag + '/' + pathGroups)
    for i in range(0,len(groupFileName)):
        groupFileName[i] = groupFileName[i][:-len(extension)]

def saveGroups(entity, fileName):
    file = open(pathAvatars + entity.tag + '/' + pathGroups + fileName + extension, 'w')

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

def loadGroup(entity, fileName):
    Sensors.virtuSens = []

    if fileName == "":
        return

    file = open(pathAvatars + entity.tag + '/' + pathGroups + fileName + extension, 'r')

    while True:
        line = file.readline() # read sensor data
        if line == "":
            break
        name, parent, type, x, t, s = line.split(';')
        Sensors.virtuSens = Sensors.virtuSens + [Sensors.sensors(parent, type, (float(x),float(t),float(s)))]
        Sensors.virtuSens[len(Sensors.virtuSens)-1].tag = name
    file.close()
    
def removeGroup(entity, fileName):
    os.remove(pathAvatars + entity.tag + '/' + pathGroups + fileName + extension)

def renameGroup(entity, oldName, newName):
    try:
        os.rename(pathAvatars + entity.tag + '/' + pathGroups + oldName + extension, pathAvatars + entity.tag + '/' + pathGroups + newName + extension)
    except:
        pass
