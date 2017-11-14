from OpenGL.GL import *
import numpy as np
import math

import Cursor
import Definitions
import Events
import Graphics
import Muscles
import Sensors
import Shaders


class characteristics(object):
    """
        characteristics
        .o      rotation angle
        .xyz    rotation axis
    """
    __name__ = "characteristics"
    nb__init__ = 0 # keeps track of how many creations there are


    def __init__(self, ini = 1.70, coord = (0, 0, 0), parts = []): # add orientation sometime...
        """ constructor """
        characteristics.nb__init__ += 1
        self.size = ini # change to a 3D scale after ?
        self.x = coord[0]
        self.y = coord[1]
        self.z = coord[2]
        self.parts = parts

    @classmethod
    def feedback(cls,reset = False):
        """ print feedback on class calls """
        print("nb__init__ : {}".format(characteristics.nb__init__))
        if reset == True:
            characteristics.nb__init__ = 0
            print("reset for {} is done".format(cls.__name__))
        print("\n")
        

    def values(self):
        """ print characteristics values """
        print(self.size, self.x, self.y, self.z)
        for p in self.parts:
            print(p)

            
part = -1 # global helps through recursivity
overPartId = 0
selectedParts = []
virtuMan = None
lookingAt = np.array([[0, 0, 0, 1]])
lookingAtID = 0
def preprocessPart(x,y,z,dx,dy,dz,partIsSelected, ID):
    """ part transformations """
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.translate(dx,dy,dz)
    Definitions.modelMatrix.scale(x,y,z)
    """ store transformation in package """
    if parts[ID][Data_id] == "Head":
        Definitions.packagePreprocess[Graphics.vboSphere] = Definitions.packagePreprocess[Graphics.vboSphere] + [[Definitions.modelMatrix.peek(), "Body", ID, partIsSelected],]
    elif parts[ID][Data_id] == "Hat":
        Definitions.packagePreprocess[Graphics.vboCone] = Definitions.packagePreprocess[Graphics.vboCone] + [[Definitions.modelMatrix.peek(), "Body", ID, partIsSelected],]
    else:
        Definitions.packagePreprocess[Graphics.vboCylindre] = Definitions.packagePreprocess[Graphics.vboCylindre] + [[Definitions.modelMatrix.peek(), "Body", ID, partIsSelected],]

    """ preprocess muscles attachment points """
    for i in range(0,len(Muscles.muscles)):
        if Muscles.muscles[i][Muscles.A][Muscles.Attach_tag] == parts[ID][Data_id]:
            Muscles.muscles[i][Muscles.A][Muscles.Attach_world] = np.dot(np.array([Muscles.muscles[i][Muscles.A][Muscles.Attach_local]]), Definitions.modelMatrix.peek())
        if Muscles.muscles[i][Muscles.B][Muscles.Attach_tag] == parts[ID][Data_id]:
            Muscles.muscles[i][Muscles.B][Muscles.Attach_world] = np.dot(np.array([Muscles.muscles[i][Muscles.B][Muscles.Attach_local]]), Definitions.modelMatrix.peek())



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
            i = (pack[Definitions.packID])/float(len(parts)-1)
            color = np.array([i,0.,0.,1.], dtype = np.float32)
        elif pack[Definitions.selected] == True:
            color = np.array([0.,0.,0.5,0.3], dtype = np.float32)
            drawSaturation = True
        elif pack[Definitions.packID] == overPartId:
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
            elif pack[Definitions.packID] == overPartId:
                color = np.array([0.,0.,1.,0.3], dtype = np.float32)
            else:
                color = np.array([1.,1.,1.,1.], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)
    
        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)


""" recursive function that goes through all body parts and sensors """
def stick(entity = characteristics(), offset = (0,0,0), rotation = (0,0,0,0)):
    global part
    global selectedPart
    if part + 1 >= len(entity.parts):
        return

    part += 1
    current_part = part

    """ Check if part is selected """
    partIsSelected = False
    for selectedPart in selectedParts:
        if selectedPart == entity.parts[current_part][Data_id]:
            partIsSelected = True
            break
        if selectedPart == 'Wrist' and entity.parts[current_part][Data_id] == "Origin":
            partIsSelected = True
            break

    """ default orientation of part """
    l = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0, entity.parts[current_part][Data_angleRepos][0], entity.parts[current_part][Data_angleRepos][1], entity.parts[current_part][Data_angleRepos][2])))

    """ current rotation of part """
    q = Definitions.vector4D((entity.parts[current_part][Data_angle]))

    """ new rotation to implement """
    if partIsSelected == True:
        """ swing command with saturations """
        sw = Definitions.vector4D.Swing(Definitions.vector4D((entity.parts[current_part][Data_swing])), (entity.parts[current_part][Data_saturation]))
        entity.parts[current_part][Data_swing] = [sw.o,sw.x,sw.y,sw.z]

        """ twist command with saturations """
        tw = Definitions.vector4D.Twist(Definitions.vector4D((entity.parts[current_part][Data_twist])), (entity.parts[current_part][Data_saturation]))
        entity.parts[current_part][Data_twist] = [tw.o,tw.x,tw.y,tw.z]

        """ resulting orientation of part ... """
        q = Definitions.vector4D.QuatProd(sw, tw)
        entity.parts[current_part][Data_angle] = [q.o,q.x,q.y,q.z]
    

    """ Transformations """
    Definitions.modelMatrix.push()
    """ offset to apply """
    glTranslatef(offset[0] + entity.size*entity.parts[current_part][Data_offset][0], offset[1] + entity.size*entity.parts[current_part][Data_offset][1], offset[2] + entity.size*entity.parts[current_part][Data_offset][2])
    Definitions.modelMatrix.translate(offset[0] + entity.size*entity.parts[current_part][Data_offset][0], offset[1] + entity.size*entity.parts[current_part][Data_offset][1], offset[2] + entity.size*entity.parts[current_part][Data_offset][2])
    
    if partIsSelected == True:
        Definitions.modelMatrix.push()
        
        Cy = 0.5*(entity.parts[current_part][Data_saturation][2]+entity.parts[current_part][Data_saturation][3])
        Cz = 0.5*(entity.parts[current_part][Data_saturation][4]+entity.parts[current_part][Data_saturation][5])
        Qoffset = Definitions.vector4D.Eul2Quat(Definitions.vector4D((0,0,Cy,Cz)))
        p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,Qoffset))
        if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
            Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)
        scale = 2*entity.size*entity.parts[current_part][Data_dimensions][0]
        Definitions.modelMatrix.scale(scale,scale,scale)
        
        Graphics.SaturationModelMatrix = Graphics.SaturationModelMatrix + [[Definitions.modelMatrix.peek(),current_part]]

        Definitions.modelMatrix.pop()

    """ total rotation to apply """
    p = Definitions.vector4D.Quat2Vec(Definitions.vector4D.QuatProd(l,q))
    if math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z) >= 0.0001:
        Definitions.modelMatrix.rotate(p.o, p.x, p.y, p.z)
        
        
    """ preprocess part """
    x = entity.size*entity.parts[current_part][Data_dimensions][0]
    y = entity.size*entity.parts[current_part][Data_dimensions][1]
    z = entity.size*entity.parts[current_part][Data_dimensions][2]
    dx = 0.5*entity.size*entity.parts[current_part][Data_dimensions][0]
    dy = 0
    dz = 0
    preprocessPart(x,y,z,dx,dy,dz,partIsSelected, part)

    """ preprocess sensors """
    for sensor in Sensors.virtuSens + Sensors.zoiSens:
        if sensor.attach == entity.parts[current_part][Data_id]:
            sensor.h = 0.6
            if sensor.type == 'Eye':
                sensor.h = 0.4
            if sensor.tag == 'Zoi':
                sensor.h = 0.55
            Sensors.preprocessSensor(sensor, x, y, z)
    Definitions.modelMatrix.pop()


    """ recursive call for all parts attached to the current one """
    while part + 1 < len(entity.parts) and entity.parts[part+1][Data_layer] > entity.parts[current_part][Data_layer]:
        stick(entity, (x, 0, 0), (0,0,0,0))

    Definitions.modelMatrix.pop()



fi_a = 0.0323
fi_b = 0.0153
fi_c = 0.0141
"""
    0 - id : char string
    1 - offset x,y,z : ratio of characteristics.size
    2 - dimensions x,y,z : ratio of characteristics.size
    3 - saturation x+, x-, y+,y- ,z+ ,z- : degrees [180;-180]
    4 - angleRepos x,y,z : degrees
    5 - angle x,y,z : quaternion. (NOTE : it is not possible to convert back to euler angles so we stay in quaternion form here. anyways it would require more computation as well.)
    6 - layer : if layer(p+1) > layer(p), build from part(p). else close part(p) and repeat while a part is open.
    Note : the Torse shares it's saturations with the Wrist. To move the Wrist, move instead the Torse + Origin
"""
Data_id = 0
Data_offset = 1
Data_dimensions = 2
Data_saturation = 3
Data_angleRepos = 4
Data_twist = 5
Data_swing = 6
Data_angle = 7
Data_layer = 8
parts = [
    ["Origin",          [0, 0, 0],          [0., 0., 0.],                 [180, -180, 180, -180, 180, -180],   [0, 0, 90],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          0],
    ["Wrist",           [0, 0, 0],          [0.191, 0.15, 0.05],          [0, 0, 0, 0, 0, 0],                  [0, 0, 180],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          1],
    ["Upp_leg_r",       [0, 0.075, 0],      [0.195, 0.1, 0.1],            [45, -45, 90, -60, 45, -30],         [0, -90, 0],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          2],
    ["Low_leg_r",       [0, 0, 0],          [0.246, 0.08, 0.08],          [45, -45, 150, 0, 0, 0],             [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          3],
    ["Feet_r",          [0, 0, 0],          [0.0882, 0.0588, 0.02],       [5, -15, 60, -15, 0, 0],             [0, -90, 0],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          4],
    ["Upp_leg_l",       [0, -0.075, 0],     [0.195, 0.1, 0.1],            [45, -45, 90, -60, 30, -45],         [0, -90, 0],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          2],
    ["Low_leg_l",       [0, 0, 0],          [0.246, 0.08, 0.08],          [45, -45, 150, 0, 0, 0],             [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          3],
    ["Feet_l",          [0, 0, 0],          [0.0882, 0.0588, 0.02],       [15, -5, 60, -15, 0, 0],             [0, -90, 0],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          4],
    ["Torse",           [0, 0, 0],          [0.169, 0.15, 0.05],          [15, -15, 30, -60, 45, -45],         [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          1],
    ["Neck",            [0, 0, 0],          [0.052, 0.03, 0.03],          [0, 0, 15, -60, 30, -30],            [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          2],
    ["Head",            [0, 0, 0],          [0.13, 0.08, 0.08],           [60, -60, 30, -30, 15, -15],         [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          3],
    #["Hat",             [-0.06, 0, 0],      [0.07, 0.3, 0.3],             [0, 0, 0, 0, 0, 0],                  [0, 0, 0],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          4],
    ["Shoulder_r",      [0, 0, 0],          [0.106, 0.04, 0.04],          [15, -15, 15, -15, 15, -60],         [0, 0, 90],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          2],
    ["Arm_r",           [0, 0, 0],          [0.136, 0.06, 0.06],          [90, -90, 60, -60, 90, -45],         [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          3],
    ["Forearm_r",       [0, 0, 0],          [0.146, 0.04, 0.04],          [90, -90, 0, -150, 0, 0],            [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          4],
    ["Hand_r",          [0, 0, 0],          [0.0588, 0.06, 0.02],         [0, 0, 90, -90, 60, -15],            [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          5],
    ["Finger_r_1a",     [-0.04, -0.03, 0],  [fi_a, 0.01, 0.01],           [0, 0, 45, -60, 30, -30],            [0, 0, -30],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_r_1b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [-90, 0, 0],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_1c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_2a",     [0, -0.03, 0],      [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, -15],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_r_2b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_2c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_3a",     [0, -0.01, 0],      [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, -5],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_r_3b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_3c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_4a",     [0, 0.01, 0],       [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, 5],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_r_4b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_4c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_5a",     [0, 0.03, 0],       [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, 15],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_r_5b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_5c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Shoulder_l",      [0, 0, 0],          [0.106, 0.04, 0.04],          [15, -15, 15, -15, 60, -15],         [0, 0, -90],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          2],
    ["Arm_l",           [0, 0, 0],          [0.136, 0.06, 0.06],          [90, -90, 60, -60, 45, -90],         [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          3],
    ["Forearm_l",       [0, 0, 0],          [0.146, 0.04, 0.04],          [90, -90, 0, -150, 0, 0],            [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          4],
    ["Hand_l",          [0, 0, 0],          [0.0588, 0.06, 0.02],         [0, 0, 90, -90, 15, -60],            [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          5],
    ["Finger_l_1a",     [-0.04, 0.03, 0],   [fi_a, 0.01, 0.01],           [0, 0, 45, -60, 30, -30],            [0, 0, 30],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_l_1b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [90, 0, 0],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_1c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_2a",     [0, 0.03, 0],       [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, 15],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_l_2b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_2c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_3a",     [0, 0.01, 0],       [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, 5],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_l_3b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_3c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_4a",     [0, -0.01, 0],      [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, -5],         [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_l_4b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_4c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_5a",     [0, -0.03, 0],      [fi_a, 0.01, 0.01],           [0, 0, 45, -90, 25, -25],            [0, 0, -15],        [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          6],
    ["Finger_l_5b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_5c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          [1, 0, 0, 0],          8]
    ]