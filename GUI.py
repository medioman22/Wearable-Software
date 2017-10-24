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

help = ['Help : ']

helpList = ['Arrows, page up/page dn = camera',
            'right mouse = lock camera on target',
            'Left mouse = (un)select entity',
            'Q,W = rotate part around x axis',
            'E,R = rotate part around y axis',
            'T,Y = rotate part around z axis',
            'U   = reset part orientation',
            'I,O = switch selected part',
            'Z,X = translate sensor on x axis',
            'C,V = rotate sensor around cylinder',
            'B,N = rotate sensor around sphere',
            'M   = reset sensor orientation',
            'P   = switch view mode',
            'H,L = save/load model',
            'J,K = switch model',
            'A,F = save/load sensor group',
            'S,D = switch sensor group',
            'G   = change floor']

def lenGui():
    return len(sensorTypes) + len(help)

TEX_TEXTURE = None
"""
    display some text on the screen. each element in the "text" list is a new line.
    x = [0;1], y = [0;1] : text starting position, normalized to window dimensions
    sx = 1|0|-1 : text aligned on left|center|right side
    sy = 1|-1 : new line under|over current line
"""
guiId = 0
overGuiId = 0
selectedGuiId = 0
newGuiPosDir = [0,0,1,1]
def textTexture(text, x = 0, y = 0, sx = 1, sy = 1, idDraw = False):
    global guiId
    global newGuiPosDir
    x = x
    dy = 0.03
    y = y
    glUseProgram(0)

    font = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 32)
    for txt in text:
        guiId += 1
        if idDraw != True:
            if selectedGuiId == guiId:
                textSurface = font.render(txt, True, (255,0,0,255), (0,0,0,0))
            elif overGuiId == guiId:
                textSurface = font.render(txt, True, (127,0,0,255), (0,0,0,0))
            else:
                textSurface = font.render(txt, True, (255,255,255,255), (0,0,0,0))
        else:
            textSurface = font.render(txt, True, (255,255,255,255), (0,0,255*guiId/lenGui(),0))
        ix, iy = textSurface.get_width(), textSurface.get_height()
        dx = dy*ix/iy
        if txt == help[0]:
            if guiId == selectedGuiId:
                newGuiPosDir[0] = x + 2*sx*dx
                newGuiPosDir[1] = y
                newGuiPosDir[2] = sx
                newGuiPosDir[3] = sy
            else:
                newGuiPosDir[0] = -100
                newGuiPosDir[1] = -100
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
        glColor4f(0,0,guiId/lenGui(),0)
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