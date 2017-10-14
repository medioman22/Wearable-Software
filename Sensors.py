class sensors(object):
    """
        characteristics
        .x      attachment distance
        .t      attachment angle
    """
    __name__ = "sensors"
    nb__init__ = 0 # keeps track of how many creations there are


    def __init__(self, attach = "Origin", coord = (0, 0), color = (1,0,0)): # add orientation sometime...
        """ constructor """
        sensors.nb__init__ += 1
        self.attach = attach
        self.x = coord[0]
        self.t = coord[1]
        self.h = 0.
        self.color = color

    @classmethod
    def feedback(cls,reset = False):
        """ print feedback on class calls """
        print("nb__init__ : {}".format(sensors.nb__init__))
        if reset == True:
            sensors.nb__init__ = 0
            print("reset for {} is done".format(cls.__name__))
        print("\n")
        

    def values(self):
        """ print characteristics values """
        print(self.attach, self.x, self.t)



virtuSens = ["",]

from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import numpy as np

import Definitions
import Graphics
import Shaders

countID = 0
def preprocessSensor(sensor):
    global countID
    countID += 1
    Definitions.transform.push()

    """ sensor orientation """
    u = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, 90, 0)))
    v = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, 0, 0, sensor.t)))
    w = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, time.clock()*100, 0, 0)))
    t = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(u, Definitions.vector4D.QuatProd(v,w)))

    """ transformation matrix update """
    Definitions.transform.push()
    Definitions.transform.translate(sensor.x, 0, 0)

    if math.sqrt(t.x*t.x + t.y*t.y + t.z*t.z) >= 0.0001:
        """ transformation matrix update """
        Definitions.transform.rotate(t.o, t.x, t.y, t.z)

        Definitions.transform.push()
        Definitions.transform.scale(sensor.h,sensor.h,sensor.h)
        
        """ store transformation in package """
        Definitions.packagePreprocess[Graphics.vboDashed] = Definitions.packagePreprocess[Graphics.vboDashed] + [[Definitions.transform.peek(), "Link", countID, sensor],]
        #Definitions.packageDashed = Definitions.packageDashed + [[Definitions.transform.peek(), sensor],]
        
        Definitions.transform.pop()
        
    """ transformation matrix update """
    Definitions.transform.translate(sensor.h, 0, 0)
    Definitions.transform.scale(0.03,0.03,0.03)
    Definitions.transform.translate(0.5, 0, 0)
    
    
    """ store transformation in package """
    if countID < 4:
        Definitions.packagePreprocess[Graphics.vboCube] = Definitions.packagePreprocess[Graphics.vboCube] + [[Definitions.transform.peek(), "Sensor", countID, sensor],]
    elif countID < 6:
        Definitions.packagePreprocess[Graphics.vboPyramide] = Definitions.packagePreprocess[Graphics.vboPyramide] + [[Definitions.transform.peek(), "Sensor", countID, sensor],]
    else:
        Definitions.packagePreprocess[Graphics.vboHexagon] = Definitions.packagePreprocess[Graphics.vboHexagon] + [[Definitions.transform.peek(), "Sensor", countID, sensor],]
    #Definitions.packageSensors = Definitions.packageSensors + [[Definitions.transform.peek(), sensor],]

    Definitions.transform.pop()
    Definitions.transform.pop()

def drawSensor(style):
    vboId = -1
    for indices in Definitions.packageIndices[2]:
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
            color = np.array([sensor.color[0], sensor.color[1], sensor.color[2], 1.], dtype = np.float32)
        else:
            i = pack[Definitions.packID]/float(countID)
            color = np.array([0, i, 0, 1.], dtype = np.float32)
        
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])

        """ draw vbo """
        if style != Graphics.idBuffer:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)
        else:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)


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
            color = np.array([sensor.color[0], sensor.color[1], sensor.color[2], 1.], dtype = np.float32)
        else:
            i = pack[Definitions.packID]/float(countID)
            color = np.array([0, i, 0, 1.], dtype = np.float32)
            
        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ load matrix in shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])
        
        """ draw vbo """
        if style != Graphics.idBuffer:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)
        else:
            glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)