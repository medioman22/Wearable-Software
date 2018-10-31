#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:08:06 2018

@author: matteomacchini
"""


import time
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg

hor = 1800
ver = 300

app = QtGui.QApplication([])

win1 = pg.GraphicsWindow(title="Motors 1 2 3") #now window for real time plot of motor 1
win1.resize(hor,ver)
win2 = pg.GraphicsWindow(title="Motors 4 5 6") #now window for real time plot of motor 1
win2.resize(hor,ver)
win3 = pg.GraphicsWindow(title="Motors  7 8 9") #now window for real time plot of motor 1
win3.resize(hor,ver)

p = []
for i in range(0,2):
    title_plot = "Realtime plot (%d)" %i
    p.append(win1.addPlot(title=title_plot))
for i in range(3,5):
    title_plot = "Realtime plot (%d)" %i
    p.append(win2.addPlot(title=title_plot))
for i in range(6,8):
    title_plot = "Realtime plot (%d)" %i
    p.append(win2.addPlot(title=title_plot))

#print(p)
    
p1 = win1.addPlot(title="Realtime plot") #empty space for real time plot
p1.setYRange(0,1.5, padding = None)
p2 = win1.addPlot(title ="Realtime plot 2")
p2.setYRange(0,1.5, padding = None)
p3 = win1.addPlot(title ="Realtime plot 3")
p3.setYRange(0,1.5, padding = None)
p4 = win2.addPlot(title="Realtime plot 4") #empty space for real time plot
p4.setYRange(0,1.5, padding = None)
p5 = win2.addPlot(title ="Realtime plot 5")
p5.setYRange(0,1.5, padding = None)
p6 = win2.addPlot(title ="Realtime plot 6")
p6.setYRange(0,1.5, padding = None)
p7 = win3.addPlot(title="Realtime plot 7") #empty space for real time plot
p7.setYRange(0,1.5, padding = None)
p8 = win3.addPlot(title ="Realtime plot 8")
p8.setYRange(0,1.5, padding = None)
p9 = win3.addPlot(title ="Realtime plot 9")
p9.setYRange(0,1.5, padding = None)

curve1 = p1.plot() 
curve2 = p2.plot()
curve3 = p3.plot() 
curve4 = p4.plot()
curve5 = p5.plot() 
curve6 = p6.plot()
curve7 = p7.plot() 
curve8 = p8.plot()
curve9 = p9.plot() 

time_pointer = 0
windowWidth = 10
nbOfData = 40
time_tab = np.linspace(0,0,nbOfData)    
                 # width of the window displaying the curve
Y1,Y2,Y3,Y4,Y5,Y6,Y7,Y8,Y9 = np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData),np.linspace(0,0,nbOfData)       # create array that will contain the relevant time series     


listOfMotorSignals = [];
for i in range(0,9):
    Yi = [0]*nbOfData;
    listOfMotorSignals.append(Yi);

print (listOfMotorSignals)

motors = [0,0,0,0,0,0,0,0,0]


class haptic_device():
    
    """
    REMEMBER : ALL class functions have 'self' as a first argument
    """
    
    ### CLASS FUNCTIONS ###
   
        
    def __init__(self):
        self.motor_number = 9
        self.matteo = 'nice guy !'
        
        self.motor_state = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0]
#     def _init_windows(self) :    
        
    ### PRIVATE FUNCTIONS ###
    
    # they start with a _
    
        
    ### PUBLIC FUNCTIONS ###
    
    def motor_activation(self, num, duty):
        self.update()
        if duty: 
#            print('Motor',num,'switched on with duty of', duty)
            self.motor_state[num-1] = duty
#            print(motors)
        else : 
#            print('Motor',num,' switched off')
            self.motor_state[num-1] = 0
        self.update()
    
    def motor_control_flat(self, length, duty, direction):
        self.motor_activation(direction[0],duty)        
        self.waitAndUpdate(length/3)
        self.motor_activation(direction[0],0)
        self.motor_activation(direction[1],duty)
        self.waitAndUpdate(length/3)
        self.motor_activation(direction[1],0)
        self.motor_activation(direction[2],duty)
        self.waitAndUpdate(length/3)
        self.motor_activation(direction[2],0)
        self.waitAndUpdate(1)
        
    def motor_control_linear(self, length, duty, direction, fraction = 10):

        for i in range(1,fraction+1):
            self.motor_activation(direction[0],i*duty/fraction)
            self.wait(length/(4*fraction)) #4 is coming from the 4 different phases
        for i in range(1,fraction+1):
            self.motor_activation(direction[0],(fraction-i)*duty/fraction)
            self.motor_activation(direction[1],i*duty/fraction)
            self.wait(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[1],(fraction-i)*duty/fraction)
            self.motor_activation(direction[2],i*duty/fraction)
            self.wait(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[2],(fraction-i)*duty/fraction)
            self.wait(length/(4*fraction))
        #self.waitAndUpdate(2)    #just to set a little break between the impulsions         
        
    def motor_control_sinus(self, length, duty, direction):
        print('sinus motor control')
        
        
        
    def impulsion_command(self, direction,length = 1, signalType = 'linear', duty = 1):
        
        if signalType == 'flat':
            self.motor_control_flat(length,duty,direction)
        elif signalType == 'linear':
            self.motor_control_linear(length,duty,direction)
        elif signalType == 'sinus':
            self.motor_control_sinus(length, duty, direction)
        else: 
            print('Incorrect signal type')
        
   # Realtime data plot. Each time this function is called, the data display is updated
    def update(self):
        global curve1,curve2,curve3,curve4,curve5,curve6,curve7,curve8,curve9, Y1,Y2,Y3,Y4,Y5,Y6,Y7,Y8,Y9, time_pointer, nbOfData, time_tab
        
        time_tab = np.roll(time_tab,-1)
        time_tab[-1] = time_pointer

        Y1 = np.roll(Y1,-1)                      # shift data in the temporal mean 1 sample left
        Y2 = np.roll(Y2,-1)                      # shift data in the temporal mean 1 sample left
        Y3 = np.roll(Y3,-1)                      # shift data in the temporal mean 1 sample left
        Y4 = np.roll(Y4,-1)                      # shift data in the temporal mean 1 sample left
        Y5 = np.roll(Y5,-1)                      # shift data in the temporal mean 1 sample left
        Y6 = np.roll(Y6,-1)                      # shift data in the temporal mean 1 sample left
        Y7 = np.roll(Y7,-1)                      # shift data in the temporal mean 1 sample left
        Y8 = np.roll(Y8,-1)                      # shift data in the temporal mean 1 sample left
        Y9 = np.roll(Y9,-1)                      # shift data in the temporal mean 1 sample left
      
        for i in range(0,9):
            listOfMotorSignals[i] = np.roll(listOfMotorSignals[i],-1)
            listOfMotorSignals[i][-1] = float(self.motor_state[i])
            
        
        Y1[-1] = float(self.motor_state[0])                  # vector containing the instantaneous values      
        Y2[-1] = float(self.motor_state[1])
        Y3[-1] = float(self.motor_state[2])
        Y4[-1] = float(self.motor_state[3])                   
        Y5[-1] = float(self.motor_state[4])
        Y6[-1] = float(self.motor_state[5])
        Y7[-1] = float(self.motor_state[6])                    
        Y8[-1] = float(self.motor_state[7])
        Y9[-1] = float(self.motor_state[8])
        
        curve1.setData(time_tab,listOfMotorSignals[0])            # set the curve with the table of the motor value and the table of the time 
        curve2.setData(time_tab,listOfMotorSignals[1])               
        curve3.setData(time_tab,listOfMotorSignals[2])
        curve4.setData(time_tab,listOfMotorSignals[3])
        curve5.setData(time_tab,listOfMotorSignals[4])
        curve6.setData(time_tab,listOfMotorSignals[5])
        curve7.setData(time_tab,listOfMotorSignals[6])
        curve8.setData(time_tab,listOfMotorSignals[7])
        curve9.setData(time_tab,listOfMotorSignals[8])

        
        QtGui.QApplication.processEvents()    # you MUST process the plot now 
        
    def waitAndUpdate(self, sec):
        self.update()
        self.wait(sec/4)
        self.update()
        self.wait(sec/4)
        self.update()
        self.wait(sec/4)
        self.update()
        self.wait(sec/4)
     
    
    def wait(self, sec):
#        print('waiting ', str(sec), ' seconds')
        global time_pointer
        time_pointer += sec
        time.sleep(sec)