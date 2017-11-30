class limb(object):
    """
        limb
    """

    def __init__(self): # add orientation sometime...
        """ constructor """
        self.id = 0
        self.tag = ''
        self.offset = [0,0,0]
        self.dimensions = [0,0,0]
        self.saturations = [0,0,0,0,0,0]
        self.angleRepos = [0,0,0]
        self.twist = [1,0,0,0]
        self.swing = [1,0,0,0]
        self.angle = [1,0,0,0]
        self.layer = 0
        self.modelMatrix = []
        self.vbo = 0
        self.selected = False
        self.show = Events.SHOW



from OpenGL.GL import *
import numpy as np
import math

import Definitions
import Events
import Graphics
import ID
import Muscles
import Sensors
import Shaders


            
overLimbId = 0
lookingAt = np.array([[0, 0, 0, 1]])
lookingAtID = 0

def preprocessLimb(entity,x,y,z,dx,dy,dz,limbIsSelected, current_limb):
    """ limb transformations """
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.translate(dx,dy,dz)
    Definitions.modelMatrix.scale(x,y,z)
    entity.limbs[current_limb].modelMatrix = Definitions.modelMatrix.peek()

    """ limb is selected ? """
    entity.limbs[current_limb].selected = limbIsSelected

    """ preprocess muscles attachment points """
    for i in range(0,len(entity.muscles)):
        if entity.muscles[i].A == entity.limbs[current_limb].tag:
            entity.muscles[i].Aworld = np.dot(np.array([entity.muscles[i].Alocal]), Definitions.modelMatrix.peek())
        if entity.muscles[i].B == entity.limbs[current_limb].tag:
            entity.muscles[i].Bworld = np.dot(np.array([entity.muscles[i].Blocal]), Definitions.modelMatrix.peek())
    
    """ preprocess sensors """
    for sensor in Sensors.virtuSens + Sensors.zoiSens:
        if sensor.attach == entity.limbs[current_limb].tag:
            sensor.h = 0.6
            if sensor.type == 'Eye':
                sensor.h = 0.4
            if ID.idCategory(sensor.id) == ID.ZOI:
                sensor.h = 0.55
            Sensors.preprocessSensor(sensor, x, y, z)


            # TODO : do all same vbo together !!
def drawBodySurface(entity, style, show):
    if Events.showBody == Events.HIDE or Events.showBody == Events.FADE and style == Graphics.idBuffer:
        return


    global lookingAt

    vboId = -1
    for part in entity.limbs:
        if part.show == Events.FADE and show == 1\
        or part.show == Events.SHOW and show == 0\
        or part.show == Events.FADE and style == Graphics.idBuffer:
            continue

        drawSaturation = False
        if vboId != part.vbo:
            """ choose vbo """
            vboId = part.vbo
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboSurfaces].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        """ choose color """
        alpha = 0.3
        if Events.showBody == Events.FADE or part.show == Events.FADE:
            alpha = 0.1
        if style == Graphics.idBuffer:
            r, g, b = ID.id2color(part.id)
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
        elif part.selected == True:
            color = np.array([0.,0.,0.5,alpha], dtype = np.float32)
            drawSaturation = True
        elif part.id == overLimbId:
            color = np.array([0.,0.,1.,alpha], dtype = np.float32)
        else:
            color = np.array([1.,1.,1.,alpha], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, part.modelMatrix)

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)
        
        if part.id == lookingAtID:
            lookingAt = np.dot(np.array([[0, 0, 0, 1]]), part.modelMatrix)

    
def drawBodyEdge(entity, style):
    if Events.showBody == Events.HIDE or Events.showBody == Events.FADE:
        return

    if style != Graphics.opaque and style != Graphics.blending:
        return
    

    vboId = -1
    for part in entity.limbs:
        if part.show == Events.FADE or part.show == Events.HIDE:
            continue
        if vboId != part.vbo:
            """ choose vbo """
            vboId = part.vbo
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboEdges].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
                    
        """ choose color """
        if style == Graphics.opaque:
            color = np.array([0.5,0.5,0.5,1.], dtype = np.float32)
        elif style == Graphics.blending:
            if part.selected == True:
                color = np.array([0.,0.,0.5,0.3], dtype = np.float32)
            elif part.id == overLimbId:
                color = np.array([0.,0.,1.,0.3], dtype = np.float32)
            else:
                color = np.array([1.,1.,1.,1.], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
    
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, part.modelMatrix)

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)


def setLimbsShow(entity, show):
    for part in entity.limbs:
        part.show = show

def showLimb(entity, tag):
    for part in entity.limbs:
        if part.tag == tag:
            part.show = Events.SHOW 