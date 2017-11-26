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


def preprocessSaturations(entity):
    Graphics.SaturationVertexPositions = []
    Graphics.SaturationIndexPositions = []
    Graphics.SaturationNbIndex = []
    Graphics.SaturationStyleIndex = []
    for part in entity.limbs:
        Graphics.VBO_hypar((part.saturations))
        

def drawSaturationLines():
    if Events.style != Graphics.idBuffer:
        vboId = 0
        edgeSurf = 0
        for saturation in Graphics.SaturationModelMatrix:
            vboId = saturation[1]
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, saturation[0])

            color = np.array([0.,1.,0.,0.8], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            Graphics.SaturationIndexPositions[vboId][edgeSurf].bind()
            Graphics.SaturationVertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
            glDrawElements(Graphics.SaturationStyleIndex[vboId][edgeSurf], Graphics.SaturationNbIndex[vboId][edgeSurf], GL_UNSIGNED_INT, None)

            
def drawSaturationBalls():
    if Events.style != Graphics.idBuffer:
        vboId = 0
        edgeSurf = 0
        for saturation in Graphics.SaturationModelMatrix:
            vboId = saturation[1]
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, saturation[0])

            color = np.array([0.5,0.5,0.5,0.1], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            Graphics.indexPositions[Graphics.vboSphere][Graphics.vboSurfaces].bind()
            Graphics.vertexPositions[Graphics.vboSphere].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
            glDrawElements(Graphics.styleIndex[Graphics.vboSphere][Graphics.vboSurfaces], Graphics.nbIndex[Graphics.vboSphere][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)

        vboId = -1