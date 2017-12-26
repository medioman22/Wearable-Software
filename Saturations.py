#
#   File : Saturations.py
#   
#   Code written by : Johann Heches
#
#   Description : Preprocess of saturations model matrix ; rendering of saturation meshes.
#   


class saturation(object):
    """
        saturation
    """

    def __init__(self): # add orientation sometime...
        """ constructor """
        self.saturations = None
        self.modelMatrix = []
        self.mesh = None


from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

from OpenGL.arrays import vbo
from OpenGL.raw.GL.ARB.vertex_array_object import glGenVertexArrays, \
                                                  glBindVertexArray
from ctypes import *
import numpy as np

import Events
import Graphics
import Shaders

saturationBall = None

def preprocessSaturations(part, saturations):
    part.saturation = saturation()
    part.saturation.saturations = saturations
    part.saturation.mesh = Graphics.VBO_hypar((part.saturation.saturations))
    Graphics.buildVBO(part.saturation)
        

def drawSaturationLines(entity):
    if Events.showSaturations == Events.HIDE:
        return
    

    if Events.style != Graphics.idBuffer:
        vboId = 0
        edgeSurf = 0
        for part in entity.limbs:
            if part.selected == False:
                continue
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, part.saturation.modelMatrix)

            color = np.array([0.,1.,0.,0.8], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            part.saturation.mesh.edgeIndexPositions.bind()
            part.saturation.mesh.vertexPositions.bind()
            glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
            glDrawElements(part.saturation.mesh.edgeStyleIndex,part.saturation.mesh.edgeNbIndex, GL_UNSIGNED_INT, None)

            
def drawSaturationBalls(entity):
    if Events.showSaturations == Events.HIDE or Events.showSaturations == Events.FADE:
        return
    
    
    if Events.style != Graphics.idBuffer:
        vboId = 0
        edgeSurf = 0
        for part in entity.limbs:
            if part.selected == False:
                continue
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, part.saturation.modelMatrix)

            color = np.array([0.5,0.5,0.5,0.1], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            saturationBall.mesh.surfIndexPositions.bind()
            saturationBall.mesh.vertexPositions.bind()
            glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
            glDrawElements(saturationBall.mesh.surfStyleIndex,saturationBall.mesh.surfNbIndex, GL_UNSIGNED_INT, None)