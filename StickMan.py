from OpenGL.GL import *
import numpy as np

import Cursor
import Graphics
import Definitions
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

            
selectedParts = [("Origin"),]
virtuMan = None

def preprocessPart(x,y,z,dx,dy,dz,partIsSelected, ID):

    """ part transformations """
    Definitions.transform.push()
    Definitions.transform.translate(dx,dy,dz)
    Definitions.transform.scale(x,y,z)
    
    """ store transformation in package """
    Definitions.packageStickMan = Definitions.packageStickMan + [[Definitions.transform.peek(), partIsSelected, ID],]

    Definitions.transform.pop()


def drawStickMan(style):
    """ send color to shader """
    glUniform4fv(Shaders.setColor_loc, 1, np.array([1.,1.,1.,0.3], dtype = np.float32))
    """ bind cube surfaces vbo """
    Graphics.indexPositions[Graphics.vboCube][Graphics.vboSurfaces].bind()
    Graphics.vertexPositions[Graphics.vboCube].bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
    """ draw all at once """
    i = 0
    for pack in Definitions.packageStickMan:
        i +=1./len(Definitions.packageStickMan)
        if pack[1] == True:
            glUniform4fv(Shaders.setColor_loc, 1, np.array([0.,0.,1.,0.3], dtype = np.float32))
        if style == 3:
            glUniform4fv(Shaders.setColor_loc, 1, np.array([i,0.,0.,1.], dtype = np.float32))
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[0])
        """ draw vbo """
        glDrawElements(GL_QUADS, 24, GL_UNSIGNED_INT, None)
        if pack[1] == True:
            glUniform4fv(Shaders.setColor_loc, 1, np.array([1.,1.,1.,0.3], dtype = np.float32))

    
    """ send color to shader """
    if style == Graphics.opaque:
        glUniform4fv(Shaders.setColor_loc, 1, np.array([0.5,0.5,0.5,1.], dtype = np.float32))
    elif style == Graphics.blending:
        glUniform4fv(Shaders.setColor_loc, 1, np.array([1.,1.,1.,1.], dtype = np.float32))
    if style == Graphics.opaque or style == Graphics.blending:
        """ bind cube edges vbo """
        Graphics.indexPositions[Graphics.vboCube][Graphics.vboEdges].bind()
        Graphics.vertexPositions[Graphics.vboCube].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        """ draw all at once """
        for pack in Definitions.packageStickMan:
            glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[0])
            """ draw vbo """
            glDrawElements(GL_LINES, 48, GL_UNSIGNED_INT, None)

            


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
Data_angle = 5
Data_layer = 6
parts = [
    ["Origin",          [0, 0, 0],          [0., 0., 0.],                 [180, -180, 180, -180, 180, -180],   [0, 0, 90],         [1, 0, 0, 0],          0],
    ["Wrist",           [0, 0, 0],          [0.191, 0.15, 0.05],          [0, 0, 0, 0, 0, 0],                  [0, 0, 180],        [1, 0, 0, 0],          1],
    ["Upp_leg_r",       [0, 0.075, 0],      [0.195, 0.1, 0.1],            [45, -45, 0, -90, 30, -30],          [0, 0, 0],          [1, 0, 0, 0],          2],
    ["Low_leg_r",       [0, 0, 0],          [0.246, 0.08, 0.08],          [45, -45, 150, 0, 0, 0],             [0, 0, 0],          [1, 0, 0, 0],          3],
    ["Feet_r",          [0, 0, 0],          [0.0882, 0.0588, 0.02],       [5, -15, 60, -15, 0, 0],             [0, -90, 0],        [1, 0, 0, 0],          4],
    ["Upp_leg_l",       [0, -0.075, 0],     [0.195, 0.1, 0.1],            [45, -45, 0, -90, 30, -30],          [0, 0, 0],          [1, 0, 0, 0],          2],
    ["Low_leg_l",       [0, 0, 0],          [0.246, 0.08, 0.08],          [45, -45, 150, 0, 0, 0],             [0, 0, 0],          [1, 0, 0, 0],          3],
    ["Feet_l",          [0, 0, 0],          [0.0882, 0.0588, 0.02],       [15, -5, 60, -15, 0, 0],             [0, -90, 0],        [1, 0, 0, 0],          4],
    ["Torse",           [0, 0, 0],          [0.169, 0.15, 0.05],          [15, -15, 30, -60, 45, -45],         [0, 0, 0],          [1, 0, 0, 0],          1],
    ["Neck",            [0, 0, 0],          [0.052, 0.03, 0.03],          [0, 0, 15, -60, 30, -30],            [0, 0, 0],          [1, 0, 0, 0],          2],
    ["Head",            [0, 0, 0],          [0.130, 0.08, 0.08],          [60, -60, 30, -30, 15, -15],         [0, 0, 0],          [1, 0, 0, 0],          3],
    ["Shoulder_r",      [0, 0, 0],          [0.106, 0.04, 0.04],          [0, 0, 0, -15, 15, -15],             [0, 0, 90],         [1, 0, 0, 0],          2],
    ["Arm_r",           [0, 0, 0],          [0.136, 0.06, 0.06],          [90, -90, 60, -60, 90, 0],           [0, 0, 0],          [1, 0, 0, 0],          3],
    ["Forearm_r",       [0, 0, 0],          [0.146, 0.04, 0.04],          [90, -90, 0, -150, 0, 0],            [0, 0, 0],          [1, 0, 0, 0],          4],
    ["Hand_r",          [0, 0, 0],          [0.0588, 0.06, 0.02],         [0, 0, 90, -90, 15, -15],            [0, 0, 5],          [1, 0, 0, 0],          5],
    ["Finger_r_1a",     [-0.04, -0.03, 0],  [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, -30],        [1, 0, 0, 0],          6],
    ["Finger_r_1b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_1c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_2a",     [0, -0.03, 0],      [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, -15],        [1, 0, 0, 0],          6],
    ["Finger_r_2b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_2c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_3a",     [0, -0.01, 0],      [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, -5],         [1, 0, 0, 0],          6],
    ["Finger_r_3b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_3c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_4a",     [0, 0.01, 0],       [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, 5],          [1, 0, 0, 0],          6],
    ["Finger_r_4b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_4c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_r_5a",     [0, 0.03, 0],       [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, 15],         [1, 0, 0, 0],          6],
    ["Finger_r_5b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_r_5c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Shoulder_l",      [0, 0, 0],          [0.106, 0.04, 0.04],          [0, 0, 0, -15, 15, -15],             [0, 0, -90],        [1, 0, 0, 0],          2],
    ["Arm_l",           [0, 0, 0],          [0.136, 0.06, 0.06],          [90, -90, 60, -60, 0, -90],          [0, 0, 0],          [1, 0, 0, 0],          3],
    ["Forearm_l",       [0, 0, 0],          [0.146, 0.04, 0.04],          [90, -90, 0, -150, 0, 0],            [0, 0, 0],          [1, 0, 0, 0],          4],
    ["Hand_l",          [0, 0, 0],          [0.0588, 0.06, 0.02],         [0, 0, 90, -90, 15, -15],            [0, 0, -5],         [1, 0, 0, 0],          5],
    ["Finger_l_1a",     [-0.04, 0.03, 0],   [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, 30],         [1, 0, 0, 0],          6],
    ["Finger_l_1b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_1c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_2a",     [0, 0.03, 0],       [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, 15],         [1, 0, 0, 0],          6],
    ["Finger_l_2b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_2c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_3a",     [0, 0.01, 0],       [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, 5],          [1, 0, 0, 0],          6],
    ["Finger_l_3b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_3c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_4a",     [0, -0.01, 0],      [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, -5],         [1, 0, 0, 0],          6],
    ["Finger_l_4b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_4c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8],
    ["Finger_l_5a",     [0, -0.03, 0],      [fi_a, 0.01, 0.01],           [0, 0, 0, -90, 10, -10],             [0, 0, -15],        [1, 0, 0, 0],          6],
    ["Finger_l_5b",     [0, 0, 0],          [fi_b, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          7],
    ["Finger_l_5c",     [0, 0, 0],          [fi_c, 0.01, 0.01],           [0, 0, 0, -90, 0, 0],                [0, 0, 0],          [1, 0, 0, 0],          8]
    ]