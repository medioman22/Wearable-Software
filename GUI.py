import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import time
import numpy as np

import Definitions
import Sensors
import Shaders
import State


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
    return len(Sensors.sensorGraphics) + len(State.sensorFileName) + len(help)

TEX_TEXTURE = None
"""
    display some text on the screen. each element in the "text" list is a new line.
    x = [0;1], y = [0;1] : text starting position, normalized to window dimensions
    sx = 1|0|-1 : text aligned on left|center|right side
    sy = 1|-1 : new line under|over current line
"""

overGuiId = 0
selectedGuiId = 0
newGuiPosDir = [0,0,1,1]
def textTexture(text, x = 0, y = 0, sx = 1, sy = 1, idDraw = False, rx = 1, ry = 1, guiId = 9999):
    global newGuiPosDir
    x = x
    dy = ry*0.03
    y = y
    glUseProgram(0)

    font = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 32)
    for txt in text:
        guiId += 1
        if idDraw != True:
            if guiId-1 < len(Sensors.sensorGraphics):
                color = Sensors.sensorGraphics[guiId-1][1]
            else:
                color = (255, 0, 0, 255)
            if selectedGuiId == guiId:
                textSurface = font.render(txt, True, color, (0,0,0,0))
            elif overGuiId == guiId:
                color = (0.5*color[0], 0.5*color[1], 0.5*color[2],255)
                textSurface = font.render(txt, True, color, (0,0,0,0))
            else:
                textSurface = font.render(txt, True, (255,255,255,255), (0,0,0,0))
        else:
            textSurface = font.render(txt, True, (255,255,255,255), (0,0,255*guiId/lenGui(),0))
        ix, iy = textSurface.get_width(), textSurface.get_height()
        dx = rx/ry*dy*ix/iy
        if txt == help[0]:
            newGuiPosDir[0] = x + 2*sx*dx
            newGuiPosDir[1] = y
            newGuiPosDir[2] = sx
            newGuiPosDir[3] = sy
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


def subWindow(x,y,dx,dy,e, drawBorder = True, color = (0.5,0.5,0.5,1)):
    if drawBorder == True:
        glViewport(x,y, dx, dy)
        
        glDisable(GL_TEXTURE_2D)
        glUseProgram(0)
        glLoadIdentity()
        glBegin(GL_QUADS)
        glColor4f(color[0], color[1], color[2], color[3])
        glVertex3f(-1,-1, 1)
        glVertex3f(1,-1, 1)
        glVertex3f(1,1, 1)
        glVertex3f(-1,1, 1)
        glEnd()
        glUseProgram(Shaders.shader)
        glEnable(GL_TEXTURE_2D)
        
        glViewport(int(x+e),int(y+e), int(dx-2*e), int(dy-2*e))

        glDisable(GL_TEXTURE_2D)
        glUseProgram(0)
        glLoadIdentity()
        glBegin(GL_QUADS)
        glColor4f(0,0,0,1)
        glVertex3f(-1,-1, 1)
        glVertex3f(1,-1, 1)
        glVertex3f(1,1, 1)
        glVertex3f(-1,1, 1)
        glEnd()
        glUseProgram(Shaders.shader)
        glEnable(GL_TEXTURE_2D)
    else:
        glViewport(int(x+e),int(y+e), int(dx-2*e), int(dy-2*e))