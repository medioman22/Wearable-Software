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
nbIndex = []
styleIndex = []

vboCube = 0
vboPyramide = 1
vboDashed = 2
vboHexagon = 3
vboEdges = 0
vboSurfaces = 1
def VBO_cube():
    """ Create the "cube" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,-0.5,-0.5],  [0.5,-0.5,-0.5],    [0.5,0.5,-0.5],     [-0.5,0.5,-0.5],    \
                         [-0.5,-0.5,0.5],   [0.5,-0.5,0.5],     [0.5,0.5,0.5],      [-0.5,0.5,0.5]],    dtype='f')

    edgeIndices = np.array([[0,1,   1,2,    2,3,    3,0,    \
                             0,4,   1,5,    2,6,    3,7,    \
                             4,5,   5,6,    6,7,    7,4,    ]], dtype=np.int32)
    surfIndices = np.array([[0,1,2,3,    \
                             0,4,5,1,    \
                             1,5,6,2,    \
                             2,6,7,3,    \
                             3,7,4,0,    \
                             7,6,5,4,    ]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_QUADS],]

def VBO_pyramide():
    """ Create the "pyramide" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,0,0],    [0.5,0,0.5],   [0.5,0.25*math.sqrt(3),-0.25],    [0.5,-0.25*math.sqrt(3),-0.25]],    dtype='f')

    edgeIndices = np.array([[0,1,   0,2,    0,3,    1,2,    2,3,    3,1]], dtype=np.int32)

    surfIndices = np.array([[0,1,2,   0,2,3,    0,3,1,    1,2,3]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_dashed():
    """ Create the "dashed" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[0,0,0],    [1/6.,0,0],   [2/6.,0,0],    [3/6.,0,0],    [4/6.,0,0],    [5/6.,0,0],    [6/6.,0,0]],    dtype='f')

    edgeIndices = np.array([[0,1,   2,3,    4,5]], dtype=np.int32)

    surfIndices = np.array([[0,1,   2,3,    4,5]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_LINES],]
    
def VBO_hexagon():
    """ Create the "hexagon" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,-0.5,0],    [-0.5,-0.25,0.25*math.sqrt(3)],   [-0.5,0.25,0.25*math.sqrt(3)],    [-0.5,0.5,0],    [-0.5,0.25,-0.25*math.sqrt(3)],   [-0.5,-0.25,-0.25*math.sqrt(3)],    \
                         [0.5,-0.5,0],     [0.5,-0.25,0.25*math.sqrt(3)],    [0.5,0.25,0.25*math.sqrt(3)],     [0.5,0.5,0],     [0.5,0.25,-0.25*math.sqrt(3)],    [0.5,-0.25,-0.25*math.sqrt(3)]],    dtype='f')

    edgeIndices = np.array([[0,1,   1,2,    2,3,    3,4,    4,5,    5,0,    \
                             6,7,   7,8,    8,9,    9,10,   10,11,  11,6,   \
                             0,6,   1,7,    2,8,    3,9,    4,10,   5,11]], dtype=np.int32)

    surfIndices = np.array([[0,1,2,3,   3,4,5,0,    \
                             6,7,8,9,   9,10,11,6,  \
                             0,6,7,1,   1,7,8,2,   2,8,9,3,   3,9,10,4,   4,10,11,5,   5,11,6,0]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_QUADS],]

def VBO_init():
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    """ init VBO & EBO buffers """
    VBO_init = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_init)

    EBO_init = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_init)

    """ Create VBOs"""
    n = -1
    n+=1 ; VBO_cube()
    n+=1 ; VBO_pyramide()
    n+=1 ; VBO_dashed()
    n+=1 ; VBO_hexagon()

    while n > 0:
        n -= 1
        Definitions.packagePreprocess = Definitions.packagePreprocess + [[]]
        Definitions.packageIndices = Definitions.packageIndices + [[]] # change to number of entity types instead, bad atm

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

                Definitions.packagePreprocess[vboHexagon] = Definitions.packagePreprocess[vboHexagon] + [[Definitions.transform.peek(), "Ground"],]

                Definitions.transform.pop()
            j += 1
        i += 1
    Definitions.transform.pop()

def drawGround():
    vboId = -1
    for indices in Definitions.packageIndices[0]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]

        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            indexPositions[vboId][vboSurfaces].bind()
            vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.05], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])

        """ draw vbo """
        glDrawElements(styleIndex[vboId][vboSurfaces], nbIndex[vboId][vboSurfaces], GL_UNSIGNED_INT, None)

    vboId = -1
    for indices in Definitions.packageIndices[0]:
        pack = Definitions.packagePreprocess[indices[0]][indices[1]]

        if vboId != indices[0]:
            """ choose vbo """
            vboId = indices[0]
                    
            """ bind surfaces vbo """
            indexPositions[vboId][vboEdges].bind()
            vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.2], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.transform_loc, 1, GL_FALSE, pack[Definitions.packTransform])

        """ draw vbo """
        glDrawElements(styleIndex[vboId][vboEdges], nbIndex[vboId][vboEdges], GL_UNSIGNED_INT, None)