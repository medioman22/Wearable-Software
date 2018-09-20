#
#   File : Graphics.py
#   
#   Code written by : Johann Heches
#
#   Description : Manage meshes generation.
#   


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

display = [800, 800] # window size

class mesh(object):
    """
        mesh
    """

    def __init__(self): # add orientation sometime...
        """ constructor """
        self.defaultVertices = None
        self.vertices = None
        self.surfIndices = None
        self.edgeIndices = None

        self.vertexPositions = None
        self.surfIndexPositions = None
        self.edgeIndexPositions = None

        self.surfNbIndex = None
        self.edgeNbIndex = None

        self.surfStyleIndex = None
        self.edgeStyleIndex = None

        self.surfIndexOffset = None
        self.edgeIndexOffset = None

    
    def twistVBO(self, angleTwist = 0):
        vertices = self.defaultVertices.copy()
        for i in range(0,vertices.size):
            if i%3 == 0:
                angle = (vertices[0,i]+0.5)*math.pi/180*angleTwist
                newY = vertices[0,i+1]*math.cos(angle) - vertices[0,i+2]*math.sin(angle)
                newZ = vertices[0,i+1]*math.sin(angle) + vertices[0,i+2]*math.cos(angle)
                vertices[0,i+1] = newY
                vertices[0,i+2] = newZ
        self.vertices = vertices

    #to be removed, purely cosmetic...
    def oscilateVBO(self):
        vertices = self.defaultVertices.copy()
        for i in range(0,vertices.size):
            if i%3 == 0 and not (vertices[0,i] == 0 and vertices[0,i+1] == 0 and vertices[0,i+2] == 0):
                angle = math.atan2(vertices[0,i+2],vertices[0,i+1])
                angle2 = math.atan2(vertices[0,i], math.sqrt(vertices[0,i+1]*vertices[0,i+1]+vertices[0,i+2]*vertices[0,i+2]))
                radius = math.sqrt(vertices[0,i]*vertices[0,i]+vertices[0,i+1]*vertices[0,i+1]+vertices[0,i+2]*vertices[0,i+2]) + 0.05*math.sin(10*angle + 0.3*time.clock()) + 0.02*math.sin(50*angle - 1*time.clock())
                newX = radius*math.sin(angle2)
                newY = radius*math.cos(angle)*math.cos(angle2)
                newZ = radius*math.sin(angle)*math.cos(angle2)
                vertices[0,i+1] = newY
                vertices[0,i+2] = newZ
        self.vertices = vertices



vboEdges = 0
vboSurfaces = 1
def VBO_cube():
    """ Create the "cube" VBO & EBO """
    vertices = [-0.5,-0.5,-0.5] + [0.5,-0.5,-0.5] + [0.5,0.5,-0.5] + [-0.5,0.5,-0.5] + [-0.5,-0.5,0.5] + [0.5,-0.5,0.5] + [0.5,0.5,0.5] + [-0.5,0.5,0.5]
    edgeIndices = [0,1, 1,2, 2,3, 3,0, 0,4, 1,5, 2,6, 3,7, 4,5, 5,6, 6,7, 7,4]
    surfIndices = [0,1,2, 2,3,0, 0,4,5, 5,1,0, 1,5,6, 6,2,1, 2,6,7, 7,3,2, 3,7,4, 4,0,3, 7,6,5, 5,4,7]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_pyramide():
    """ Create the "pyramide" VBO & EBO """
    vertices = [-0.5,0,0] + [0.5,0,0.5] + [0.5,0.25*math.sqrt(3),-0.25] + [0.5,-0.25*math.sqrt(3),-0.25]
    edgeIndices = [0,1, 0,2, 0,3, 1,2, 2,3, 3,1]
    surfIndices = [0,1,2, 0,2,3, 0,3,1, 1,2,3]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_cone(iMax = 8):
    """ Create the "pyramide" VBO & EBO """
    vertices = []
    edgeIndices = []
    surfIndices = []

    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        vertices = vertices + [-0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            edgeIndices = edgeIndices + [i, (iMax+1)]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1
    vertices = vertices + [0.5, 0., 0.]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_dashed():
    """ Create the "dashed" VBO & EBO """
    vertices = [-5/10.,0,0] + [-3/10.,0,0] + [-1/10.,0,0] + [1/10.,0,0] + [3/10.,0,0] + [5/10.,0,0]
    edgeIndices = [0,1, 2,3, 4,5]
    surfIndices = [0,1, 2,3, 4,5]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_LINES, GL_LINES)
    
def VBO_circle(iMax = 8):
    """ Create the "sphere" VBO & EBO """
    vertices = []
    edgeIndices = []
    surfIndices = []
    
    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        vertices = vertices + [-0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1
    vertices = vertices + [-0.5, 0., 0.]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_cylinder(iMax = 16, jMax = 8):
    """ Create the "sphere" VBO & EBO """
    vertices = []
    edgeIndices = []
    surfIndices = []
    
    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        
        for j in range(0,jMax):
            vertices = vertices + [-0.5 + (j)/float(jMax-1), 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [jMax*i,            jMax*(i+1)]
            edgeIndices = edgeIndices + [jMax*i + jMax-1,   jMax*(i+1) + jMax-1]
            for j in range(1,jMax):
                edgeIndices = edgeIndices + [jMax*i+j-1,       jMax*i+j]

                surfIndices = surfIndices + [jMax*i+j-1,       jMax*(i+1)+j-1,    jMax*(i+1)+j]
                surfIndices = surfIndices + [jMax*(i+1)+j, jMax*i+j,      jMax*i+j-1]
            surfIndices = surfIndices + [jMax*i,       jMax*(i+1),    jMax*(iMax+1)]
            surfIndices = surfIndices + [jMax*i+jMax-1,     jMax*(i+1)+jMax-1,  jMax*(iMax+1)+1]
        i +=1
    vertices = vertices + [-0.5, 0., 0.]
    vertices = vertices + [0.5, 0., 0.]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_sphere(iMax = 16, jMax = 16, iMin = 16, jMin = 16):
    """ Create the "sphere" VBO & EBO """
    vertices = []
    edgeIndices = []
    surfIndices = []
    
    i = 0
    while i <= iMin:
        phi = math.pi*i/float(iMax)
        j = 0
        while j < jMin:
            theta = 2*math.pi*j/float(jMax)
            vertices = vertices + [0.5*math.cos(phi), 0.5*math.sin(phi)*math.cos(theta), 0.5*math.sin(phi)*math.sin(theta)]
            if i != iMin:
                edgeIndices = edgeIndices + [i*jMin + j, i*jMin + (j+1)%jMin]
                edgeIndices = edgeIndices + [i*jMin + j, (i+1)*jMin + j]
                surfIndices = surfIndices + [i*jMin + j, i*jMin + (j+1)%jMin, (i+1)*jMin + (j+1)%jMin]
                surfIndices = surfIndices + [(i+1)*jMin + (j+1)%jMin, (i+1)*jMin + j, i*jMin + j]
            j +=1
        i +=1
        
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)

def VBO_hypar(saturation = (0, 0, 0, 0, 0, 0)):
    """ Create the "sphere" VBO & EBO """
    vertices = []
    edgeIndices = []
    surfIndices = []
    
    Cy = 0.5*(saturation[2]+saturation[3])
    Cz = 0.5*(saturation[4]+saturation[5])
    Ey = 0.5*(saturation[2]-saturation[3])
    Ez = 0.5*(saturation[4]-saturation[5])
    
    i = 0
    iMax = 360
    ####### BUG if Ey or Ez > 90
    while i <= iMax:
        swingAngle = math.pi/180.*i
        if Ey != 0 and Ez != 0:
            k = 1./math.sqrt(Ez*Ez*math.cos(swingAngle)*math.cos(swingAngle) + Ey*Ey*math.sin(swingAngle)*math.sin(swingAngle))
            theta = k*Ey*Ez*math.sin(swingAngle)
            phi = k*Ey*Ez*math.cos(swingAngle)
        elif Ey != 0:
            phi = -Ey + 2*Ey*i/360.
            theta = 0
        elif Ez != 0:
            phi = 0
            theta = -Ez + 2*Ez*i/360.
        else:
            phi = 0
            theta = 0
        theta *= math.pi/180.
        phi *= math.pi/180.
        x = 0.5*math.cos(phi)*math.cos(theta)
        y = 0.5*math.cos(phi)*math.sin(theta)
        z = 0.5*math.sin(phi)
        vertices = vertices + [x, y, z]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1

    vertices = vertices + [0., 0., 0.]
    
    return storeVertices(vertices, edgeIndices, surfIndices, GL_TRIANGLES, GL_LINES)


def storeVertices(vertices, edgeIndices, surfIndices, surfStyle, edgeStyle):
    newMesh = mesh()

    vertices = np.array([vertices],    dtype='f')
    newMesh.defaultVertices = vertices
    newMesh.vertices = vertices

    edgeIndices = np.array([edgeIndices], dtype=np.int32)
    newMesh.edgeIndices = edgeIndices

    surfIndices = np.array([surfIndices], dtype=np.int32)
    newMesh.surfIndices = surfIndices

    newMesh.surfNbIndex = surfIndices.size
    newMesh.edgeNbIndex = edgeIndices.size

    newMesh.surfStyleIndex = surfStyle
    newMesh.edgeStyleIndex = edgeStyle

    return newMesh

def buildVBO(entity):
    entity.mesh.vertexPositions = vbo.VBO(entity.mesh.vertices)
    entity.mesh.surfIndexPositions = vbo.VBO(entity.mesh.surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)
    entity.mesh.edgeIndexPositions = vbo.VBO(entity.mesh.edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER)

def VBO_init():
    """ init VBO & EBO buffers """
    VBO_init = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_init)

    EBO_init = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_init)


vboCube = 0
vboPyramide = 1
vboDashed = 2
vboHexagon = 3
vboSphere = 4
vboCylindre = 5
vboCone = 6
vboCircle = 7
def VBO_create(vboID = 0):
    newMesh = None
    if vboID == vboCube:
        newMesh = VBO_cube()
    elif vboID == vboPyramide:
        newMesh = VBO_pyramide()
    elif vboID == vboDashed:
        newMesh = VBO_dashed()
    elif vboID == vboHexagon:
        newMesh = VBO_cylinder(6,2)
    elif vboID == vboSphere:
        newMesh = VBO_sphere(16,16,16,16)
    elif vboID == vboCylindre:
        newMesh = VBO_cylinder(16,2)
    elif vboID == vboCone:
        newMesh = VBO_cone()
    else:
        newMesh = VBO_circle(16)
    return newMesh

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
