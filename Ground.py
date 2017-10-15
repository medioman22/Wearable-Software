
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import numpy as np

import Definitions
import Events
import Graphics
import Shaders
    
def preprocessGround(rMax = 5):
    Definitions.transform.push()
    Definitions.transform.rotate(90, 0, 0, 1)
    Definitions.transform.translate(-1.1, 0, 0)
    Definitions.transform.scale(1,3,3)

    i = -rMax
    while i <= rMax:
        j = -rMax
        while j <= rMax:
            dy = 0.75*i
            dz = 0.5*math.sqrt(3)*j + 0.25*math.sqrt(3)*i
            r = math.sqrt(dy*dy + dz*dz)
            if  r <= 0.501*math.sqrt(3)*rMax:
                """ transformation matrix update """
                Definitions.transform.push()
                Definitions.transform.translate(0.25*r, dy, dz)
                Definitions.transform.scale(0.5*r,1,1)

                Definitions.packagePreprocess[Graphics.vboHexagon] = Definitions.packagePreprocess[Graphics.vboHexagon] + [[Definitions.transform.peek(), "Ground"],]

                Definitions.transform.pop()
            j += 1
        i += 1
    Definitions.transform.pop()

def drawGround():
    if Events.style == Graphics.idBuffer:
        return

    vboId = -1
    for indices in Definitions.packageIndices[0]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]

        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboSurfaces].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.05], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboSurfaces], Graphics.nbIndex[vboId][Graphics.vboSurfaces], GL_UNSIGNED_INT, None)

    vboId = -1
    for indices in Definitions.packageIndices[0]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]

        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][Graphics.vboEdges].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.2], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)