#
#   File : Limbs.py
#   
#   Code written by : Johann Heches
#
#   Description : Preprocess of limbs model matrix ; rendering of limb meshes.
#   





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
        self.angleRepos = [0,0,0]
        self.twist = [1,0,0,0]
        self.swing = [1,0,0,0]
        self.layer = 0
        self.modelMatrix = []
        self.vboId = 0
        self.mesh = None
        self.saturation = None
        self.selected = False
        self.show = Events.SHOW

            
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

    """ angle """
    angleTwist = Definitions.vector4D(entity.limbs[current_limb].twist).quatAngle()

    """ preprocess muscles attachment points """
    for i in range(0,len(entity.muscles)):
        if entity.muscles[i].A == entity.limbs[current_limb].tag:
            coordLocal = [entity.muscles[i].Alocal[0], entity.muscles[i].Alocal[1], entity.muscles[i].Alocal[2], entity.muscles[i].Alocal[3]]
            angle = (coordLocal[0]+0.5)*math.pi/180*angleTwist
            newY = coordLocal[1]*math.cos(angle) - coordLocal[2]*math.sin(angle)
            newZ = coordLocal[1]*math.sin(angle) + coordLocal[2]*math.cos(angle)
            coordLocal[1] = newY
            coordLocal[2] = newZ
            entity.muscles[i].Aworld = np.dot(np.array([coordLocal]), Definitions.modelMatrix.peek())
        if entity.muscles[i].B == entity.limbs[current_limb].tag:
            coordLocal = [entity.muscles[i].Blocal[0], entity.muscles[i].Blocal[1], entity.muscles[i].Blocal[2], entity.muscles[i].Blocal[3]]
            angle = (coordLocal[0]+0.5)*math.pi/180*angleTwist
            newY = coordLocal[1]*math.cos(angle) - coordLocal[2]*math.sin(angle)
            newZ = coordLocal[1]*math.sin(angle) + coordLocal[2]*math.cos(angle)
            coordLocal[1] = newY
            coordLocal[2] = newZ
            entity.muscles[i].Bworld = np.dot(np.array([coordLocal]), Definitions.modelMatrix.peek())
        if entity.muscles[i].C == entity.limbs[current_limb].tag:
            coordLocal = [entity.muscles[i].Clocal[0], entity.muscles[i].Clocal[1], entity.muscles[i].Clocal[2], entity.muscles[i].Clocal[3]]
            angle = (coordLocal[0]+0.5)*math.pi/180*angleTwist
            newY = coordLocal[1]*math.cos(angle) - coordLocal[2]*math.sin(angle)
            newZ = coordLocal[1]*math.sin(angle) + coordLocal[2]*math.cos(angle)
            coordLocal[1] = newY
            coordLocal[2] = newZ
            entity.muscles[i].Cworld = np.dot(np.array([coordLocal]), Definitions.modelMatrix.peek())
    
    """ preprocess sensors """
    for sensor in Sensors.virtuSens + Sensors.zoiSens:
        if sensor.attach == entity.limbs[current_limb].tag:
            sensor.h = 0.6
            if sensor.type == 'Eye':
                sensor.h = 0.4
            if ID.idCategory(sensor.id) == ID.ZOI:
                sensor.h = 0.55
            Definitions.modelMatrix.push()
            Qtw = Definitions.vector4D((angleTwist*(sensor.x+0.5),1,0,0))
            Definitions.modelMatrix.rotate(Qtw.o, Qtw.x, Qtw.y, Qtw.z)
            Sensors.preprocessSensor(sensor, x, y, z)
            Definitions.modelMatrix.pop()
    Definitions.modelMatrix.pop()



def drawBodySurface(entity, style, show):
    if Events.showBody == Events.HIDE\
    or Events.showBody == Events.FADE and show != Events.FADE\
    or Events.showBody == Events.FADE and style == Graphics.idBuffer:
        return


    global lookingAt
    
    """ bind surfaces vbo """
    entity.mesh.surfIndexPositions.bind()
    entity.mesh.vertexPositions.bind()
    i = -1
    for part in entity.limbs:
        i += 1
        if part.show == Events.FADE and show == Events.SHOW\
        or part.show == Events.SHOW and show == Events.FADE and Events.showBody != Events.FADE\
        or part.show == Events.FADE and style == Graphics.idBuffer:
            continue

        drawSaturation = False
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
        offset = ctypes.c_void_p(4*entity.mesh.surfIndexOffset[i]); #note : GL_UNSIGNED_INT is 4 bytes
        glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
        glDrawElements(entity.mesh.surfStyleIndex[i], entity.mesh.surfNbIndex[i], GL_UNSIGNED_INT, offset)
        
        if part.id == lookingAtID:
            lookingAt = np.dot(np.array([[0, 0, 0, 1]]), part.modelMatrix)

    
def drawBodyEdge(entity, style):
    if Events.showBody == Events.HIDE or Events.showBody == Events.FADE:
        return

    if style != Graphics.opaque and style != Graphics.blending:
        return
    
    
    """ bind edges vbo """
    entity.mesh.edgeIndexPositions.bind()
    entity.mesh.vertexPositions.bind()
    i = -1
    for part in entity.limbs:
        i+=1
        if part.show == Events.FADE or part.show == Events.HIDE:
            continue
                    
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
        offset = ctypes.c_void_p(4*entity.mesh.edgeIndexOffset[i]); #note : GL_UNSIGNED_INT is 4 bytes
        glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
        glDrawElements(entity.mesh.edgeStyleIndex[i], entity.mesh.edgeNbIndex[i], GL_UNSIGNED_INT, offset)


def setLimbsShow(entity, show):
    for part in entity.limbs:
        part.show = show

def showLimb(entity, tag):
    for part in entity.limbs:
        if part.tag == tag:
            part.show = Events.SHOW 