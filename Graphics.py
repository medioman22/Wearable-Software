import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import time
import numpy as np

import Definitions
import Shaders



vertexPositions = []
indexPositions = []


vboCube = 0
vboPyramide = 1
vboDashed = 2
vboHexagon = 3
vboEdges = 0
vboSurfaces = 1
def VBO_init():
    global vertexPositions
    global indexPositions
    """ init VBO & EBO buffers """
    VBO_init = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_init)

    EBO_init = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_init)

    """ Create the "cube" VBO & index buffer arrays """
    cubeVertices = np.array([[-0.5,-0.5,-0.5],  [0.5,-0.5,-0.5],    [0.5,0.5,-0.5],     [-0.5,0.5,-0.5],    \
                             [-0.5,-0.5,0.5],   [0.5,-0.5,0.5],     [0.5,0.5,0.5],      [-0.5,0.5,0.5]],    dtype='f')
    cubeIndices = np.array([[0,1,   1,2,    2,3,    3,0,    \
                             0,4,   4,5,    5,1,    1,0,    \
                             1,5,   5,6,    6,2,    2,1,    \
                             2,6,   6,7,    7,3,    3,2,    \
                             3,7,   7,4,    4,0,    0,3,    \
                             7,6,   6,5,    5,4,    4,7,    ]], dtype=np.int32)
    kubeIndices = np.array([[0,1,2,3,    \
                             0,4,5,1,    \
                             1,5,6,2,    \
                             2,6,7,3,    \
                             3,7,4,0,    \
                             7,6,5,4,    ]], dtype=np.int32)

    """ Create the "pyramide" VBO & index buffer arrays """
    pyramideVertices = np.array([[0,0,0],    [1,0.5,0],   [1,-0.25,0.25*math.sqrt(3)],    [1,-0.25,-0.25*math.sqrt(3)]],    dtype='f')
    pyramideIndices = np.array([[0,1,   0,2,    0,3,    1,2,    2,3,    3,1]], dtype=np.int32)
    piramideIndices = np.array([[0,1,2,   0,2,3,    0,3,1,    1,2,3]], dtype=np.int32)
    
    """ Create the "dashed" VBO & index buffer arrays """
    dashedVertices = np.array([[0,0,0],    [1/6.,0,0],   [2/6.,0,0],    [3/6.,0,0],    [4/6.,0,0],    [5/6.,0,0],    [6/6.,0,0]],    dtype='f')
    dashedIndices = np.array([[0,1,   2,3,    4,5]], dtype=np.int32)
    
    """ Create the "hexagon" VBO & index buffer arrays """
    hexagonVertices = np.array([[-0.5,-0.5,0],    [-0.5,-0.25,0.25*math.sqrt(3)],   [-0.5,0.25,0.25*math.sqrt(3)],    [-0.5,0.5,0],    [-0.5,0.25,-0.25*math.sqrt(3)],   [-0.5,-0.25,-0.25*math.sqrt(3)],    \
                                [0.5,-0.5,0],     [0.5,-0.25,0.25*math.sqrt(3)],    [0.5,0.25,0.25*math.sqrt(3)],     [0.5,0.5,0],     [0.5,0.25,-0.25*math.sqrt(3)],    [0.5,-0.25,-0.25*math.sqrt(3)]],    dtype='f')
    hexagonIndices = np.array([[0,1,   1,2,    2,3,    3,4,    4,5,    5,0,    \
                                6,7,   7,8,    8,9,    9,10,   10,11,  11,6,   \
                                0,6,   1,7,    2,8,    3,9,    4,10,   5,11]], dtype=np.int32)
    hexakonIndices = np.array([[0,1,2,3,   3,4,5,0,    \
                                6,7,8,9,   9,10,11,6,  \
                                0,6,7,1,   1,7,8,2,   2,8,9,3,   3,9,10,4,   4,10,11,5,   5,11,6,0]], dtype=np.int32)

    """ Create the VBO & index buffer objects """
    vertexPositions = [vbo.VBO(cubeVertices), vbo.VBO(pyramideVertices), vbo.VBO(dashedVertices), vbo.VBO(hexagonVertices)]
    indexPositions = [[vbo.VBO(cubeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(kubeIndices, target=GL_ELEMENT_ARRAY_BUFFER)],
                      [vbo.VBO(pyramideIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(piramideIndices, target=GL_ELEMENT_ARRAY_BUFFER)],
                      vbo.VBO(dashedIndices, target=GL_ELEMENT_ARRAY_BUFFER),
                      [vbo.VBO(hexagonIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(hexakonIndices, target=GL_ELEMENT_ARRAY_BUFFER)]]

opaque = 0
blending = 1
wireframe = 2
idBuffer = 3
def modelView(style = 0):
    if style == 0 or style == 3:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
    elif style == 1:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
    elif style == 2:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)


def bindTexture(textureData, width, height):
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def loadTexture(texture = 'Textures/awesomeface.png'):
    textureSurface = pygame.image.load(texture)
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texid)

    return [textureData, width, height]

    

def displayGround(rMax = 5):
    Definitions.transform.push()
    Definitions.transform.rotate(90, 0, 0, 1)
    Definitions.transform.translate(-1.1, 0, 0)
    Definitions.transform.scale(1,3,3)
    
    
    
    """ send color to shader """
    glUniform4fv(Shaders.setColor_loc, 1, np.array([0.5,0.,1,0.05], dtype = np.float32))

    """ bind hexagon surfaces vbo """
    indexPositions[vboHexagon][vboSurfaces].bind()
    vertexPositions[vboHexagon].bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
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
                """ send transformation matrix to shader """
                glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, Definitions.transform.peek())

                """ draw vbo """
                glDrawElements(GL_QUADS, 40, GL_UNSIGNED_INT, None)
                Definitions.transform.pop()
            j += 1
        i += 1
    
    
    """ send color to shader """
    glUniform4fv(Shaders.setColor_loc, 1, np.array([0.5,0.,1.,0.2], dtype = np.float32))

    """ bind hexagon edges vbo """
    indexPositions[vboHexagon][vboEdges].bind()
    vertexPositions[vboHexagon].bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
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
                """ send transformation matrix to shader """
                glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, Definitions.transform.peek())

                """ draw vbo """
                glDrawElements(GL_LINES, 36, GL_UNSIGNED_INT, None)
                Definitions.transform.pop()
            j += 1
        i += 1
    Definitions.transform.pop()