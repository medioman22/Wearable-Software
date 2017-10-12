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



sensorTypes = [ 'EEG',
                'EMG',
                'ECG',
                'IMU',
                'Strain',
                'Pressure',
                'Marker',
                'Custom']

TEX_TEXTURE = None
"""
    display some text on the screen. each element in the "text" list is a new line.
    x = [0;1], y = [0;1] : text starting position, normalized to window dimensions
    sx = 1|0|-1 : text aligned on left|center|right side
    sy = 1|-1 : new line under|over current line
"""
guiId = 0
selectedGuiId = 0
def textTexture(text, x = 0, y = 0, sx = 1, sy = 1, idDraw = False):
    global guiId
    x = x
    dy = 0.03
    y = y
    glUseProgram(0)

    font = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 128)
    for txt in text:
        guiId += 1
        if idDraw != True:
            if selectedGuiId != guiId:
                textSurface = font.render(txt, True, (255,255,255,255), (0,0,0,0))
            else:
                textSurface = font.render(txt, True, (255,0,0,255), (0,0,0,0))
        else:
            textSurface = font.render(txt, True, (255,255,255,255), (0,0,255*guiId/len(text),0))
        ix, iy = textSurface.get_width(), textSurface.get_height()
        dx = dy*ix/iy
        image = pygame.image.tostring(textSurface, "RGBA", True)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, TEX_TEXTURE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    
        glLoadIdentity()
        glTranslatef(x + sx*dx,y - sy*dy,0.0)
        glScalef(dx,dy,1.)
        glBindTexture(GL_TEXTURE_2D, TEX_TEXTURE)
        glColor4f(0,0,guiId/len(text),0)
        glBegin(GL_QUADS)
        if idDraw != True:
            glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.0,  1.0)
        if idDraw != True:
            glTexCoord2f(1.0, 0.0)
        glVertex3f( 1.0, -1.0,  1.0)
        if idDraw != True:
            glTexCoord2f(1.0, 1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        if idDraw != True:
            glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        glEnd()
        y -= 2*sy*dy
    glUseProgram(Shaders.shader)