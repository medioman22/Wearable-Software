from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

import Definitions
import Graphics
import Sensors
import Shaders

def preprocessMuscle():
    for i in range(0,len(muscles)):

        P1 = muscles[i][A][Attach_world]
        P2 = muscles[i][B][Attach_world]
        if P1 == [] or P2 == []:
            continue

        v1 = Definitions.vector4D((0, 1, 0, 0))
        v2 = Definitions.vector4D((0, P1[0][0]-P2[0][0], P1[0][1]-P2[0][1], P1[0][2]-P2[0][2]))
        scale = math.sqrt(v2.x*v2.x + v2.y*v2.y + v2.z*v2.z)
        center = Definitions.vector4D((0, 0.5*(P1[0][0]+P2[0][0]), 0.5*(P1[0][1]+P2[0][1]), 0.5*(P1[0][2]+P2[0][2])))
        u = Definitions.vector4D.AngleAxisBetween2Vec(v1,v2)
    
        """ load matrix in shader """
        Definitions.modelMatrix.push()
        Definitions.modelMatrix.set(Definitions.I)
        Definitions.modelMatrix.translate(center.x, center.y, center.z)
        Definitions.modelMatrix.rotate(u.o, u.x, u.y, u.z)
        Definitions.modelMatrix.scale(scale,0.03,0.03)
        
        muscles[i][modelMatrix] = Definitions.modelMatrix.peek()

        
        for sensor in Sensors.virtuSens + Sensors.zoiSens:
            if sensor.attach == muscles[i][Tag]:
                sensor.h = 0.6
                if sensor.type == 'Eye':
                    sensor.h = 0.4
                if sensor.tag == 'Zoi':
                    sensor.h = 0.55
                Sensors.preprocessSensor(sensor, scale, 0.03, 0.03)
        Definitions.modelMatrix.pop()

OverMuscId = 0
SelectedMuscId = 0

def drawMuscleSurface(style):

    for i in range(0,len(muscles)):

        """ verify matrix validity """
        if muscles[i][modelMatrix] == []:
            continue


        """ choose vbo """
        vboId = Graphics.vboHexagon
        vboDraw = Graphics.vboSurfaces
        """ bind surfaces vbo """
        Graphics.indexPositions[vboId][vboDraw].bind()
        Graphics.vertexPositions[vboId].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        
        """ choose color """
        if style == Graphics.idBuffer:
            j = (i+1)/float(len(muscles))
            color = np.array([j,j,j,1.], dtype = np.float32)
        elif i+1 == SelectedMuscId:
            color = np.array([0.5,0,0.,0.3], dtype = np.float32)
        elif i+1 == OverMuscId:
            color = np.array([1,0,0,0.3], dtype = np.float32)
        else:
            color = np.array([1.,0.4,0.7,0.3], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
            
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, muscles[i][modelMatrix])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][vboDraw], Graphics.nbIndex[vboId][vboDraw], GL_UNSIGNED_INT, None)

        
def drawMuscleEdge(style):
        
    if style != Graphics.opaque and style != Graphics.blending:
        return

    for i in range(0,len(muscles)):

        """ verify matrix validity """
        if muscles[i][modelMatrix] == []:
            continue


        """ choose vbo """
        vboId = Graphics.vboHexagon
        vboDraw = Graphics.vboEdges
        """ bind surfaces vbo """
        Graphics.indexPositions[vboId][vboDraw].bind()
        Graphics.vertexPositions[vboId].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        if style == Graphics.opaque:
            color = np.array([0.5,0.5,0.5,1.], dtype = np.float32)
        elif style == Graphics.blending:
            if i+1 == SelectedMuscId:
                color = np.array([0.5,0.,0.,0.3], dtype = np.float32)
            elif i+1 == OverMuscId:
                color = np.array([1.,0.,0.,0.3], dtype = np.float32)
            else:
                color = np.array([0.5,0.7,0.7,0.3], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
        
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, muscles[i][modelMatrix])
            
        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][vboDraw], Graphics.nbIndex[vboId][vboDraw], GL_UNSIGNED_INT, None)


Tag = 0
A = 1
B = 2
modelMatrix = 3
Attach_tag = 0
Attach_local = 1
Attach_world = 2
muscles = [
           ["Biceps_r",       ["Arm_r",    [0.45, 0.5, 0, 1],         []],    ["Arm_r",       [-0.45, 0.5, 0, 1],          []],    []],
           ["Triceps_r",      ["Arm_r",    [0.45, -0.5, 0, 1],        []],    ["Arm_r",       [-0.45, -0.5, 0, 1],         []],    []],
           ["Biceps_l",       ["Arm_l",    [0.45, 0.5, 0, 1],         []],    ["Arm_l",       [-0.45, 0.5, 0, 1],          []],    []],
           ["Triceps_l",      ["Arm_l",    [0.45, -0.5, 0, 1],        []],    ["Arm_l",       [-0.45, -0.5, 0, 1],         []],    []],
           
           ["TAG",            ["Forearm_r",         [0.45, 0, 0.5, 1],         []],    ["Forearm_r",          [-0.45, 0, 0.5, 1],          []],    []],
           ["TAG",            ["Forearm_r",         [0.45, 0, -0.5, 1],        []],    ["Forearm_r",          [-0.45, 0, -0.5, 1],         []],    []],
           ["TAG",            ["Forearm_l",         [0.45, 0, 0.5, 1],         []],    ["Forearm_l",          [-0.45, 0, 0.5, 1],          []],    []],
           ["TAG",            ["Forearm_l",         [0.45, 0, -0.5, 1],        []],    ["Forearm_l",          [-0.45, 0, -0.5, 1],         []],    []],

           ["Achille_r",      ["Low_leg_r",     [0.45, 0, -0.5, 1],        []],    ["Low_leg_r",          [-0.45, 0, -0.5, 1],         []],    []],
           ["Achille_l",      ["Low_leg_l",     [0.45, 0, -0.5, 1],        []],    ["Low_leg_l",          [-0.45, 0, -0.5, 1],         []],    []]]