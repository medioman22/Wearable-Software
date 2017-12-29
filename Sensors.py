#
#   File : Sensors.py
#   
#   Code written by : Johann Heches
#
#   Description : Preprocess of sensors model matrix ; rendering of sensor meshes.
#   

#TODO : send all templates vbo at once
class templates(object):
    """
        templates
        .x      attachment distance
        .t      attachment angle
    """

    def __init__(self, type = "", color = [0,0,0,255], shape = 0, scale = 0.03): # add orientation sometime...
        """ constructor """
        self.type = type
        self.color = color
        self.shape = shape
        self.scale = scale
        self.mesh = None
        


class sensors(object):
    """
        sensors
        .x      attachment distance
        .t      attachment angle
    """

    def __init__(self, attach = "Origin", type = "Custom", coord = (0, 0, 0), color = (1,0,0)): # add orientation sometime...
        """ constructor """
        self.id = 0
        self.attach = attach
        self.type = type
        self.tag = 'Tag'
        self.x = coord[0]
        self.t = coord[1]
        self.s = coord[2]
        self.h = 0.
        self.color = color
        self.modelMatrix = []
        self.linkModelMatrix = []
        self.selected = False
        self.show = True
        


from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import numpy as np

import Definitions
import Events
import Graphics
import ID
import Shaders
import UI

customTemplate = templates("", [0, 0, 0, 255], 0, 0.03)

sensorGraphics = []
newSens = []
virtuSens = []
zoiSens = []
overSensId = 0
selectedSens = 0
selectedTemplate = ""

def preprocessSensor(sensor, x, y, z):
    
    """ update sensor coordinates """
    if sensor.id == selectedSens:
        sensor.x += Events.incSens[0]
        if sensor.x < -0.5:
            sensor.x = -0.5
        elif sensor.x > 0.5:
            sensor.x = 0.5
        sensor.t += Events.incSens[1]
        sensor.s += Events.incSens[2]
        if Events.resetSens == True:
            sensor.x = 0
            sensor.t = 90
            sensor.s = 90
        UI.uiSensor.updateTable()

    Definitions.modelMatrix.push()

    """ sensor orientation """
    u = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, 90, 0)))
    v = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, 0, sensor.t)))
    s = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, sensor.s-90, 0)))
    w = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, time.clock()*100, 0, 0)))
    t = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(u, Definitions.vector4D.QuatProd(v, Definitions.vector4D.QuatProd(s,w))))

    """ model matrix update """
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.translate(sensor.x, 0, 0)

    if math.sqrt(t.x*t.x + t.y*t.y + t.z*t.z) >= 0.0001:
        Definitions.modelMatrix.rotate(t.o, t.x, t.y, t.z)

        Definitions.modelMatrix.push()
        Definitions.modelMatrix.scale(sensor.h,1,1)
        Definitions.modelMatrix.translate(0.5, 0, 0)
        
        """ store linkModelMatrix in sensor """
        sensor.linkModelMatrix = Definitions.modelMatrix.peek()

        Definitions.modelMatrix.pop()
        
    Definitions.modelMatrix.translate(sensor.h, 0, 0)
    Definitions.modelMatrix.rotate(-t.o, t.x, t.y, t.z)
    Definitions.modelMatrix.scale(1/x,1/y,1/z)
    Definitions.modelMatrix.rotate(t.o, t.x, t.y, t.z)
    
    for sensorData in sensorGraphics:
        if sensor.type == sensorData.type:
            scale = sensorData.scale
            break
    Definitions.modelMatrix.scale(scale, scale, scale)

    Definitions.modelMatrix.translate(0.5, 0, 0)
    
    """ store modelMatrix in sensor """
    sensor.modelMatrix = Definitions.modelMatrix.peek()

    Definitions.modelMatrix.pop()
    Definitions.modelMatrix.pop()


def drawSensor(style):
    if Events.showSensors == False:
        return
    
    for sensor in virtuSens:
        """ find sensor's template """
        template = None
        for sensorData in sensorGraphics:
            if sensor.type == sensorData.type:
                template = sensorData
                break
        if template == None:
            print("WARNING : No template match !")
            continue

        """ choose color """
        if style != Graphics.idBuffer:
            color = np.array([template.color[0]/255., template.color[1]/255., template.color[2]/255., template.color[3]/255.], dtype = np.float32)
            if sensor.id == selectedSens:
                color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
                vboDraw = Graphics.vboSurfaces
            elif sensor.id == overSensId:
                vboDraw = Graphics.vboSurfaces
            else:
                vboDraw = Graphics.vboEdges
        else:
            vboDraw = Graphics.vboSurfaces
            r, g, b = ID.id2color(sensor.id)
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, sensor.modelMatrix)

        """ bind vbo """
        template.mesh.vertexPositions.bind()
        if vboDraw == Graphics.vboSurfaces:
            template.mesh.surfIndexPositions.bind()
        else:
            template.mesh.edgeIndexPositions.bind()
        glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)

        """ draw vbo """
        if vboDraw == Graphics.vboSurfaces:
            glDrawElements(template.mesh.surfStyleIndex, template.mesh.surfNbIndex, GL_UNSIGNED_INT, None)
        else:
            glDrawElements(template.mesh.edgeStyleIndex, template.mesh.edgeNbIndex, GL_UNSIGNED_INT, None)

zoi = None
def drawZoi(style):
    if Events.showSensors == False:
        return
    
    """ bind vbo """
    zoi.mesh.vertexPositions.bind()
    zoi.mesh.surfIndexPositions.bind()
    glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
    for sensor in zoiSens:
        """ find sensor's template """
        template = None
        for sensorData in sensorGraphics:
            if sensor.type == sensorData.type:
                template = sensorData
                break
        if template == None:
            print("WARNING : No template match !")
            continue

        """ choose color """
        if style != Graphics.idBuffer:
            color = np.array([0.5,0.5,0.5,1], dtype = np.float32)
            if sensor.id == overSensId:
                color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
        else:
            r, g, b = ID.id2color(sensor.id)
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, sensor.modelMatrix)
        
        """ draw vbo """
        glDrawElements(zoi.mesh.surfStyleIndex, zoi.mesh.surfNbIndex, GL_UNSIGNED_INT, None)
        

link = None
def drawLink(style):
    if Events.showSensors == False or style == Graphics.idBuffer:
        return

    link.mesh.edgeIndexPositions.bind()
    link.mesh.vertexPositions.bind()
    glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
    for sensor in virtuSens + zoiSens:
        """ choose color """
        for sensorData in sensorGraphics:
            if sensor.type == sensorData.type:
                if ID.idCategory(sensor.id) == ID.ZOI:
                    color = np.array([0.5,0.5,0.5,1], dtype = np.float32)
                else:
                    color = np.array([sensorData.color[0]/255., sensorData.color[1]/255., sensorData.color[2]/255., sensorData.color[3]/255.], dtype = np.float32)
                break
        if sensor.id == selectedSens:
            color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
    
        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, sensor.linkModelMatrix)
        
        """ draw vbo """
        glDrawElements(link.mesh.surfStyleIndex, link.mesh.surfNbIndex, GL_UNSIGNED_INT, None)