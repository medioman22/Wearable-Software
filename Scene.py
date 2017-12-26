#
#   File : Scene.py
#   
#   Code written by : Johann Heches
#
#   Description : Fancy background. Not required for the purpose of this project. Could be uterly changed to add a room for the avatar to move in (or stairs, obstacles, ...).
#   


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import numpy as np

import Definitions
import Events
import Graphics
import Shaders
    

groundPreprocess = []
def preprocessGround():
    global groundPreprocess
    #preprocess only if something changed (empty groundPreprocess)
    if groundPreprocess != []:
        return
    
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.rotate(90, 0, 0, 1)
    Definitions.modelMatrix.translate(-1.1,0,0)
    Definitions.modelMatrix.scale(0.1,2,2)
    a = 5
    for y in range(-a,a+1):
        for z in range(-a,a+1):
            Definitions.modelMatrix.push()
            Definitions.modelMatrix.translate(0,y,z)
            Definitions.modelMatrix.scale(1,0.95,0.95)
            groundPreprocess = groundPreprocess + [Definitions.modelMatrix.peek(),]
            Definitions.modelMatrix.pop()
    Definitions.modelMatrix.pop()


tile = None
def drawScene():
    if Events.style == Graphics.idBuffer:
        return
    if Events.showGround == False:
        return
    
    
    """ bind surfaces vbo """
    tile.mesh.surfIndexPositions.bind()
    tile.mesh.vertexPositions.bind()
    glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
    for pack in groundPreprocess:

        """ choose color """
        color = np.array([0.5,0.,1,0.05], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack)

        """ draw vbo """
        glDrawElements(tile.mesh.surfStyleIndex, tile.mesh.surfNbIndex, GL_UNSIGNED_INT, None)
        

    """ bind edges vbo """
    tile.mesh.edgeIndexPositions.bind()
    tile.mesh.vertexPositions.bind()
    glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None)
    for pack in groundPreprocess:

        """ choose color """
        color = np.array([0.5,0.,1,0.2], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack)

        """ draw vbo """
        glDrawElements(tile.mesh.edgeStyleIndex, tile.mesh.edgeNbIndex, GL_UNSIGNED_INT, None)