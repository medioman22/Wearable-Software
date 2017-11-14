import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

from OpenGL.arrays import vbo
from OpenGL.raw.GL.ARB.vertex_array_object import glGenVertexArrays, \
                                                  glBindVertexArray
from ctypes import *
import numpy as np

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

import math
import time
import random

import Cursor
import Definitions
import Events
import Graphics
import Ground
import GUI
import Muscles
import Saturations
import Sensors
import Shaders
import State
import StickMan





def refreshId():
    id = 0
    for i in range(0, len(Sensors.virtuSens)):
        Sensors.virtuSens[i].id = id
        id += 1
    for i in range(0, len(Sensors.zoiSens)):
        Sensors.zoiSens[i].id = id
        id += 1
        #TODO : do it with body & GUI as well, change ID buffer also ?

def main():
    v1 = Definitions.vector4D((0, 1, 0, 0))
    v2 = Definitions.vector4D((0, 0, 1, 0))
    v = Definitions.vector4D.AngleAxisBetween2Vec(v1,v2)
    v.values()
    """ Create list of models """
    State.createList()
    State.updateTemplateList()
    """ Create Entities """
    StickMan.virtuMan = StickMan.characteristics(1.7, (0,0,0), StickMan.parts)
    State.loadModel(StickMan.virtuMan)
    Saturations.preprocessSaturations(StickMan.virtuMan)
    """Sensors.virtuSens = [Sensors.sensors("Head", "Eye", (0.,160,90), (1,0,0.5)),
                         Sensors.sensors("Head", "Eye", (0.,200,90), (1,0,0.5))]
    # EEG ZOI
    color = (0.5, 0.5, 0.)
    Sensors.virtuSens = Sensors.virtuSens + [

                         ##### 10/20 System Position

                         Sensors.sensors("Head", "EEG", (0.,0,0), color),               #Cz
                         
                         Sensors.sensors("Head", "EEG", (0.,0,36), color),              #Pz
                         Sensors.sensors("Head", "EEG", (0.,-90,36), color),            #C3
                         Sensors.sensors("Head", "EEG", (0.,90,36), color),             #C4
                         Sensors.sensors("Head", "EEG", (0.,180,36), color),            #Fz
                         
                         Sensors.sensors("Head", "EEG", (0.,0,72), color),              #Oz
                         Sensors.sensors("Head", "EEG", (0.,-90,72), color),            #T3
                         Sensors.sensors("Head", "EEG", (0.,90,72), color),             #T4
                         Sensors.sensors("Head", "EEG", (0.,180,72), color),            #Fpz
                         
                         Sensors.sensors("Head", "EEG", (0.,-18,72), color),            #O1
                         Sensors.sensors("Head", "EEG", (0.,18,72), color),             #O2
                         Sensors.sensors("Head", "EEG", (0.,-(180-18),72), color),      #Fp1
                         Sensors.sensors("Head", "EEG", (0.,180-18,72), color),         #Fp2

                         Sensors.sensors("Head", "EEG", (0.,-54,72), color),            #T5
                         Sensors.sensors("Head", "EEG", (0.,54,72), color),             #T6
                         Sensors.sensors("Head", "EEG", (0.,-(180-54),72), color),      #F7
                         Sensors.sensors("Head", "EEG", (0.,180-54,72), color),         #F8
                         
                         Sensors.sensors("Head", "EEG", (0.,-33.86,51), color),         #P3
                         Sensors.sensors("Head", "EEG", (0.,33.86,51), color),          #P4
                         Sensors.sensors("Head", "EEG", (0.,-(180-33.86),51), color),   #F3
                         Sensors.sensors("Head", "EEG", (0.,180-33.86,51), color),      #F4
                         
                         
                         ##### 10/10 System Position
                         
                         Sensors.sensors("Head", "EEG", (0.,0,18), color),              #CPz
                         Sensors.sensors("Head", "EEG", (0.,-90,18), color),            #C1
                         Sensors.sensors("Head", "EEG", (0.,90,18), color),             #C2
                         Sensors.sensors("Head", "EEG", (0.,180,18), color),            #FCz

                         Sensors.sensors("Head", "EEG", (0.,0,54), color),              #POz
                         Sensors.sensors("Head", "EEG", (0.,-90,54), color),            #C5
                         Sensors.sensors("Head", "EEG", (0.,90,54), color),             #C6
                         Sensors.sensors("Head", "EEG", (0.,180,54), color),            #AFz
                         
                         Sensors.sensors("Head", "EEG", (0.,-36,72), color),            #PO7
                         Sensors.sensors("Head", "EEG", (0.,36,72), color),             #PO8
                         Sensors.sensors("Head", "EEG", (0.,-(180-36),72), color),      #AF7
                         Sensors.sensors("Head", "EEG", (0.,180-36,72), color),         #AF8
                         
                         Sensors.sensors("Head", "EEG", (0.,-72,72), color),            #TP7
                         Sensors.sensors("Head", "EEG", (0.,72,72), color),             #TP8
                         Sensors.sensors("Head", "EEG", (0.,-(180-72),72), color),      #FT7
                         Sensors.sensors("Head", "EEG", (0.,180-72,72), color),         #FT8
                         
                         Sensors.sensors("Head", "EEG", (0.,-25.13,61.27), color),          #PO3
                         Sensors.sensors("Head", "EEG", (0.,25.13,61.27), color),           #PO4
                         Sensors.sensors("Head", "EEG", (0.,-(180-25.13),61.27), color),    #AF3
                         Sensors.sensors("Head", "EEG", (0.,180-25.13,61.27), color),       #AF4
                         
                         Sensors.sensors("Head", "EEG", (0.,-19.35,42.26), color),          #P1
                         Sensors.sensors("Head", "EEG", (0.,19.35,42.26), color),           #P2
                         Sensors.sensors("Head", "EEG", (0.,-(180-19.35),42.26), color),    #F1
                         Sensors.sensors("Head", "EEG", (0.,180-19.35,42.26), color),       #F2
                         
                         Sensors.sensors("Head", "EEG", (0.,-44.95,61.13), color),          #P5
                         Sensors.sensors("Head", "EEG", (0.,44.95,61.13), color),           #P6
                         Sensors.sensors("Head", "EEG", (0.,-(180-44.95),61.13), color),    #F5
                         Sensors.sensors("Head", "EEG", (0.,180-44.95,61.13), color),       #F6
                         
                         Sensors.sensors("Head", "EEG", (0.,-56.31,40.78), color),          #CP3
                         Sensors.sensors("Head", "EEG", (0.,56.31,40.78), color),           #CP4
                         Sensors.sensors("Head", "EEG", (0.,-(180-56.31),40.78), color),    #FC3
                         Sensors.sensors("Head", "EEG", (0.,180-56.31,40.78), color),       #FC4
                         
                         Sensors.sensors("Head", "EEG", (0.,-38.99,26.82), color),          #CP1
                         Sensors.sensors("Head", "EEG", (0.,38.99,26.82), color),           #CP2
                         Sensors.sensors("Head", "EEG", (0.,-(180-38.99),26.82), color),    #FC1
                         Sensors.sensors("Head", "EEG", (0.,180-38.99,26.82), color),       #FC2
                         
                         Sensors.sensors("Head", "EEG", (0.,-65.62,56.15), color),          #CP5
                         Sensors.sensors("Head", "EEG", (0.,65.62,56.15), color),           #CP6
                         Sensors.sensors("Head", "EEG", (0.,-(180-65.62),56.15), color),    #FC5
                         Sensors.sensors("Head", "EEG", (0.,180-65.62,56.15), color),       #FC6

                         # all spher 90
                         Sensors.sensors("Head", "EEG", (0.,0,90), color),              #Iz
                         Sensors.sensors("Head", "EEG", (0.,-90,90), color),            #T9
                         Sensors.sensors("Head", "EEG", (0.,90,90), color),             #T10
                         Sensors.sensors("Head", "EEG", (0.,180,90), color),            #Nzn

                         Sensors.sensors("Head", "EEG", (0.,-54,90), color),            #P9
                         Sensors.sensors("Head", "EEG", (0.,54,90), color),             #P10
                         Sensors.sensors("Head", "EEG", (0.,-(180-54),90), color),      #F9
                         Sensors.sensors("Head", "EEG", (0.,180-54,90), color),         #F10
                         
                         Sensors.sensors("Head", "EEG", (0.,-72,90), color),            #TP9
                         Sensors.sensors("Head", "EEG", (0.,72,90), color),             #TP10
                         Sensors.sensors("Head", "EEG", (0.,-(180-72),90), color),      #FT9
                         Sensors.sensors("Head", "EEG", (0.,180-72,90), color),         #FT10
                         ]"""
    
    State.loadGroups()

    """ Create a window """
    pygame.init()
    State.importUserSettings()
    GUI.resize()
    GUI.screen = pygame.display.set_mode(GUI.display, pygame.DOUBLEBUF|pygame.OPENGL|pygame.OPENGLBLIT|RESIZABLE|NOFRAME)
    glClearColor(0.0, 0.0, 0.0, 0.0);
    
    """ texture for ID buffer """
    # create texture
    plane_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, plane_texture)
    # texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, GUI.display[0], GUI.display[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glBindTexture(GL_TEXTURE_2D, 0)


    """ render buffer for depth for ID buffer """
    # create render buffer
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, GUI.display[0], GUI.display[1])
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    

    """ frame buffer object as ID buffer """
    # create frame buffer
    FBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, FBO)
    # attach texture to frame buffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, plane_texture, 0)
    # attach render buffer to frame buffer
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    """ Generate the VBOs """
    Graphics.VBO_init()
    

    """ Create the shaders """
    Shaders.shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(Shaders.vertex_shader,GL_VERTEX_SHADER),
                                                      OpenGL.GL.shaders.compileShader(Shaders.fragment_shader,GL_FRAGMENT_SHADER))
    glUseProgram(Shaders.shader)


    """ Enable position attrib ? """
    position = glGetAttribLocation(Shaders.shader, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None) 
    glEnableVertexAttribArray(position)


    """ Initialize some more stuff"""
    GUI.TEX_TEXTURE = glGenTextures(1)
    glEnable(GL_TEXTURE_2D)
    glDepthFunc(GL_LEQUAL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    

    """ Shader var. locations """
    Shaders.proj_loc = glGetUniformLocation(Shaders.shader, "projection")
    Shaders.view_loc = glGetUniformLocation(Shaders.shader, "view")
    Shaders.model_loc = glGetUniformLocation(Shaders.shader, "model")
    Shaders.setColor_loc = glGetUniformLocation(Shaders.shader, "setColor")
    
    Definitions.projectionMatrix.perspectiveProjection(90, 0.5*GUI.display[0]/GUI.display[1], 0.1, 100.0)
    glUniformMatrix4fv(Shaders.proj_loc, 1, GL_FALSE, Definitions.projectionMatrix.peek())
    glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())


    """ >>> main loop <<< """
    while True:
        # keep track of loop frequency
        flagStart = time.clock()

        
        """
            Update ZOI & template lists.
            you can edit / add / remove ZOI & template files without closing software (as long as syntax is respected)
        """
        State.updateTemplateList()
        sensorTypes = []
        for sensorType in Sensors.sensorGraphics:
            sensorTypes = sensorTypes + [sensorType[0]]


        """
            Events management.
            Most interactions between the user and the software is aknowledged here.
        """
        Events.manage()
        
        refreshId() # TODO : only when adding/removing sensors
        


        """
            Preprocess entities.
            Store all needed transformations to significantly lower calculation cost when rendering (redundancy otherwise between display buffer, ID buffer and bindings)
        """
        Definitions.modelMatrix.translate(-StickMan.lookingAt[0][0],-StickMan.lookingAt[0][1],-StickMan.lookingAt[0][2])
        StickMan.part = -1 # initialize the recursivity here
        Sensors.countID = 0
        Graphics.SaturationModelMatrix = []
        StickMan.stick(StickMan.virtuMan, (StickMan.virtuMan.x, StickMan.virtuMan.y, StickMan.virtuMan.z))
        Muscles.preprocessMuscle()
        Ground.preprocessGround(math.fabs(Events.rMax))

        i = 0
        for package in Definitions.packagePreprocess:
            j = 0
            for pack in package:
                if pack[Definitions.packParent] == "Ground":
                    Definitions.packageIndices[0] = Definitions.packageIndices[0] + [[i, j],]
                elif pack[Definitions.packParent] == "Body":
                    Definitions.packageIndices[1] = Definitions.packageIndices[1] + [[i, j],]
                elif pack[Definitions.packParent] == "Sensor":
                    Definitions.packageIndices[2] = Definitions.packageIndices[2] + [[i, j],]
                elif pack[Definitions.packParent] == "Link":
                    Definitions.packageIndices[3] = Definitions.packageIndices[3] + [[i, j],]
                j += 1
            i += 1


        """ 
            Draw on the ID buffer.
            The ID BUFFER is used for the mouse implementation, to know which body/sensor/gui part is targeted with the cursor.
        """
        # bind the ID buffer
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)
        
        # clear the ID buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        list = []
        for file in State.sensorFileName:
            list = list + [file[0]]
        # fill ID buffer

        window = GUI.windowScene
        GUI.subWindow(window,False)

        Graphics.modelView(Graphics.opaque)
        StickMan.drawBodySurface(Graphics.idBuffer)
        Sensors.drawSensor(Graphics.idBuffer)
        Muscles.drawMuscle(Graphics.idBuffer)

        glClear(GL_DEPTH_BUFFER_BIT) # clear depth to ensure gui in front of display
        if GUI.selectedWindow == GUI.windowTemplatesId:
            window = GUI.windowTemplates
            GUI.subWindow(window,False)
            GUI.textTexture(sensorTypes, -0.95, 0.95-4*0.03*window.ty, 1, 1, True, window, 0)
        if GUI.selectedWindow == GUI.windowGroupsId:
            window = GUI.windowGroups
            GUI.subWindow(window,False)
            GUI.textTexture(list, -0.95, 0.95-6*0.03*window.ty, 1, 1, True, window, len(sensorTypes))
        window = GUI.windowPannel
        GUI.subWindow(window,False)
        GUI.textTexture(GUI.windowList, -0.95, 0, 1, 0, True, window, len(sensorTypes) + len(list))


        """
            Mouse interaction with ID buffer.
            Read the value of the ID buffer at mouse position, do some stuff.
        """
        Cursor.mouseManage()
        


        """
            Draw on the display buffer.
            The display buffer is what the user will see on his screen.
        """
        # bind the display buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # clear the display buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        window = GUI.windowScene
        GUI.subWindow(window,Events.style != Graphics.idBuffer)

        # draw scene
        Graphics.modelView(Graphics.blending)
        Ground.drawGround()
        
        # draw saturation balls
        Graphics.modelView(Graphics.blending)
        Saturations.drawSaturationBalls()

        # draw body
        Graphics.modelView(Events.style)
        StickMan.drawBodySurface(Events.style)
        StickMan.drawBodyEdge(Events.style)

        # draw muscles
        Graphics.modelView(Events.style)
        Muscles.drawMuscle(Events.style)

        # draw saturation lines
        Graphics.modelView(Graphics.opaque)
        Saturations.drawSaturationLines()

        # draw sensors
        Graphics.modelView(Graphics.opaque)
        Sensors.drawSensor(Events.style)
        Sensors.drawDashed(Events.style)
        

        # draw GUI
        glClear(GL_DEPTH_BUFFER_BIT)
        Graphics.modelView(Graphics.opaque)


        """ display template window """
        if GUI.selectedWindow == GUI.windowTemplatesId:
            window = GUI.windowTemplates
            GUI.subWindow(window,Events.style != Graphics.idBuffer,)
            if Events.style != Graphics.idBuffer:
                GUI.textTexture(['Wearable templates'], 0, 0.95, 0, 1, False, window)
            GUI.textTexture(sensorTypes, -0.95, 0.95-4*0.03*window.ty, 1, 1, Events.style == Graphics.idBuffer, window, 0)
            
            """ display selected template """
            window = GUI.windowSensor
            GUI.subWindow(window,False)
            if Events.style != Graphics.idBuffer and GUI.guiType(GUI.selectedTemplate) == GUI.guiTemplate:
                Sensors.displayTemplate()
                GUI.textTexture(['Color : ' + str(Sensors.sensorGraphics[GUI.selectedTemplate-1][1]),
                                 'Scale : ' + str(Sensors.sensorGraphics[GUI.selectedTemplate-1][3])], 0.95, -0.95, -1, -1, False, window)


        """ display groups window """
        if GUI.selectedWindow == GUI.windowGroupsId:
            window = GUI.windowGroups
            GUI.subWindow(window,Events.style != Graphics.idBuffer)
            if Events.style != Graphics.idBuffer:
                GUI.textTexture(['Wearable groups',
                                 'Save in ~'], 0, 0.95, 0, 1, False, window)
            GUI.textTexture(list, -0.95, 0.95-6*0.03*window.ty, 1, 1, Events.style == Graphics.idBuffer, window, len(sensorTypes))
            

        """ display data window """
        if GUI.selectedWindow == GUI.windowDataId:
            window = GUI.windowData
            GUI.subWindow(window,Events.style != Graphics.idBuffer)
            if Events.style != Graphics.idBuffer:
                GUI.textTexture(['Model : ' + str(State.modelFileName[State.currentModelFile])], 0, 0.95, 0, 1, False, window)
                GUI.textTexture(['ID : ' + str(int(Cursor.ID)) + str(Cursor.name),]
                                + Cursor.info, 0.95, -0.95, -1, -1, False, window)
                GUI.textTexture([str(int(1./(time.clock()-flagStart))) + ' Hz'], 0.95, 0.95, -1, 1, False, window)


        """ display panel window """
        window = GUI.windowPannel
        GUI.subWindow(window,Events.style != Graphics.idBuffer)
        GUI.textTexture(GUI.windowList, -0.95, 0, 1, 0, Events.style == Graphics.idBuffer, window, len(sensorTypes) + len(list))


        """ display help window """
        if GUI.selectedWindow == GUI.windowHelpId:
            if Events.style != Graphics.idBuffer:
                window = GUI.windowHelp
                GUI.subWindow(window,Events.style != Graphics.idBuffer)
                GUI.textTexture(GUI.helpList, -0.95,-0.95, 1, -1, False, window)
        
        

        # update screen
        pygame.display.flip()

        """
            empty preprocess package
        """
        i = len(Definitions.packagePreprocess)
        while i > 0:
            i -= 1
            while len(Definitions.packagePreprocess[i]) > 0:
                Definitions.packagePreprocess[i] = Definitions.packagePreprocess[i][:-1]
        i = len(Definitions.packageIndices)
        while i > 0:
            i -= 1
            while len(Definitions.packageIndices[i]) > 0:
                Definitions.packageIndices[i] = Definitions.packageIndices[i][:-1]


        pygame.time.wait(10)


        


main()