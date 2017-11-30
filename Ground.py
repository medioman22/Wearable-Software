
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
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.rotate(90, 0, 0, 1)
    Definitions.modelMatrix.translate(-1.1, 0, 0)
    Definitions.modelMatrix.scale(1,3,3)

    i = -rMax
    while i <= rMax:
        j = -rMax
        while j <= rMax:
            dy = 0.75*i
            dz = 0.5*math.sqrt(3)*j + 0.25*math.sqrt(3)*i
            r = math.sqrt(dy*dy + dz*dz)
            if  r <= 0.501*math.sqrt(3)*rMax:
                """ model matrix update """
                Definitions.modelMatrix.push()
                Definitions.modelMatrix.translate(0.25*r, dy, dz)
                Definitions.modelMatrix.scale(0.5*r,1,1)

                Definitions.packagePreprocess[Graphics.vboHexagon] = Definitions.packagePreprocess[Graphics.vboHexagon] + [[Definitions.modelMatrix.peek(), "Ground"],]

                Definitions.modelMatrix.pop()
            j += 1
        i += 1
    Definitions.modelMatrix.pop()

def drawGround():
    if Events.style == Graphics.idBuffer:
        return
    if Events.showGround == False:
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
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

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
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack[Definitions.packModel])

        """ draw vbo """
        glDrawElements(Graphics.styleIndex[vboId][Graphics.vboEdges], Graphics.nbIndex[vboId][Graphics.vboEdges], GL_UNSIGNED_INT, None)