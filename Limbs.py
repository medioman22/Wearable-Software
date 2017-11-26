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



from OpenGL.GL import *
import numpy as np
import math

import Definitions
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
    """ store transformation in package """
    if entity.limbs[current_limb].tag == "Head":
        Definitions.packagePreprocess[Graphics.vboSphere] = Definitions.packagePreprocess[Graphics.vboSphere] + [[Definitions.modelMatrix.peek(), "Body", entity.limbs[current_limb].id, limbIsSelected],]
    else:
        Definitions.packagePreprocess[Graphics.vboCylindre] = Definitions.packagePreprocess[Graphics.vboCylindre] + [[Definitions.modelMatrix.peek(), "Body", entity.limbs[current_limb].id, limbIsSelected],]

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



def drawBodySurface(style):
    global lookingAt

    vboId = -1
    for indices in Definitions.packageIndices[1]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]
        
        drawSaturation = False
        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboSurfaces].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        """ choose color """
        if style == Graphics.idBuffer:
            r, g, b = ID.id2color(pack[Definitions.packID])
            color = np.array([r/255.,g/255.,b/255.,1.], dtype = np.float32)
        elif pack[Definitions.selected] == True:
            color = np.array([0.,0.,0.5,0.3], dtype = np.float32)
            drawSaturation = True
        elif pack[Definitions.packID] == overLimbId:
            color = np.array([0.,0.,1.,0.3], dtype = np.float32)
        else:
            color = np.array([1.,1.,1.,0.3], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)
        
        if pack[Definitions.packID] == lookingAtID:
            lookingAt = np.dot(np.array([[0, 0, 0, 1]]), pack[Definitions.packModel])

    
def drawBodyEdge(style):
    if style != Graphics.opaque and style != Graphics.blending:
        return

    vboId = -1
    for indices in Definitions.packageIndices[1]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]
                
        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboEdges].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
                    
        """ choose color """
        if style == Graphics.opaque:
            color = np.array([0.5,0.5,0.5,1.], dtype = np.float32)
        elif style == Graphics.blending:
            if pack[Definitions.selected] == True:
                color = np.array([0.,0.,0.5,0.3], dtype = np.float32)
            elif pack[Definitions.packID] == overLimbId:
                color = np.array([0.,0.,1.,0.3], dtype = np.float32)
            else:
                color = np.array([1.,1.,1.,1.], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
    
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)
