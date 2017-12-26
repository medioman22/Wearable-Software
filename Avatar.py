#
#   File : Avatar.py
#   
#   Code written by : Johann Heches
#
#   Description : Preprocess the avatar layer by layer.
#   


class characteristics(object):
    """
        characteristics
        .o      rotation angle
        .xyz    rotation axis
    """


    def __init__(self, ini = 1.70): # add orientation here or keep it on origin limb ?
        """ constructor """
        self.tag = ""
        self.size = ini # change to a 3D scale after ?
        self.position = [0, 0, 0]
        self.orientation = [1, 0, 0, 0]
        self.limbs = []
        self.mesh = None
        self.muscles = []




from OpenGL.GL import *
import numpy as np
import math

import Definitions
import Events
import Graphics
import ID
import Limbs
import Muscles



virtuMan = None

            
limb = -1 # global helps through recursivity
selectedLimbs = []

""" recursive function that generates limbs by layers """
def stick(entity, offset = (0,0,0)):
    global limb
    global selectedLimb
    if limb + 1 >= len(entity.limbs):
        return

    limb += 1
    current_limb = limb

    """ Check if limb is selected """
    limbIsSelected = False
    for selectedLimb in selectedLimbs:
        if selectedLimb == entity.limbs[current_limb].tag:
            limbIsSelected = True
            break

    """ default orientation of limb """
    l = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, entity.limbs[current_limb].angleRepos[0], entity.limbs[current_limb].angleRepos[1], entity.limbs[current_limb].angleRepos[2])))


    """ new rotation to implement """
    if limbIsSelected == True:
        """ swing command with saturations """
        sw = Definitions.vector4D.Swing(Definitions.vector4D((entity.limbs[current_limb].swing)), (entity.limbs[current_limb].saturation.saturations))
        entity.limbs[current_limb].swing = [sw.o,sw.x,sw.y,sw.z]

        """ twist command with saturations """
        tw = Definitions.vector4D.Twist(Definitions.vector4D((entity.limbs[current_limb].twist)), (entity.limbs[current_limb].saturation.saturations))
        entity.limbs[current_limb].twist = [tw.o,tw.x,tw.y,tw.z]

        """ twist effect on vbo """
        entity.limbs[current_limb].mesh.twistVBO(Definitions.vector4D(entity.limbs[current_limb].twist).quatAngle())


    """ current rotation of limb """
    Qsw = Definitions.vector4D((entity.limbs[current_limb].swing))
    Qtw = Definitions.vector4D((entity.limbs[current_limb].twist))
    

    """ Transformations """
    Definitions.modelMatrix.push()
    """ offset to apply """
    Definitions.modelMatrix.translate(offset[0] + entity.size*entity.limbs[current_limb].offset[0], offset[1] + entity.size*entity.limbs[current_limb].offset[1], offset[2] + entity.size*entity.limbs[current_limb].offset[2])
    
    if limbIsSelected == True:
        Definitions.modelMatrix.push()
        
        Cy = 0.5*(entity.limbs[current_limb].saturation.saturations[2]+entity.limbs[current_limb].saturation.saturations[3])
        Cz = 0.5*(entity.limbs[current_limb].saturation.saturations[4]+entity.limbs[current_limb].saturation.saturations[5])
        Qoffset = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0,0,Cy,Cz)))
        p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,Qoffset))
        if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
            Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)
        scale = 2*entity.size*entity.limbs[current_limb].dimensions[0]
        Definitions.modelMatrix.scale(scale,scale,scale)
        
        entity.limbs[current_limb].saturation.modelMatrix = Definitions.modelMatrix.peek()

        Definitions.modelMatrix.pop()

        
    """ total rotation to apply """
    p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,Qsw))
    if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
        Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)
        
    """ preprocess limb """
    x = entity.size*entity.limbs[current_limb].dimensions[0]
    y = entity.size*entity.limbs[current_limb].dimensions[1]
    z = entity.size*entity.limbs[current_limb].dimensions[2]
    dx = 0.5*entity.size*entity.limbs[current_limb].dimensions[0]
    dy = 0
    dz = 0
    Limbs.preprocessLimb(entity,x,y,z,dx,dy,dz,limbIsSelected, current_limb)

    
    """ total rotation to apply """
    p = Definitions.vector4D.Quat2Vec(Qtw)
    if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
        Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)

    """ recursive call for all limbs children to the current one """
    while limb + 1 < len(entity.limbs) and entity.limbs[limb+1].layer > entity.limbs[current_limb].layer:
        stick(entity, (x, 0, 0))

    Definitions.modelMatrix.pop()


def oneMesh(entity):
    entity.mesh = Graphics.mesh()
    entity.mesh.vertices = np.array([],    dtype='f')
    entity.mesh.surfIndices = np.array([],    dtype=np.int32)
    entity.mesh.edgeIndices = np.array([],    dtype=np.int32)
    entity.mesh.surfNbIndex = []
    entity.mesh.edgeNbIndex = []
    entity.mesh.surfIndexOffset = []
    entity.mesh.edgeIndexOffset = []
    entity.mesh.surfStyleIndex = []
    entity.mesh.edgeStyleIndex = []
    for limb in entity.limbs:
        entity.mesh.surfIndices = np.append(entity.mesh.surfIndices, limb.mesh.surfIndices + entity.mesh.vertices.size/3)
        entity.mesh.edgeIndices = np.append(entity.mesh.edgeIndices, limb.mesh.edgeIndices + entity.mesh.vertices.size/3)
        entity.mesh.vertices = np.append(entity.mesh.vertices, limb.mesh.vertices)
        if entity.mesh.surfIndexOffset != []:
            entity.mesh.surfIndexOffset = entity.mesh.surfIndexOffset + [entity.mesh.surfIndexOffset[-1] + entity.mesh.surfNbIndex[-1],]
            entity.mesh.edgeIndexOffset = entity.mesh.edgeIndexOffset + [entity.mesh.edgeIndexOffset[-1] + entity.mesh.edgeNbIndex[-1],]
        else:
            entity.mesh.surfIndexOffset = [0]
            entity.mesh.edgeIndexOffset = [0]
        entity.mesh.surfNbIndex = entity.mesh.surfNbIndex + [limb.mesh.surfNbIndex,]
        entity.mesh.edgeNbIndex = entity.mesh.edgeNbIndex + [limb.mesh.edgeNbIndex,]
        entity.mesh.surfStyleIndex = entity.mesh.surfStyleIndex + [limb.mesh.surfStyleIndex,]
        entity.mesh.edgeStyleIndex = entity.mesh.edgeStyleIndex + [limb.mesh.edgeStyleIndex,]
    Graphics.buildVBO(entity)