#
#   File : Main.py
#   
#   Code written by : Johann Heches
#
#   Description : Main loop, initialisation, main window.
#   


from ctypes import *
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
from OpenGL.arrays import vbo
from OpenGL.raw.GL.ARB.vertex_array_object import glGenVertexArrays, \
                                                  glBindVertexArray
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.uic import *
import sys
import time

import Cursor
import Definitions
import Events
import Graphics
import Scene
import ID
import Limbs
import Muscles
import Saturations
import Sensors
import Shaders
import State
import Avatar
import UI




class mainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args):
        self.initialized = False
        self.displayFBO = 1 # for some reasons PyQt made a new fbo on it's own, so it's 1 and not 0 ?
        self.idFBO = None
        super(mainWindow, self).__init__(*args)
        loadUi('minimal.ui', self)


    def setupUI(self):
        self.setWindowTitle('Wearable Sensors')
        self.setWindowIcon(UI.iconFace)
        self.openGLWidget.initializeGL()
        self.openGLWidget.resizeGL(1500,800)
        self.openGLWidget.paintGL = self.paintGL

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.openGLWidget.update) 
        timer.start(10)

        self.setMouseTracking(True)

    def paintGL(self):

        """
            first call requires initialization
        """
        if self.initialized == False:
            self.initialized = True
            self.initializeGL()
            print("initialization done")



        """  -----------------  """
        """  >>> main loop <<<  """
        """  -----------------  """
        # keep track of loop frequency
        flagStart = time.clock()



        """
            Events management.
            Keyboard interactions between the user and the software are done here.
        """
        Events.manage()
        


        """
            Update all entities ID
        """
        ID.setId([Avatar.virtuMan.limbs, Avatar.virtuMan.muscles, Sensors.virtuSens, Sensors.zoiSens])
        


        """
            Preprocess entities.
            Store all needed transformations to significantly lower calculation cost when rendering (redundancy otherwise between display buffer, ID buffer and bindings)
        """

        # Preprocess of limbs
        Definitions.modelMatrix.push()
        Definitions.modelMatrix.translate(Avatar.virtuMan.position[0],Avatar.virtuMan.position[1],Avatar.virtuMan.position[2])
        R = Definitions.vector4D.Quat2Vec(Definitions.vector4D((Avatar.virtuMan.orientation)))
        Definitions.modelMatrix.rotate(R.o,R.x,R.y,R.z)
        Avatar.limb = -1 # initialize the recursivity here
        Sensors.countID = 0
        Graphics.SaturationModelMatrix = []
        Avatar.stick(Avatar.virtuMan)
        Definitions.modelMatrix.pop()

        Avatar.oneMesh(Avatar.virtuMan)

        Muscles.preprocessMuscle(Avatar.virtuMan)
        
        Scene.preprocessGround()


        """ 
            Draw on the ID buffer.
            The ID BUFFER is used for the mouse implementation, to know which entity is targeted with the cursor.
        """
        # bind the ID buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.idFBO)
        # clear the ID buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # fill ID buffer

        glViewport(0,0,Graphics.display[0],Graphics.display[1])

        Graphics.modelView(Graphics.opaque)
        
        Limbs.drawBodySurface(Avatar.virtuMan, Graphics.idBuffer, Events.SHOW)
        Muscles.drawMuscleSurface(Avatar.virtuMan, Graphics.idBuffer, Events.SHOW)
        Sensors.drawZoi(Graphics.idBuffer)
        Sensors.drawSensor(Graphics.idBuffer)


        """
            Mouse interaction with ID buffer.
            Read the value of the ID buffer at mouse position, do some stuff.
        """
        dx = -8; dy = -30
        Cursor.mouse = [QtGui.QCursor().pos().x()+dx, QtGui.QCursor().pos().y()+dy]
        Cursor.mouseManage()
        


        """
            Draw on the display buffer.
            The display buffer is what the user will see on his screen.
        """
        # bind the display buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.displayFBO)
        
        # clear the display buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glViewport(0,0,Graphics.display[0],Graphics.display[1])
        
        # draw scene
        Graphics.modelView(Graphics.blending)
        Scene.drawScene()

        # draw saturation balls
        Graphics.modelView(Graphics.blending)
        Saturations.drawSaturationBalls(Avatar.virtuMan)
        
        # draw FADE body
        Graphics.modelView(Graphics.blending)
        Limbs.drawBodySurface(Avatar.virtuMan, Events.style, Events.FADE)
        # draw FADE muscles
        Graphics.modelView(Events.style)
        Muscles.drawMuscleSurface(Avatar.virtuMan, Events.style, Events.FADE)
        
        # draw SHOW body
        Graphics.modelView(Events.style)
        Limbs.drawBodySurface(Avatar.virtuMan, Events.style, Events.SHOW)
        Limbs.drawBodyEdge(Avatar.virtuMan, Events.style)
        # draw SHOW muscles
        Graphics.modelView(Events.style)
        Muscles.drawMuscleSurface(Avatar.virtuMan, Events.style, Events.SHOW)
        Muscles.drawMuscleEdge(Avatar.virtuMan, Events.style)
            
        # draw saturation lines
        Graphics.modelView(Graphics.opaque)
        Saturations.drawSaturationLines(Avatar.virtuMan)
        
        # draw sensors
        Graphics.modelView(Graphics.opaque)
        Sensors.drawDashed(Events.style)
        Sensors.drawZoi(Events.style)
        Sensors.drawSensor(Events.style)
        

        #print("FREQ : ", int(1./(time.clock()-flagStart)))

    def initializeGL(self):
        
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
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, Graphics.display[0], Graphics.display[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glBindTexture(GL_TEXTURE_2D, 0)


        """ render buffer for depth for ID buffer """
        # create render buffer
        rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, Graphics.display[0], Graphics.display[1])
        glBindRenderbuffer(GL_RENDERBUFFER, 0)
    

        """ frame buffer object as ID buffer """
        # create frame buffer
        self.idFBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.idFBO)
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
        Shaders.position = glGetAttribLocation(Shaders.shader, "position")
        glVertexAttribPointer(Shaders.position, 3, GL_FLOAT, GL_FALSE, 0, None) 
        glEnableVertexAttribArray(Shaders.position)


        """ Initialize some more stuff"""
        glEnable(GL_TEXTURE_2D)
        glDepthFunc(GL_LEQUAL)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    

        """ Shader var. locations """
        Shaders.proj_loc = glGetUniformLocation(Shaders.shader, "projection")
        Shaders.view_loc = glGetUniformLocation(Shaders.shader, "view")
        Shaders.model_loc = glGetUniformLocation(Shaders.shader, "model")
        Shaders.setColor_loc = glGetUniformLocation(Shaders.shader, "setColor")
    
        Definitions.projectionMatrix.perspectiveProjection(90, Graphics.display[0]/Graphics.display[1], 0.1, 100.0)
        glUniformMatrix4fv(Shaders.proj_loc, 1, GL_FALSE, Definitions.projectionMatrix.peek())
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())

    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            Events.mouse_click = True
        if event.button() == QtCore.Qt.RightButton:
            Events.setLookAt = True

    def keyPressEvent(self, event):
        Events.eventModifierList = Events.eventModifierList + [QtWidgets.QApplication.keyboardModifiers()]
        if event.isAutoRepeat() == False:
            Events.eventKeyList = Events.eventKeyList + [event.key()]
            Events.eventPressList = Events.eventPressList + [True]

    def keyReleaseEvent(self, event):
        Events.eventModifierList = Events.eventModifierList + [QtWidgets.QApplication.keyboardModifiers()]
        if event.isAutoRepeat() == False:
            Events.eventKeyList = Events.eventKeyList + [event.key()]
            Events.eventPressList = Events.eventPressList + [False]

    
if __name__ == '__main__':


    """ Create Entities """
    State.updateAvatar()
    Avatar.virtuMan = Avatar.characteristics(1.7)
    State.loadAvatar(Avatar.virtuMan, State.avatarFileName[0])
    
    Saturations.saturationBall = Saturations.saturation()
    Saturations.saturationBall.mesh = Graphics.VBO_sphere(32,32,32,32)
    Graphics.buildVBO(Saturations.saturationBall)
    Sensors.zoi = Sensors.templates()
    Sensors.zoi.mesh = Graphics.VBO_circle()
    Graphics.buildVBO(Sensors.zoi)
    Sensors.dash = Sensors.templates()
    Sensors.dash.mesh = Graphics.VBO_dashed()
    Graphics.buildVBO(Sensors.dash)

    Scene.tile = Avatar.characteristics(1.7)
    Scene.tile.mesh = Graphics.VBO_cube()
    Graphics.buildVBO(Scene.tile)

    """ window size """
    State.importUserSettings()

    """ Application """
    app = QtWidgets.QApplication(sys.argv)
    
    UI.iconSave  = QtGui.QIcon("Textures/Save.png")
    UI.iconLoad  = QtGui.QIcon("Textures/Load.png")
    UI.iconFace  = QtGui.QIcon("Textures/Face.png")
    UI.iconDelete = QtGui.QIcon("Textures/Delete.png")
    UI.iconRename = QtGui.QIcon("Textures/Rename.png")

    """ UI """
    UI.uiAvatars = UI.uiList(UI.ListAvatars)
    UI.uiPostures = UI.uiList(UI.ListPostures)
    UI.uiTemplates = UI.uiList(UI.ListTemplates)
    UI.uiZoi = UI.uiList(UI.ListZoi)
    UI.uiGroups = UI.uiList(UI.ListGroups)
    UI.uiCustom = UI.uiCustomize()
    UI.uiSensor = UI.uiSensors()

    """ 3D Scene """
    window = mainWindow()
    window.setupUI()
    window.show()


    sys.exit(app.exec_())