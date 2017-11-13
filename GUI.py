class subwindow(object):
    """
        characteristics
        .x      attachment distance
        .t      attachment angle
    """


    def __init__(self, x, y, dx, dy, tx, ty, e, borderColor, backgroundColor): # add orientation sometime...
        """ constructor """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.tx = tx
        self.ty = ty
        self.e = e
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import time
import numpy as np

import Definitions
import Events
import Sensors
import Shaders
import State


helpList = ['Arrows, page up/page dn = camera',
            'right mouse = lock camera on target',
            'Left mouse = (un)select entity',
            'Q,W = twist limb axis x',
            'E,R = swing limb axis y',
            'T,Y = swing limb axis z',
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


display = [1550, 900] # window size
screen = None

border = 0.005*display[1]
windowScene = None
windowTemplates = None
windowGroups = None
windowPannel = None
windowData = None
windowSensor = None
windowHelp = None

def resize():
    global windowScene
    global windowTemplates
    global windowGroups
    global windowPannel
    global windowData
    global windowSensor
    global windowHelp

    windowScene = subwindow(0,0,display[1],display[1],1,1,border,(0.5,0.5,0.5,1),(0,0,0,1))
    windowTemplates = subwindow(display[1],0,int(0.6*display[1]),int(0.95*display[1]),1/0.6,1/0.95,border,(0,1,0,1),(0.25,0.5,0.25,1))
    windowGroups = subwindow(display[1],0,int(0.6*display[1]),int(0.95*display[1]),1/0.6,1/0.95,border,(1,0,0,1),(0.5,0.25,0.25,1))
    windowPannel = subwindow(display[1],int(0.95*display[1]),int(0.6*display[1]),int(0.05*display[1]),1/0.6,1/0.05,border,(0,0,1,1),(0.25,0.25,0.5,1))
    windowData = subwindow(display[1],int(0.35*display[1]),int(0.6*display[1]),int(0.6*display[1]),1/0.6,1/0.6,border,(1,1,0,1),(0.5,0.5,0.25,1))
    windowSensor = subwindow(int(1.2*display[1]),int(0.55*display[1]),int(0.4*display[1]),int(0.4*display[1]),1/0.4,1/0.4,border,(0,1,0,1),(1,1,1,1))
    windowHelp = subwindow(display[1],int(0.35*display[1]),int(0.6*display[1]),int(0.6*display[1]),1.8,1.8,border,(1,1,1,1),(0,0,0,1))

windowHelpId = 1
windowTemplatesId = 2
windowGroupsId = 3
windowDataId = 4
windowList = ['Help', 'Templates', 'Groups', 'Data', '----', 'Quit']

def lenGui():
    return len(Sensors.sensorGraphics) + len(State.sensorFileName) + len(windowList)

guiTemplate = 1
guiGroup = 2
guiWindow = 3
def guiType(guiId):
    if guiId > 0 and\
       guiId <= len(Sensors.sensorGraphics):
        return guiTemplate
    elif guiId > len(Sensors.sensorGraphics) and\
         guiId <= len(Sensors.sensorGraphics) + len(State.sensorFileName):
        return guiGroup
    elif guiId > len(Sensors.sensorGraphics) + len(State.sensorFileName) and\
         guiId <= len(Sensors.sensorGraphics) + len(State.sensorFileName) + len(windowList):
        return guiWindow
    else:
        return 0

def guiOffsetId(guiType):
    if guiType == guiTemplate:
        return 0
    elif guiType == guiGroup:
        return len(Sensors.sensorGraphics)
    elif guiType == guiWindow:
        return len(Sensors.sensorGraphics) + len(State.sensorFileName)

TEX_TEXTURE = None
"""
    display some text on the screen. each element in the "text" list is a new line.
    x = [0;1], y = [0;1] : text starting position, normalized to window dimensions
    sx = 1|0|-1 : text aligned on left|center|right side
    sy = 1|-1 : new line under|over current line
"""

overGuiId = 0
selectedTemplate = 0
selectedGroup = 0
selectedWindow = 0
def textTexture(text, x = 0, y = 0, sx = 1, sy = 1, idDraw = False, window = windowScene, guiId = 9999):
    rx = window.tx
    ry = window.ty
    x = x
    dy = ry*0.03
    y = y

    glUseProgram(0)

    font = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 32)
    for txt in text:
        backgroundColor = (255*window.backgroundColor[0], 255*window.backgroundColor[1], 255*window.backgroundColor[2], 255*window.backgroundColor[3])
        guiId += 1
        if idDraw != True:
            if guiType(guiId) == guiTemplate:
                if Events.rename == Sensors.sensorGraphics[guiId-1][0] + State.extension:
                    backgroundColor = (0, 0, 0, 255)
                if selectedTemplate == guiId:
                    color = Sensors.sensorGraphics[guiId-1][1]
                elif overGuiId == guiId:
                    color = Sensors.sensorGraphics[guiId-1][1]
                    color = (0.5*color[0], 0.5*color[1], 0.5*color[2],255)
                else:
                    color = (255,255,255,255)
            elif guiType(guiId) == guiGroup:
                if Events.rename == State.sensorFileName[guiId-1 - guiOffsetId(guiGroup)][0]:
                    backgroundColor = (0, 0, 0, 255)
                if State.sensorFileName[guiId-1 - guiOffsetId(guiGroup)][1] == True:
                    color = (0, 255, 0, 255)
                elif overGuiId == guiId:
                    color = (0, 127, 0, 255)
                else:
                    color = (255,255,255,255)
            else:
                if selectedWindow + guiOffsetId(guiWindow) == guiId:
                    color = (255, 0, 0, 255)
                elif overGuiId == guiId:
                    color = (127, 0, 0,255)
                else:
                    color = (255,255,255,255)
            textSurface = font.render(txt, True, color, backgroundColor)
        # id buffer
        else:
            textSurface = font.render(txt, True, (255,255,255,255), (0,0,255*guiId/lenGui(),0))

        ix, iy = textSurface.get_width(), textSurface.get_height()
        dx = rx/ry*dy*ix/iy
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
        if sy != 0:
            y -= 2*sy*dy
        else:
            x += 2*sx*(dx + 0.04)
    glUseProgram(Shaders.shader)


def subWindow(window, drawBorder = True):
    x = window.x
    y = window.y
    dx = window.dx
    dy = window.dy
    e = window.e
    borderColor = window.borderColor
    backgroundColor = window.backgroundColor
    if drawBorder == True:
        glViewport(x,y, dx, dy)
        
        glDisable(GL_TEXTURE_2D)
        glUseProgram(0)
        glLoadIdentity()

        glBegin(GL_QUADS)
        glColor4f(borderColor[0], borderColor[1], borderColor[2], borderColor[3])
        glVertex3f(-1,-1, 1)
        glVertex3f(1,-1, 1)
        glVertex3f(1,1, 1)
        glVertex3f(-1,1, 1)
        glEnd()
        
        glViewport(int(x+e),int(y+e), int(dx-2*e), int(dy-2*e))

        glBegin(GL_QUADS)
        glColor4f(backgroundColor[0],backgroundColor[1],backgroundColor[2],backgroundColor[3])
        glVertex3f(-1,-1, 1)
        glVertex3f(1,-1, 1)
        glVertex3f(1,1, 1)
        glVertex3f(-1,1, 1)
        glEnd()

        glUseProgram(Shaders.shader)
        glEnable(GL_TEXTURE_2D)
    else:
        glViewport(int(x+e),int(y+e), int(dx-2*e), int(dy-2*e))

