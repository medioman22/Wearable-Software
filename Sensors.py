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

def displaySensor(sensor, l):
    """ shader access """

    """ send color to shader """
    glUniform4fv(Shaders.setColor_loc, 1, np.array([sensor.color[0], sensor.color[1], sensor.color[2], 1.], dtype = np.float32))

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
        Definitions.transform.scale(l,l,l)
        """ send transformation matrix to shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, Definitions.transform.peek())

        """ bind dashed vbo """
        Graphics.indexPositions[Graphics.vboDashed].bind()
        Graphics.vertexPositions[Graphics.vboDashed].bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ draw vbo """
        glDrawElements(GL_LINES, 6, GL_UNSIGNED_INT, None)
        Definitions.transform.pop()
        
    """ transformation matrix update """
    Definitions.transform.translate(l, 0, 0)
    Definitions.transform.scale(0.03,0.03,0.03)
    """ send transformation matrix to shader """
    Shaders.transform_loc = glGetUniformLocation(Shaders.shader, "transform")

    """ bind pyramide vbo """
    Graphics.indexPositions[Graphics.vboPyramide].bind()
    Graphics.vertexPositions[Graphics.vboPyramide].bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
    """ draw vbo """
    glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, Definitions.transform.peek())
    glDrawElements(GL_LINES, 12, GL_UNSIGNED_INT, None)
    Definitions.transform.pop()