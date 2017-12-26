#
#   File : Muscles.py
#   
#   Code written by : Johann Heches
#
#   Description : Preprocess of muscles model matrix ; rendering of muscles meshes.
#   


class muscle(object):
    """
        muscle
    """

    def __init__(self): # add orientation sometime...
        """ constructor """
        self.id = 0
        self.tag = ''
        self.A = ""
        self.Alocal = []
        self.Aworld = []
        self.B = ""
        self.Blocal = []
        self.Bworld = []
        self.C = ""
        self.Clocal = []
        self.Cworld = []
        self.modelMatrix = []
        self.mesh = None
        self.selected = False
        self.show = Events.SHOW


from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

import Definitions
import Events
import Graphics
import ID
import Sensors
import Shaders

def preprocessMuscle(entity):

    for i in range(0,len(entity.muscles)):
        if entity.muscles[i].mesh == None:
            entity.muscles[i].mesh = Graphics.VBO_cylinder(6,2)
            Graphics.buildVBO(entity.muscles[i])

        P1 = entity.muscles[i].Aworld
        P2 = entity.muscles[i].Bworld
        P3 = entity.muscles[i].Cworld
        if P1 == [] or P2 == [] or P3 == []:
            continue

        """ set muscle model matrix """
        Ux = Definitions.vector4D((0, 1, 0, 0))
        Vx = Definitions.vector4D((0, P1[0][0]-P2[0][0], P1[0][1]-P2[0][1], P1[0][2]-P2[0][2]))
        scale = math.sqrt(Vx.x*Vx.x + Vx.y*Vx.y + Vx.z*Vx.z)
        center = Definitions.vector4D((0, 0.5*(P1[0][0]+P2[0][0]), 0.5*(P1[0][1]+P2[0][1]), 0.5*(P1[0][2]+P2[0][2])))
        Wx = Definitions.vector4D.AngleAxisBetween2Vec(Ux,Vx)
    
        Definitions.modelMatrix.push()
        Definitions.modelMatrix.set(Definitions.I)
        Definitions.modelMatrix.translate(center.x, center.y, center.z)
        Definitions.modelMatrix.rotate(Wx.o, Wx.x, Wx.y, Wx.z)

        """ readjust facing direction """
        uy = np.dot(np.array([0, 1, 0, 0]), Definitions.modelMatrix.peek()) # Note : not same as Ux because here it's [x,y,z,o] and in vector4D it's [o,x,y,z]
        vy = np.array([0.5*(P1[0][0]+P2[0][0])-P3[0][0], 0.5*(P1[0][1]+P2[0][1])-P3[0][1], 0.5*(P1[0][2]+P2[0][2])-P3[0][2], 0])
        Uy = Definitions.vector4D((0, uy[0], uy[1], uy[2]))
        Vy = Definitions.vector4D((0, vy[0], vy[1], vy[2]))
        Wy = Definitions.vector4D.AngleAxisBetween2Vec(Uy,Vy)
        if Definitions.vector4D.VecDot(Vx,Wy) < 0:
            Wy.o = -Wy.o

        Definitions.modelMatrix.rotate(Wy.o, 1, 0, 0)
            
        Definitions.modelMatrix.scale(scale,0.03,0.03)

        entity.muscles[i].modelMatrix = Definitions.modelMatrix.peek()

        
        for sensor in Sensors.virtuSens + Sensors.zoiSens:
            if sensor.attach == entity.muscles[i].tag:
                sensor.h = 0.6
                if sensor.type == 'Eye':
                    sensor.h = 0.4
                if ID.idCategory(sensor.id) == ID.ZOI:
                    sensor.h = 0.55
                Sensors.preprocessSensor(sensor, scale, 0.03, 0.03)
        Definitions.modelMatrix.pop()

OverMuscId = 0
SelectedMuscId = 0

def drawMuscleSurface(entity, style, show):
    if Events.showMuscles == False:
        return


    for i in range(0,len(entity.muscles)):
        if entity.muscles[i].show == Events.HIDE\
        or entity.muscles[i].show == Events.SHOW and show == Events.FADE:
            continue

        """ verify matrix validity """
        if entity.muscles[i].modelMatrix == []:
            continue


        """ choose vbo """
        #vboId = Graphics.vboHexagon
        #vboDraw = Graphics.vboSurfaces
        """ bind surfaces vbo """
        entity.muscles[i].mesh.surfIndexPositions.bind()
        entity.muscles[i].mesh.vertexPositions.bind()
        #Graphics.indexPositions[vboId][vboDraw].bind()
        #Graphics.vertexPositions[vboId].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        
        """ choose color """
        if style == Graphics.idBuffer:
            r, g, b = ID.id2color(entity.muscles[i].id)
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
        elif i+ID.offsetId(ID.MUSCLE) == SelectedMuscId:
            color = np.array([0.5,0,0.,0.3], dtype = np.float32)
        elif i+ID.offsetId(ID.MUSCLE) == OverMuscId:
            color = np.array([1,0,0,0.3], dtype = np.float32)
        else:
            color = np.array([1.,0.4,0.7,0.3], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
            
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, entity.muscles[i].modelMatrix)

        """ draw vbo """
        glDrawElements(entity.muscles[i].mesh.surfStyleIndex, entity.muscles[i].mesh.surfNbIndex, GL_UNSIGNED_INT, None)

        
def drawMuscleEdge(entity, style):
    if Events.showMuscles == False:
        return
        
    if style != Graphics.opaque and style != Graphics.blending:
        return

    for i in range(0,len(entity.muscles)):

        """ verify matrix validity """
        if entity.muscles[i].modelMatrix == []:
            continue


        """ choose vbo """
        #vboId = Graphics.vboHexagon
        #vboDraw = Graphics.vboEdges
        """ bind surfaces vbo """
        entity.muscles[i].mesh.edgeIndexPositions.bind()
        entity.muscles[i].mesh.vertexPositions.bind()
        #Graphics.indexPositions[vboId][vboDraw].bind()
        #Graphics.vertexPositions[vboId].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        if style == Graphics.opaque:
            color = np.array([0.5,0.5,0.5,1.], dtype = np.float32)
        elif style == Graphics.blending:
            if i+ID.offsetId(ID.MUSCLE) == SelectedMuscId:
                color = np.array([0.5,0.,0.,0.3], dtype = np.float32)
            elif i+ID.offsetId(ID.MUSCLE) == OverMuscId:
                color = np.array([1.,0.,0.,0.3], dtype = np.float32)
            else:
                color = np.array([0.5,0.7,0.7,0.3], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
        
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, entity.muscles[i].modelMatrix)
            
        """ draw vbo """
        glDrawElements(entity.muscles[i].mesh.edgeStyleIndex, entity.muscles[i].mesh.edgeNbIndex, GL_UNSIGNED_INT, None)


def setMusclesShow(entity, show):
    for part in entity.muscles:
        part.show = show

def showMuscle(entity, tag):
    for part in entity.muscles:
        if part.tag == tag:
            part.show = Events.SHOW 