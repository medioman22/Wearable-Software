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
import StickMan


def preprocessSaturations(entity):
    Graphics.SaturationVertexPositions = []
    Graphics.SaturationIndexPositions = []
    Graphics.SaturationNbIndex = []
    Graphics.SaturationStyleIndex = []
    for part in entity.parts:
        Graphics.VBO_hypar((part[StickMan.Data_saturation]))
        

def drawSaturations():
    if Events.style != Graphics.idBuffer:
        vboId = 0
        edgeSurf = 0
        for saturation in Graphics.SaturationModelMatrix:
            vboId = saturation[1]
            color = np.array([0.,1.,0.,0.3], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, saturation[0])
            Graphics.SaturationIndexPositions[vboId][edgeSurf].bind()
            Graphics.SaturationVertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
            glDrawElements(Graphics.SaturationStyleIndex[vboId][edgeSurf], Graphics.SaturationNbIndex[vboId][edgeSurf], GL_UNSIGNED_INT, None)
        vboId = -1