#
#   File : UI.py
#   
#   Code written by : Johann Heches
#
#   Description : Manage all user interfaces.
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
import ID
import Limbs
import Muscles
import Saturations
import Sensors
import Shaders
import State
import Avatar


iconSave  = None
iconLoad  = None
iconFace  = None
iconDelete = None
iconRename = None



class uiSensors(QtWidgets.QWidget):
    
    def __init__(self):
        super(uiSensors, self).__init__()
        self.initUI()
        
    def initUI(self):
    
        self.setWindowIcon(iconFace)

        self.edit = QtWidgets.QLineEdit(self)
        self.edit.move(10, 10)
        self.edit.editingFinished.connect(self.valueEdit)


        self.table = QtWidgets.QTableWidget(self)
        self.table.move(10, 40)
        self.table.selectionModel().selectionChanged.connect(self.itemSelect)

        self.setWindowTitle('Sensors')
        self.setGeometry(1145, 610, 275, 250)
        
        self.table.setRowCount(len(Sensors.virtuSens))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tag","Type","Attach", "x", "t", "s"])
        for i in range(0,len(Sensors.virtuSens)):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].tag))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].type))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].attach))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].x)))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].t)))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].s)))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
            
        self.show()

    def updateTable(self):
        self.table.setRowCount(len(Sensors.virtuSens))
        self.table.setColumnCount(6)
        for i in range(0,len(Sensors.virtuSens)):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].tag))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].type))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].attach))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].x)))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].t)))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].s)))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        
    def itemSelect(self, text):
        text = ""
        if self.table.currentItem() != None:
            text = self.table.currentItem().text()
            Sensors.selectedSens = self.table.currentRow() + ID.offsetId(ID.SENSOR)
        else:
            print("TODO, not working yet.")
            Sensors.selectedSens = 0
        self.edit.setText(text)

    
    def valueEdit(self):
        try:
            value = self.edit.text()
            self.table.currentItem().setText(value)
            if self.table.currentColumn() == 0:
                Sensors.virtuSens[self.table.currentRow()].tag = value
            elif self.table.currentColumn() == 1:
                Sensors.virtuSens[self.table.currentRow()].type = value
            elif self.table.currentColumn() == 2:
                Sensors.virtuSens[self.table.currentRow()].attach = value
            elif self.table.currentColumn() == 3:
                Sensors.virtuSens[self.table.currentRow()].x = float(value)
            elif self.table.currentColumn() == 4:
                Sensors.virtuSens[self.table.currentRow()].t = float(value)
            elif self.table.currentColumn() == 5:
                Sensors.virtuSens[self.table.currentRow()].s = float(value)

            text = uiGroups.qle.text()
            State.saveGroups(Avatar.virtuMan, text)
            State.updateGroup(Avatar.virtuMan)
        except:
            pass


class uiCustomize(QtWidgets.QWidget):
    
    def __init__(self):
        super(uiCustomize, self).__init__()
        self.initUI()
        
    def initUI(self):
    
        self.setWindowIcon(iconFace)
        
        self.setGeometry(1145, 610, 275, 250)
        self.setWindowTitle('Customize template')
        
        self.editR = QtWidgets.QLineEdit("127",self)
        self.editR.move(130, 10)
        self.editR.editingFinished.connect(self.valueEditR)
        self.editG = QtWidgets.QLineEdit("127",self)
        self.editG.move(130, 50)
        self.editG.editingFinished.connect(self.valueEditG)
        self.editB = QtWidgets.QLineEdit("127",self)
        self.editB.move(130, 90)
        self.editB.editingFinished.connect(self.valueEditB)
        self.editScale = QtWidgets.QLineEdit("0.03",self)
        self.editScale.move(130, 130)
        self.editScale.editingFinished.connect(self.valueEditScale)
        self.editShape = QtWidgets.QLineEdit("0",self)
        self.editShape.move(130, 170)
        self.editShape.editingFinished.connect(self.valueEditShape)

        self.lr = QtWidgets.QLabel("Red", self)
        self.lr.move(100, 10)
        self.lg = QtWidgets.QLabel("Green", self)
        self.lg.move(100, 50)
        self.lb = QtWidgets.QLabel("Blue", self)
        self.lb.move(100, 90)
        self.lscale = QtWidgets.QLabel("Scale", self)
        self.lscale.move(100, 130)
        self.lshape = QtWidgets.QLabel("Shape", self)
        self.lshape.move(100, 170)

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
        self.scale.move(10, 130)
        self.scale.setMinimum(0)
        self.scale.setMaximum(100)
        self.scale.setValue(30)
        self.scale.valueChanged.connect(self.valuechangeScale)
        
        self.shape = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.shape.move(10, 170)
        self.shape.setMinimum(0)
        self.shape.setMaximum(7)
        self.shape.setValue(0)
        self.shape.valueChanged.connect(self.valuechangeShape)

        self.show()
        
    def valueEditR(self):
        try:
            value = int(self.editR.text())
            self.r.setValue(value)
            Sensors.customTemplate.color[0] = value
        
            State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
            State.updateTemplate(Avatar.virtuMan)
        except:
            pass
        
    def valueEditG(self):
        try:
            value = int(self.editG.text())
            self.g.setValue(value)
            Sensors.customTemplate.color[1] = value
        
            State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
            State.updateTemplate(Avatar.virtuMan)
        except:
            pass
        
    def valueEditB(self):
        try:
            value = int(self.editB.text())
            self.b.setValue(value)
            Sensors.customTemplate.color[2] = value
        
            State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
            State.updateTemplate(Avatar.virtuMan)
        except:
            pass
        
    def valueEditScale(self):
        try:
            value = float(self.editScale.text())
            self.scale.setValue(int(1000*value))
            Sensors.customTemplate.scale = value
        
            State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
            State.updateTemplate(Avatar.virtuMan)
        except:
            pass
        
    def valueEditShape(self):
        try:
            value = int(self.editShape.text())
            self.shape.setValue(value)
            Sensors.customTemplate.shape = value
        
            State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
            State.updateTemplate(Avatar.virtuMan)
        except:
            pass

    def valuechangeR(self):
        value = self.r.value()
        self.editR.setText(str(value))
        Sensors.customTemplate.color[0] = value
        
        State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(Avatar.virtuMan)

    def valuechangeG(self):
        value = self.g.value()
        self.editG.setText(str(value))
        Sensors.customTemplate.color[1] = value
        
        State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(Avatar.virtuMan)
        
    def valuechangeB(self):
        value = self.b.value()
        self.editB.setText(str(value))
        Sensors.customTemplate.color[2] = value
        
        State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(Avatar.virtuMan)
        
    def valuechangeScale(self):
        value = self.scale.value()
        self.editScale.setText(str(value/1000.))
        Sensors.customTemplate.scale = value/1000.
        
        State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(Avatar.virtuMan)
        
    def valuechangeShape(self):
        value = self.shape.value()
        self.editShape.setText(str(value))
        Sensors.customTemplate.shape = value
        
        State.saveTemplate(Avatar.virtuMan, uiTemplates.qle.text())
        State.updateTemplate(Avatar.virtuMan)


uiAvatars = None
uiPostures = None
uiTemplates = None
uiZoi = None
uiGroups = None
uiCustom = None
uiSensor = None

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
            State.updatePosture(Avatar.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            self.setGeometry(850, 320, 275, 250)
            self.setWindowTitle('Templates')
            State.updateTemplate(Avatar.virtuMan)
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
            State.updateGroup(Avatar.virtuMan)
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
            State.loadAvatar(Avatar.virtuMan, text)
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
            
            uiSensor.table.setRowCount(len(Sensors.virtuSens))
            uiSensor.table.setColumnCount(6)
            for i in range(0, len(Sensors.virtuSens)):
                uiSensor.table.setItem(i, 0, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].tag))
                uiSensor.table.setItem(i, 1, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].type))
                uiSensor.table.setItem(i, 2, QtWidgets.QTableWidgetItem(Sensors.virtuSens[i].attach))
                uiSensor.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].x)))
                uiSensor.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].t)))
                uiSensor.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(Sensors.virtuSens[i].s)))
            uiSensor.table.resizeColumnsToContents()
            uiSensor.table.resizeRowsToContents()
        elif self.listType == ListPostures:
            State.loadPosture(Avatar.virtuMan, text)
        elif self.listType == ListTemplates:
            Sensors.selectedTemplate = text
            State.updateZoi(Avatar.virtuMan)
            uiZoi.listWidget.setCurrentItem(None)
            uiZoi.listWidget.clear()
            uiZoi.listWidget.addItems(State.zoiFileName)
            for sensorData in Sensors.sensorGraphics:
                if text == sensorData.type:
                    uiCustom.r.setValue(sensorData.color[0])
                    uiCustom.g.setValue(sensorData.color[1])
                    uiCustom.b.setValue(sensorData.color[2])
                    uiCustom.shape.setValue(sensorData.shape)
                    uiCustom.scale.setValue(int(sensorData.scale*1000))

        elif self.listType == ListZoi:
            State.loadZOI(Avatar.virtuMan, text)
        elif self.listType == ListGroups:
            State.loadGroup(Avatar.virtuMan, text)
            uiSensor.updateTable()
        
    def save(self):

        text = self.qle.text()

        if self.listType == ListPostures:
            State.savePosture(Avatar.virtuMan, text)
            State.updatePosture(Avatar.virtuMan)
            self.listWidget.setCurrentItem(None)
            self.listWidget.clear()
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            State.saveTemplate(Avatar.virtuMan, text)
            State.updateTemplate(Avatar.virtuMan)
            self.listWidget.setCurrentItem(None)
            self.listWidget.clear()
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListGroups:
            State.saveGroups(Avatar.virtuMan, text)
            State.updateGroup(Avatar.virtuMan)
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
            State.removePosture(Avatar.virtuMan, text)
            State.updatePosture(Avatar.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            State.removeTemplate(Avatar.virtuMan, text)
            State.updateTemplate(Avatar.virtuMan)
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListGroups:
            State.removeGroup(Avatar.virtuMan, text)
            State.updateGroup(Avatar.virtuMan)
            self.listWidget.addItems(State.groupFileName)

    def rename(self):
        if self.listWidget.currentItem() == None:
            return

        oldName = self.listWidget.currentItem().text()
        newName = self.qle.text()
        self.listWidget.setCurrentItem(None)
        self.listWidget.clear()
        
        if self.listType == ListAvatars: #setCurrentItem needed, or crash
            State.renameAvatar(Avatar.virtuMan, oldName, newName)
            State.updateAvatar()
            self.listWidget.addItems(State.avatarFileName)
        elif self.listType == ListPostures:
            State.renamePosture(Avatar.virtuMan, oldName, newName)
            State.updatePosture(Avatar.virtuMan)
            self.listWidget.addItems(State.postureFileName)
        elif self.listType == ListTemplates:
            uiGroups.listWidget.setCurrentItem(None)
            State.renameTemplate(Avatar.virtuMan, oldName, newName)
            State.updateTemplate(Avatar.virtuMan)
            self.listWidget.addItems(State.templateFileName)
        elif self.listType == ListZoi:
            State.renameZoi(Avatar.virtuMan, oldName, newName)
            State.updateZoi(Avatar.virtuMan)
            self.listWidget.addItems(State.zoiFileName)
        elif self.listType == ListGroups:
            State.renameGroup(Avatar.virtuMan, oldName, newName)
            State.updateGroup(Avatar.virtuMan)
            self.listWidget.addItems(State.groupFileName)


