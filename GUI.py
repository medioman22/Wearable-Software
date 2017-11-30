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

class textTex(object):
    """
        texTex
    """


    def __init__(self, text = ""):
        """ constructor """
        self.id = 0
        self.text = text


import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import numpy as np

import Cursor
import Events
import ID
import Sensors
import Shaders
import State




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
    windowSensor = subwindow(int(1.2*display[1]),int(0.55*display[1]),int(0.4*display[1]),int(0.4*display[1]),1/0.4,1/0.4,border,(0,1,0,1),(0.25,0.5,0.25,1))
    windowHelp = subwindow(display[1],int(0.35*display[1]),int(0.6*display[1]),int(0.6*display[1]),1.8,1.8,border,(1,1,1,1),(0,0,0,1))

windowHelpId = 1
windowTemplatesId = 2
windowGroupsId = 3
windowDataId = 4
quitButton = 6

"""
    ALL GUI TEXTS HERE
"""

guiPannel = [textTex('Help'), textTex('Templates'), textTex('Groups'), textTex('Data'), textTex('----'), textTex('Quit')]
guiPostures = []
guiSensorTypes = []
guiSensorZoi = []
guiSensorGroups = []
guiTitleTemplates = [textTex('Wearable templates')]
guiTitleGroups = [textTex('Wearable groups'), textTex('Save in ~')]
guiFrequence = [textTex()]
guiAvatar = [textTex()]
guiCursorInfo = []
guiHelp = [ textTex('Arrows, page up/page dn = camera'),
            textTex('right mouse = lock camera on target'),
            textTex('Left mouse = (un)select entity'),
            textTex('Q,W = twist limb axis x'),
            textTex('E,R = swing limb axis y'),
            textTex('T,Y = swing limb axis z'),
            textTex('U   = reset part orientation'),
            textTex('I,O = switch selected part'),
            textTex('Z,X = translate sensor on x axis'),
            textTex('C,V = rotate sensor around cylinder'),
            textTex('B,N = rotate sensor around sphere'),
            textTex('M   = reset sensor orientation'),
            textTex('P   = switch view mode'),
            textTex('H,L = save/load model'),
            textTex('J,K = switch model'),
            textTex('A,F = save/load sensor group'),
            textTex('S,D = switch sensor group'),
            textTex('G   = change floor')]
def updateGuiLists():
    global guiPostures
    global guiSensorTypes
    global guiSensorZoi
    global guiSensorGroups
    global guiCursorInfo

    guiPostures = []
    for file in State.postureFileName:
        guiPostures = guiPostures + [textTex()]
        guiPostures[len(guiPostures)-1].text = file

    guiSensorTypes = []
    for sensorType in Sensors.sensorGraphics:
        guiSensorTypes = guiSensorTypes + [textTex()]
        guiSensorTypes[len(guiSensorTypes)-1].text = sensorType.type

    guiSensorZoi = []
    for file in State.zoiFileName:
        guiSensorZoi = guiSensorZoi + [textTex()]
        guiSensorZoi[len(guiSensorZoi)-1].text = file

    guiSensorGroups = []
    for file in State.sensorFileName:
        guiSensorGroups = guiSensorGroups + [textTex()]
        guiSensorGroups[len(guiSensorGroups)-1].text = file[0]

    guiCursorInfo = []
    for info in ['ID : ' + str(Cursor.overID) + str(Cursor.name)] + Cursor.info:
        guiCursorInfo = guiCursorInfo + [textTex()]
        guiCursorInfo[len(guiCursorInfo)-1].text = info


TEX_TEXTURE = None
"""
    display some text on the screen. each element in the "text" list is a new line.
    x = [0;1], y = [0;1] : text starting position, normalized to window dimensions
    sx = 1|0|-1 : text aligned on left|center|right side
    sy = 1|-1 : new line under|over current line
"""

overGuiId = 0
selectedTemplate = ""
selectedZoi = ""
selectedGroup = 0
selectedPosture = 1
selectedWindow = 0
def textTexture(text, x = 0, y = 0, sx = 1, sy = 1, idDraw = False, window = windowScene):
    rx = window.tx
    ry = window.ty
    x = x
    dy = ry*0.03
    y = y

    glUseProgram(0)

    font = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 32)
    for txt in text:
        backgroundColor = (255*window.backgroundColor[0], 255*window.backgroundColor[1], 255*window.backgroundColor[2], 255*window.backgroundColor[3])
        if idDraw != True:
            if txt.id == 0:
                color = (255,255,255,255)
            elif ID.idCategory(txt.id) == ID.TEMPLATE:
                if Events.rename == Sensors.sensorGraphics[txt.id-1 - ID.offsetId(ID.TEMPLATE)].type:
                    backgroundColor = (0, 0, 0, 255)
                if selectedTemplate == txt.text:
                    color = Sensors.sensorGraphics[txt.id-1 - ID.offsetId(ID.TEMPLATE)].color
                elif overGuiId == txt.id:
                    color = Sensors.sensorGraphics[txt.id-1 - ID.offsetId(ID.TEMPLATE)].color
                    color = (0.5*color[0], 0.5*color[1], 0.5*color[2],255)
                else:
                    color = (255,255,255,255)
            elif ID.idCategory(txt.id) == ID.ZOILIST:
                #if Events.rename == Sensors.sensorGraphics[txt.id-1 - ID.offsetId(ID.ZOILIST)].type:
                #    backgroundColor = (0, 0, 0, 255)
                if selectedZoi == txt.text:
                    color = (255, 0, 0, 255)
                elif overGuiId == txt.id:
                    color = (127, 0, 0, 255)
                else:
                    color = (255,255,255,255)
            elif ID.idCategory(txt.id) == ID.GROUPE:
                if Events.rename == State.sensorFileName[txt.id-1 - ID.offsetId(ID.GROUPE)][0]:
                    backgroundColor = (0, 0, 0, 255)
                if State.sensorFileName[txt.id-1 - ID.offsetId(ID.GROUPE)][1] == True:
                    color = (0, 255, 0, 255)
                elif overGuiId == txt.id:
                    color = (0, 127, 0, 255)
                else:
                    color = (255,255,255,255)
            elif ID.idCategory(txt.id) == ID.POSTURE:
                if Events.rename == State.postureFileName[txt.id-1 - ID.offsetId(ID.POSTURE)]:
                    backgroundColor = (0, 0, 0, 255)
                if selectedPosture + ID.offsetId(ID.POSTURE) == txt.id:
                    color = (255, 0, 0, 255)
                elif overGuiId == txt.id:
                    color = (127, 0, 0,255)
                else:
                    color = (255,255,255,255)
            elif ID.idCategory(txt.id) == ID.PANNEL:
                if selectedWindow + ID.offsetId(ID.PANNEL) == txt.id:
                    color = (255, 0, 0, 255)
                elif overGuiId == txt.id:
                    color = (127, 0, 0,255)
                else:
                    color = (255,255,255,255)
            if txt.text == '':
                textSurface = font.render('~', True, color, backgroundColor)
            else:
                textSurface = font.render(txt.text, True, color, backgroundColor)
        # id buffer
        else:
            r, g, b = ID.id2color(txt.id)
            if txt.text == '':
                textSurface = font.render('~', True, (255,255,255,255), (r,g,b,0))
            else:
                textSurface = font.render(txt.text, True, (255,255,255,255), (r,g,b,0))

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
        r, g, b = ID.id2color(txt.id)
        glColor4f(r,g,b,0)
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

