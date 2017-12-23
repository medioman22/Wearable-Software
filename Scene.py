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
    groundPreprocess = []
    
    Definitions.modelMatrix.push()
    Definitions.modelMatrix.rotate(90, 0, 0, 1)
    Definitions.modelMatrix.scale(5,5,5)
    groundPreprocess = groundPreprocess + [Definitions.modelMatrix.peek(),]
    Definitions.modelMatrix.pop()


bubble = None
def drawBubble():
    if Events.style == Graphics.idBuffer:
        return
    if Events.showGround == False:
        return
    

    for pack in groundPreprocess:
        
        """ bind surfaces vbo """
        bubble.mesh.surfIndexPositions.bind()
        bubble.mesh.vertexPositions.bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.05], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack)

        """ draw vbo """
        glDrawElements(bubble.mesh.surfStyleIndex, bubble.mesh.surfNbIndex, GL_UNSIGNED_INT, None)

    for pack in groundPreprocess:
                    
        """ bind surfaces vbo """
        bubble.mesh.edgeIndexPositions.bind()
        bubble.mesh.vertexPositions.bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

        """ choose color """
        color = np.array([0.5,0.,1,0.2], dtype = np.float32)

        """ send color to shader """
        glUniform4fv(Shaders.setColor_loc, 1, color)

        """ send matrix to shader """
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, pack)

        """ draw vbo """
        glDrawElements(bubble.mesh.edgeStyleIndex, bubble.mesh.edgeNbIndex, GL_UNSIGNED_INT, None)