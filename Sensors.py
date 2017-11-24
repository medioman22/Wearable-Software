class templates(object):
    """
        templates
        .x      attachment distance
        .t      attachment angle
    """

    def __init__(self, type, color, shape, scale): # add orientation sometime...
        """ constructor """
        self.type = type
        self.color = color
        self.shape = shape
        self.scale = scale
        

    def values(self):
        """ print characteristics values """
        print(self.type, self.color, self.shape, self.scale)


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
        self.zoi = False
        self.x = coord[0]
        self.t = coord[1]
        self.s = coord[2]
        self.h = 0.
        self.color = color
        

    def values(self):
        """ print characteristics values """
        print(self.attach, self.x, self.t)


from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import numpy as np

import Cursor
import Definitions
import Events
import Graphics
import GUI
import ID
import Shaders


sensorGraphics = []

virtuSens = []
zoiSens = []
overSensId = 0
selectedSens = []


def preprocessSensor(sensor, x, y, z):
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
        """ model matrix update """
        Definitions.modelMatrix.rotate(t.o, t.x, t.y, t.z)

        Definitions.modelMatrix.push()
        Definitions.modelMatrix.scale(sensor.h,1,1)
        Definitions.modelMatrix.translate(0.5, 0, 0)
        
        """ store modelMatrix in package """
        Definitions.packagePreprocess[Graphics.vboDashed] = Definitions.packagePreprocess[Graphics.vboDashed] + [[Definitions.modelMatrix.peek(), "Link", sensor.id, sensor],]
        
        Definitions.modelMatrix.pop()
        
    """ model matrix update """
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
    
    
    """ store modelMatrix in package """
    for sensorData in sensorGraphics:
        if sensor.type == sensorData.type:
            Definitions.packagePreprocess[sensorData.shape] = Definitions.packagePreprocess[sensorData.shape] + [[Definitions.modelMatrix.peek(), "Sensor", sensor.id, sensor],]
            break

    Definitions.modelMatrix.pop()
    Definitions.modelMatrix.pop()

def drawSensor(style):
    vboId = -1
    for indices in Definitions.packageIndices[2]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]
        sensor = pack[Definitions.entity]
        

        """ choose color """
        if style != Graphics.idBuffer:
            for sensorData in sensorGraphics:
                if sensor.type == sensorData.type:
                    if sensor.zoi == True:
                        color = np.array([0.5,0.5,0.5,1], dtype = np.float32)
                        vboDraw = Graphics.vboSurfaces
                    else:
                        color = np.array([sensorData.color[0]/255., sensorData.color[1]/255., sensorData.color[2]/255., sensorData.color[3]/255.], dtype = np.float32)
                    break
            if pack[Definitions.packID] == selectedSens:
                if sensor.zoi == False:
                    color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
                pack[Definitions.entity].x += Events.incSens[0]
                if pack[Definitions.entity].x < -0.5:
                    pack[Definitions.entity].x = -0.5
                elif pack[Definitions.entity].x > 0.5:
                    pack[Definitions.entity].x = 0.5

                pack[Definitions.entity].t += Events.incSens[1]
                pack[Definitions.entity].s += Events.incSens[2]
                if Events.resetSens == True:
                    pack[Definitions.entity].x = 0
                    pack[Definitions.entity].t = 90
                    pack[Definitions.entity].s = 90
                vboDraw = Graphics.vboSurfaces
            elif pack[Definitions.packID] == overSensId:
                if sensor.zoi == True:
                    color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
                vboDraw = Graphics.vboSurfaces
            else:
                vboDraw = Graphics.vboEdges
        else:
            vboDraw = Graphics.vboSurfaces
            r, g, b = ID.id2color(pack[Definitions.packID])
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)

        """ choose vbo """
        vboId = indices[0]
        if sensor.zoi == True:
            vboId = Graphics.vboCircle
            vboDraw = Graphics.vboSurfaces

        """ bind surfaces vbo """
        Graphics.indexPositions[vboId][vboDraw].bind()
        Graphics.vertexPositions[vboId].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][vboDraw], Graphics.nbIndex[vboId][vboDraw], GL_UNSIGNED_INT, None)


def drawDashed(style):
    vboId = -1
    for indices in Definitions.packageIndices[3]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]
        
        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            if style != Graphics.idBuffer:
                Graphics.indexPositions[vboId][Graphics.vboEdges].bind()
            else:
                Graphics.indexPositions[vboId][Graphics.vboSurfaces].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
            
        """ choose color """
        sensor = pack[Definitions.entity]
        if style != Graphics.idBuffer:
            for sensorData in sensorGraphics:
                if sensor.type == sensorData.type:
                    if sensor.zoi == True:
                        color = np.array([0.5,0.5,0.5,1], dtype = np.float32)
                    else:
                        color = np.array([sensorData.color[0]/255., sensorData.color[1]/255., sensorData.color[2]/255., sensorData.color[3]/255.], dtype = np.float32)
                    break
            if pack[Definitions.packID] == selectedSens:
                color = np.array([0.5*color[0], 0.5*color[1], 0.5*color[2], color[3]], dtype = np.float32)
        else:
            r, g, b = ID.id2color(pack[Definitions.packID])
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])
        
        """ draw vbo """
        if style != Graphics.idBuffer:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)
        else:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)


def displayTemplate():
    glUseProgram(Shaders.shader)
    """ choose vbo """
    for sensorData in sensorGraphics:
        if GUI.selectedTemplate == sensorData.type:
            vboId = sensorData.shape
    vboDraw = Graphics.vboEdges
    """ bind surfaces vbo """
    Graphics.indexPositions[vboId][vboDraw].bind()
    Graphics.vertexPositions[vboId].bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
    """ send color to shader """
    for sensorData in sensorGraphics:
        if GUI.selectedTemplate == sensorData.type:
            r,g,b,a = sensorData.color
    color = np.array([r/255.,g/255.,b/255.,a/255.], dtype = np.float32)
    glUniform4fv(Shaders.setColor_loc, 1, color)
    """ load matrix in shader """
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.set(Definitions.I)
    u = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, 0, 90))), Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, time.clock()*100, 0, 0)))))
    Definitions.modelMatrix.rotate(u.o, u.x, u.y, u.z)

    glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())
    Definitions.modelMatrix.pop()
            
    Definitions.viewMatrix.push()
    Definitions.viewMatrix.translate(0,0,-1.5)
    glUniformMatrix4fv(Shaders.view_loc, 1, GL_FALSE, Definitions.viewMatrix.peek())
    Definitions.viewMatrix.pop()
    """ draw vbo """
    glDrawElements(Graphics.styleIndex[vboId][vboDraw], Graphics.nbIndex[vboId][vboDraw], GL_UNSIGNED_INT, None)
    glUseProgram(0)