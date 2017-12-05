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
import Ground
import GUI
import ID
import Limbs
import Muscles
import Saturations
import Sensors
import Shaders
import State
import StickMan


iconSave  = None
iconLoad  = None
iconFace  = None
iconDelete = None
iconRename = None


class uiCustomize(QtWidgets.QWidget):
    
    def __init__(self):
        super(uiCustomize, self).__init__()
        self.initUI()
        
    def initUI(self):
    
        self.setWindowIcon(iconFace)
        
        self.setGeometry(1145, 610, 275, 250)
        self.setWindowTitle('Customize template')
        

        self.lr = QtWidgets.QLabel("R : 127", self)
        self.lr.move(100, 10)
        self.lg = QtWidgets.QLabel("G : 127", self)
        self.lg.move(100, 50)
        self.lb = QtWidgets.QLabel("B : 127", self)
        self.lb.move(100, 90)
        self.lscale = QtWidgets.QLabel("Scale : 0.03", self)
        self.lscale.move(100, 140)

        self.r = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.r.move(10, 10)
        self.r.setMinimum(0)
        self.r.setMaximum(255)
        self.r.setValue(127)
        self.r.valueChanged.connect(self.valuechangeR)
        
        self.g = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.g.move(10, 50)
        self.g.setMinimum(0)
        self.g.setMaximum(255)
        self.g.setValue(127)
        self.g.valueChanged.connect(self.valuechangeG)
        
        self.b = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.b.move(10, 90)
        self.b.setMinimum(0)
        self.b.setMaximum(255)
        self.b.setValue(127)
        self.b.valueChanged.connect(self.valuechangeB)
        
        self.scale = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.scale.move(10, 140)
        self.scale.setMinimum(0)
        self.scale.setMaximum(100)
        self.scale.setValue(30)
        self.scale.valueChanged.connect(self.valuechangeScale)

        self.show()

    def valuechangeR(self):
        value = self.r.value()
        self.lr.setText("R : " + str(value))
        Sensors.customTemplate.color[0] = value
        
        State.saveTemplate(StickMan.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(StickMan.virtuMan)

    def valuechangeG(self):
        value = self.g.value()
        self.lg.setText("G : " + str(value))
        Sensors.customTemplate.color[1] = value
        
        State.saveTemplate(StickMan.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(StickMan.virtuMan)
        
    def valuechangeB(self):
        value = self.b.value()
        self.lb.setText("B : " + str(value))
        Sensors.customTemplate.color[2] = value
        
        State.saveTemplate(StickMan.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(StickMan.virtuMan)
        
    def valuechangeScale(self):
        value = self.scale.value()
        self.lscale.setText("Size : " + str(value/1000.))
        Sensors.customTemplate.scale = value/1000.
        
        State.saveTemplate(StickMan.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(StickMan.virtuMan)


uiAvatars = None
uiPostures = None
uiTemplates = None
uiZoi = None
uiGroups = None

ListAvatars = 0
ListPostures = 1
ListTemplates = 2
ListZoi = 3
ListGroups = 4


class uiList(QtWidgets.QWidget):
    
    def __init__(self, listType):
        super(uiList, self).__init__()
        self.listType = listType
        self.initUI()
        
    def initUI(self):
    
        self.setWindowIcon(iconFace)

        self.qle = QtWidgets.QLineEdit(self)
        self.qle.move(10, 10)

        
        saveButton = QtWidgets.QPushButton('', self)
        saveButton.resize(30,30)
        saveButton.move(150, 5)
        saveButton.clicked.connect(self.save)
        saveButton.setIcon(iconSave)

        reloadButton = QtWidgets.QPushButton('', self)
        reloadButton.resize(30,30)
        reloadButton.move(180, 5)
        reloadButton.clicked.connect(self.reload)
        reloadButton.setIcon(iconLoad)
        
        deleteButton = QtWidgets.QPushButton('', self)
        deleteButton.resize(30,30)
        deleteButton.move(210, 5)
        deleteButton.clicked.connect(self.delete)
        deleteButton.setIcon(iconDelete)

        renameButton = QtWidgets.QPushButton('', self)
        renameButton.resize(30,30)
        renameButton.move(240, 5)
        renameButton.clicked.connect(self.rename)
        renameButton.setIcon(iconRename)


        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.move(10, 40)
        self.listWidget.selectionModel().selectionChanged.connect(self.itemSelect)
        #self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        if self.listType == ListAvatars:
            self.setWindowTitle('Avatars')
            self.setGeometry(850, 30, 275, 250)
            State.updateAvatar()
            self.listWidget.addItems(State.avatarFileName)
            saveButton.setEnabled(False)
            deleteButton.setEnabled(False)
        elif self.listType == ListPostures:
            self.setGeometry(1145, 30, 275, 250)
            self.setWindowTitle('Postures')
            State.updatePosture(StickMan.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            self.setGeometry(850, 320, 275, 250)
            self.setWindowTitle('Templates')
            State.updateTemplate(StickMan.virtuMan)
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListZoi:
            self.setGeometry(1145, 320, 275, 250)
            self.setWindowTitle('Zoi')
            self.listWidget.addItems(State.zoiFileName)
            saveButton.setEnabled(False)
            deleteButton.setEnabled(False)
        elif self.listType == ListGroups:
            self.setGeometry(850, 610, 275, 250)
            self.setWindowTitle('Groups')
            State.updateGroup(StickMan.virtuMan)
            self.listWidget.addItems(State.groupFileName)
            
        self.show()

        
    def itemSelect(self, text):
        text = ""
        if self.listWidget.currentItem() != None:
            text = self.listWidget.currentItem().text()
        self.qle.setText(text)
        
        if self.listType == ListAvatars:
            if self.listWidget.currentItem() == None:
                return
            State.loadAvatar(StickMan.virtuMan, text)
            uiPostures.listWidget.setCurrentItem(None)
            uiPostures.listWidget.clear()
            uiPostures.listWidget.addItems(State.postureFileName)
            uiGroups.listWidget.setCurrentItem(None)
            uiGroups.listWidget.clear()
            uiGroups.listWidget.addItems(State.groupFileName)
            uiTemplates.listWidget.setCurrentItem(None)
            uiTemplates.listWidget.clear()
            uiTemplates.listWidget.addItems(State.templateFileName)
            uiZoi.listWidget.setCurrentItem(None)
            uiZoi.listWidget.clear()
            uiZoi.listWidget.addItems(State.zoiFileName)
        elif self.listType == ListPostures:
            State.loadPosture(StickMan.virtuMan, text)
        elif self.listType == ListTemplates:
            GUI.selectedTemplate = text
            State.updateZoi(StickMan.virtuMan)
            uiZoi.listWidget.setCurrentItem(None)
            uiZoi.listWidget.clear()
            uiZoi.listWidget.addItems(State.zoiFileName)
            for sensorData in Sensors.sensorGraphics:
                if text == sensorData.type:
                    uiCustom.r.setValue(sensorData.color[0])
                    uiCustom.g.setValue(sensorData.color[1])
                    uiCustom.b.setValue(sensorData.color[2])
        elif self.listType == ListZoi:
            State.loadZOI(StickMan.virtuMan, text)
        elif self.listType == ListGroups:
            State.loadGroup(StickMan.virtuMan, text)
        
    def save(self):

        text = self.qle.text()

        if self.listType == ListPostures:
            State.savePosture(StickMan.virtuMan, text)
            State.updatePosture(StickMan.virtuMan)
            self.listWidget.setCurrentItem(None)
            self.listWidget.clear()
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            State.saveTemplate(StickMan.virtuMan, text)
            State.updateTemplate(StickMan.virtuMan)
            self.listWidget.setCurrentItem(None)
            self.listWidget.clear()
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListGroups:
            State.saveGroups(StickMan.virtuMan, text)
            State.updateGroup(StickMan.virtuMan)
            self.listWidget.setCurrentItem(None)
            self.listWidget.clear()
            self.listWidget.addItems(State.groupFileName)
            

    def reload(self):
        if self.listWidget.currentItem() == None:
            return

        self.listWidget.setCurrentItem(None)
        
    def delete(self):
        if self.listWidget.currentItem() == None:
            return
        #### TODO : update child lists when removing a parent item ?
        text = self.listWidget.currentItem().text()
        self.listWidget.setCurrentItem(None)
        self.listWidget.clear()
        if self.listType == ListAvatars:
            State.updateAvatar()
            self.listWidget.addItems(State.avatarFileName)
        elif self.listType == ListPostures:
            State.removePosture(StickMan.virtuMan, text)
            State.updatePosture(StickMan.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            State.removeTemplate(StickMan.virtuMan, text)
            State.updateTemplate(StickMan.virtuMan)
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListGroups:
            State.removeGroup(StickMan.virtuMan, text)
            State.updateGroup(StickMan.virtuMan)
            self.listWidget.addItems(State.groupFileName)

    def rename(self):
        if self.listWidget.currentItem() == None:
            return

        oldName = self.listWidget.currentItem().text()
        newName = self.qle.text()
        self.listWidget.setCurrentItem(None)
        self.listWidget.clear()
        
        if self.listType == ListAvatars: #setCurrentItem needed, or crash
            State.renameAvatar(StickMan.virtuMan, oldName, newName)
            State.updateAvatar()
            self.listWidget.addItems(State.avatarFileName)
        elif self.listType == ListPostures:
            State.renamePosture(StickMan.virtuMan, oldName, newName)
            State.updatePosture(StickMan.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            uiGroups.listWidget.setCurrentItem(None)
            State.renameTemplate(StickMan.virtuMan, oldName, newName)
            State.updateTemplate(StickMan.virtuMan)
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListZoi:
            State.renameZoi(StickMan.virtuMan, oldName, newName)
            State.updateZoi(StickMan.virtuMan)
            self.listWidget.addItems(State.zoiFileName)
        elif self.listType == ListGroups:
            State.renameGroup(StickMan.virtuMan, oldName, newName)
            State.updateGroup(StickMan.virtuMan)
            self.listWidget.addItems(State.groupFileName)



class mainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args):
        self.initialized = False
        self.displayFBO = 1 # for some reasons PyQt made a new fbo on it's own, so it's 1 and not 0 ?
        self.idFBO = None
        super(mainWindow, self).__init__(*args)
        loadUi('minimal.ui', self)


    def setupUI(self):
        self.setWindowTitle('Wearable Sensors')
        self.setWindowIcon(iconFace)
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
            Update files lists.
            you can edit / add / remove groupe & template files without closing software (as long as syntax is respected)
        """
        #State.updateFilesLists(StickMan.virtuMan)
        #GUI.updateGuiLists()



        """
            Events management.
            Keyboard interactions between the user and the software are done here.
        """
        Events.manage()
        


        """
            Update all entities ID
        """
        ID.setId([StickMan.virtuMan.limbs, StickMan.virtuMan.muscles, Sensors.virtuSens, Sensors.zoiSens, GUI.guiPannel, GUI.guiSensorTypes, GUI.guiSensorZoi, GUI.guiSensorGroups, GUI.guiPostures])
        


        """
            Preprocess entities.
            Store all needed transformations to significantly lower calculation cost when rendering (redundancy otherwise between display buffer, ID buffer and bindings)
        """
        if Limbs.lookingAtID != 0:
            Definitions.modelMatrix.translate(-Limbs.lookingAt[0][0],-Limbs.lookingAt[0][1],-Limbs.lookingAt[0][2])
        else:
            Definitions.modelMatrix.set(np.identity(4))

        # Preprocess of limbs
        Definitions.modelMatrix.push()
        Definitions.modelMatrix.translate(StickMan.virtuMan.position[0],StickMan.virtuMan.position[1],StickMan.virtuMan.position[2])
        R = Definitions.vector4D.Quat2Vec(Definitions.vector4D((StickMan.virtuMan.orientation)))
        Definitions.modelMatrix.rotate(R.o,R.x,R.y,R.z)
        StickMan.limb = -1 # initialize the recursivity here
        Sensors.countID = 0
        Graphics.SaturationModelMatrix = []
        StickMan.stick(StickMan.virtuMan)
        Definitions.modelMatrix.pop()

        Muscles.preprocessMuscle(StickMan.virtuMan)
        Ground.preprocessGround(math.fabs(Events.rMax))

        i = 0
        for package in Definitions.packagePreprocess:
            j = 0
            for pack in package:
                if pack[Definitions.packParent] == "Ground":
                    Definitions.packageIndices[0] = Definitions.packageIndices[0] + [[i, j],]
                j += 1
            i += 1
        #print(len(Definitions.packagePreprocess))


        """ 
            Draw on the ID buffer.
            The ID BUFFER is used for the mouse implementation, to know which body/sensor/gui limb is targeted with the cursor.
        """
        # bind the ID buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.idFBO)
        # clear the ID buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # fill ID buffer

        window = GUI.windowScene
        GUI.subWindow(window,False)

        Graphics.modelView(Graphics.opaque)
        
        Limbs.drawBodySurface(StickMan.virtuMan, Graphics.idBuffer, Events.SHOW)
        Muscles.drawMuscleSurface(StickMan.virtuMan, Graphics.idBuffer, Events.SHOW)
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
        window = GUI.windowScene
        GUI.subWindow(window,Events.style != Graphics.idBuffer)
        
        # draw scene
        Graphics.modelView(Graphics.blending)
        Ground.drawGround()

        # draw saturation balls
        Graphics.modelView(Graphics.blending)
        Saturations.drawSaturationBalls()
        
        # draw FADE body
        Graphics.modelView(Graphics.blending)
        Limbs.drawBodySurface(StickMan.virtuMan, Events.style, Events.FADE)
        # draw FADE muscles
        Graphics.modelView(Events.style)
        Muscles.drawMuscleSurface(StickMan.virtuMan, Events.style, Events.FADE)
        
        # draw SHOW body
        Graphics.modelView(Events.style)
        Limbs.drawBodySurface(StickMan.virtuMan, Events.style, Events.SHOW)
        Limbs.drawBodyEdge(StickMan.virtuMan, Events.style)
        # draw SHOW muscles
        Graphics.modelView(Events.style)
        Muscles.drawMuscleSurface(StickMan.virtuMan, Events.style, Events.SHOW)
        Muscles.drawMuscleEdge(StickMan.virtuMan, Events.style)
            
        # draw saturation lines
        Graphics.modelView(Graphics.opaque)
        Saturations.drawSaturationLines()
        
        # draw sensors
        Graphics.modelView(Graphics.opaque)
        Sensors.drawSensor(Events.style)
        Sensors.drawDashed(Events.style)
        


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

        #print(int(1./(time.clock()-flagStart)))

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
    
        Definitions.projectionMatrix.perspectiveProjection(90, GUI.display[0]/GUI.display[1], 0.1, 100.0)
        glUniformMatrix4fv(Shaders.proj_loc, 1, GL_FALSE, Definitions.projectionMatrix.peek())
        glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())

    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            Events.mouse_click = True
        if event.button() == QtCore.Qt.RightButton:
            Events.setLookAt = True

    def keyPressEvent(self, event):
        Events.eventModifier = QtWidgets.QApplication.keyboardModifiers()
        if event.isAutoRepeat() == False:
            Events.eventKey = event.key()
            Events.eventPress = True

    def keyReleaseEvent(self, event):
        Events.eventModifier = QtWidgets.QApplication.keyboardModifiers()
        if event.isAutoRepeat() == False:
            Events.eventKey = event.key()
            Events.eventPress = False

    
if __name__ == '__main__':
    global uiPostures
    global uiTemplates
    global uiZoi
    global uiGroups

    global iconSave
    global iconLoad
    global iconFace
    global iconDelete

    """ Create Entities """
    State.updateAvatar()
    StickMan.virtuMan = StickMan.characteristics(1.7)
    State.loadAvatar(StickMan.virtuMan, State.avatarFileName[0])

    """ window size """
    State.importUserSettings()
    GUI.resize()

    """ Application """
    app = QtWidgets.QApplication(sys.argv)
    
    iconSave  = QtGui.QIcon("Textures/Save.png")
    iconLoad  = QtGui.QIcon("Textures/Load.png")
    iconFace  = QtGui.QIcon("Textures/Face.png")
    iconDelete = QtGui.QIcon("Textures/Delete.png")
    iconRename = QtGui.QIcon("Textures/Rename.png")

    """ UI """
    uiAvatars = uiList(ListAvatars)
    uiPostures = uiList(ListPostures)
    uiTemplates = uiList(ListTemplates)
    uiZoi = uiList(ListZoi)
    uiGroups = uiList(ListGroups)
    uiCustom = uiCustomize()

    """ 3D Scene """
    window = mainWindow()
    window.setupUI()
    window.show()



    sys.exit(app.exec_())