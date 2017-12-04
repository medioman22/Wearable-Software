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

    """ current rotation of limb """
    q = Definitions.vector4D((entity.limbs[current_limb].angle))

    """ new rotation to implement """
    if limbIsSelected == True:
        """ swing command with saturations """
        sw = Definitions.vector4D.Swing(Definitions.vector4D((entity.limbs[current_limb].swing)), (entity.limbs[current_limb].saturations))
        entity.limbs[current_limb].swing = [sw.o,sw.x,sw.y,sw.z]

        """ twist command with saturations """
        tw = Definitions.vector4D.Twist(Definitions.vector4D((entity.limbs[current_limb].twist)), (entity.limbs[current_limb].saturations))
        entity.limbs[current_limb].twist = [tw.o,tw.x,tw.y,tw.z]

        """ resulting orientation of limb ... """
        q = Definitions.vector4D.QuatProd(sw, tw)
        entity.limbs[current_limb].angle = [q.o,q.x,q.y,q.z]
    

    """ Transformations """
    Definitions.modelMatrix.push()
    """ offset to apply """
    Definitions.modelMatrix.translate(offset[0] + entity.size*entity.limbs[current_limb].offset[0], offset[1] + entity.size*entity.limbs[current_limb].offset[1], offset[2] + entity.size*entity.limbs[current_limb].offset[2])
    
    if limbIsSelected == True:
        Definitions.modelMatrix.push()
        
        Cy = 0.5*(entity.limbs[current_limb].saturations[2]+entity.limbs[current_limb].saturations[3])
        Cz = 0.5*(entity.limbs[current_limb].saturations[4]+entity.limbs[current_limb].saturations[5])
        Qoffset = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0,0,Cy,Cz)))
        p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,Qoffset))
        if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
            Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)
        scale = 2*entity.size*entity.limbs[current_limb].dimensions[0]
        Definitions.modelMatrix.scale(scale,scale,scale)
        
        Graphics.SaturationModelMatrix = Graphics.SaturationModelMatrix + [[Definitions.modelMatrix.peek(),current_limb]]

        Definitions.modelMatrix.pop()

    """ total rotation to apply """
    p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,q))
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

    Definitions.modelMatrix.pop()


    """ recursive call for all limbs children to the current one """
    while limb + 1 < len(entity.limbs) and entity.limbs[limb+1].layer > entity.limbs[current_limb].layer:
        stick(entity, (x, 0, 0))

    Definitions.modelMatrix.pop()