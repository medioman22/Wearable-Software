        #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:08:06 2018

@author: matteomacchini
"""


import time
import numpy as np
#from pyqtgraph.Qt import QtGui
#import pyqtgraph as pg
import json
import keyboard 
import sys
#sys.path.append('C:\\Users\\hkohli\\Desktop\\Github\\Wearable-Software\\Interface\\src\\')
sys.path.append('C:\\Users\\Hugo\\Documents\\GitHub\\Wearable-Software\\Interface\\src\\')
from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection



c = BeagleboneGreenWirelessConnection()

I2C_interface = "PCA9685@I2C[1]"


t_init = 0 #iniate the timer to 0

NS = 1 #constants to activate several motors at the same time
WE = 3

north = np.array([8,5,2]) #each direction corresponds to a pattern of 3 successive motors
south = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])

dirGiven = ''
reactionTime = 0
intensityGiven = 0
mode = ''

direction_dict = {'q' : 'NW',
           'w' : 'N', 'e': 'NE', 'a': 'W', 'd': 'E', 'y': 'SW', 'x': 'S', 'c': 'SE', '1': 1,'2':2,'3':3,'4':4,'5':5} #corresponding key pressed by the user on the keyboard

userActivationForDir = False #boolean to activate each direction when the user desire (click on the space button)
feedbackGiven = False #set to true when the user press a key to give his feeback







class haptic_device():
    ### CLASS FUNCTIONS ###
        
    def __init__(self):
        self.motor_number = 9
        self.matteo = 'nice guy !'
        
        self.motor_state = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0]
    
        
    ### PUBLIC FUNCTIONS ###
    
    def connection(self):
        c.connect()
        print('Status: {}'.format(c.getState()))
        c.sendMessages([json.dumps({"type": "Settings", "name": I2C_interface, "dutyFrequency": '50 Hz'})])
        time.sleep(3)
        c.sendMessages([json.dumps({"type": "Settings", "name": I2C_interface, "scan": False})])
        
        
    
    def motor_activation(self, num, duty):
        motor = int(num- 1)
        c.sendMessages([json.dumps({"dim":  motor, "value": duty, "type": "Set", "name": I2C_interface})])
    
    
    
    def activate_row_of_3_motors(self, central_motor, direction, duty):
        NSWE = False
        SeNw = False
        SwNe = False
        if np.array_equal(direction, south) or np.array_equal(direction, north):
            const = NS
            NSWE = True
        elif np.array_equal(direction, east) or np.array_equal(direction, west):
            const = WE
            NSWE = True
        elif np.array_equal(direction, southeast) or np.array_equal(direction, northwest):
            SeNw = True
        else: SwNe = True
        if NSWE :
            motor_to_activate = [central_motor-const,central_motor,central_motor+const]
        if SeNw :
            if central_motor == 1 : motor_to_activate = [central_motor+1, central_motor, central_motor-3]
            if central_motor == 5 : motor_to_activate = [central_motor+2, central_motor, central_motor-2]
            if central_motor == 9 : motor_to_activate = [central_motor-1, central_motor, central_motor-3]
        if SwNe :
            if central_motor == 7 : motor_to_activate = [central_motor+1, central_motor, central_motor+3]
            if central_motor == 5 : motor_to_activate = [central_motor+4, central_motor, central_motor-4]
            if central_motor == 10 : motor_to_activate = [2, central_motor, 6]
        
        if 3 in motor_to_activate : #this is because the pin 2 of the I2C / pwm board doesn't work
            motor_to_activate[motor_to_activate.index(3)] = 10 
        
        self.motor_activation(motor_to_activate[0],duty)
        self.motor_activation(motor_to_activate[1],duty)
        self.motor_activation(motor_to_activate[2],duty)
        
        
    def motor_control_flat_all_motors(self, length, duty, direction):
        
        self.activate_row_of_3_motors(direction[0],direction,duty)               
        time.sleep(length/3)
        self.activate_row_of_3_motors(direction[0],direction,0) 
        self.activate_row_of_3_motors(direction[1],direction,duty) 
        time.sleep(length/3)
        self.activate_row_of_3_motors(direction[1],direction,0) 
        self.activate_row_of_3_motors(direction[2],direction,duty) 
        time.sleep(length/3)
        self.activate_row_of_3_motors(direction[2],direction,0) 
        for i in range(0,10):
            c.sendMessages([json.dumps({"dim": i, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
        
    def motor_control_linear_all_motors(self, length, duty, direction,fraction = 10):
        start_point = 1
        step = duty/fraction
        for i in range(0,fraction):
            self.activate_row_of_3_motors(direction[0],direction,(i+1)*step)
            time.sleep(length/(4*fraction))
        for i in range(0,fraction):
            self.activate_row_of_3_motors(direction[0],direction,(fraction-(i+1)+start_point)*step)
            self.activate_row_of_3_motors(direction[1],direction,(i+1)*step)
            time.sleep(length/(4*fraction))
        for i in range(0,fraction):
            self.activate_row_of_3_motors(direction[1],direction,(fraction-(i+1)+start_point)*step)
            self.activate_row_of_3_motors(direction[2],direction,(i+1)*step)
            time.sleep(length/(4*fraction))
        for i in range(0,fraction):
            self.activate_row_of_3_motors(direction[2],direction,(fraction-(i+1)+start_point)*step)
            self.wait(length/(4*fraction))
        for i in range(0,10):
            c.sendMessages([json.dumps({"dim": i, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
            
             
        
    def motor_control_linear(self, length, duty, direction, fraction = 10):
        step = duty/fraction
        start_point = 2
        waitTime = length/(4*(fraction-start_point))
        for i in range(start_point,fraction):
            t1 = time.time()
            self.motor_activation(direction[0],(i+1)*step)
            t2 = time.time()
            time.sleep(waitTime - (t2-t1)) #4 is coming from the 4 different phases
        for i in range(start_point,fraction):
            t1 = time.time()
            self.motor_activation(direction[0],(fraction-(i+1)+start_point)*step)
            self.motor_activation(direction[1],(i+1)*duty/fraction)
            t2 = time.time()
            time.sleep(waitTime - (t2-t1))
        self.motor_activation(direction[0],0)
        for i in range(start_point,fraction):
            t1 = time.time()
            self.motor_activation(direction[1],(fraction-(i+1)+start_point)*step)
            self.motor_activation(direction[2],(i+1)*step)
            t2 = time.time()
            time.sleep(waitTime - (t2-t1))
        self.motor_activation(direction[1],0)
        for i in range(start_point,fraction):
            t1 = time.time()
            self.motor_activation(direction[2],(fraction-(i+1)+start_point)*step)
            t2 = time.time()
            time.sleep(waitTime - (t2-t1))
        self.motor_activation(direction[2],0)
        for i in range(0,10):
            c.sendMessages([json.dumps({"dim": i, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
        
    def motor_control_flat(self, length, duty, direction):
#        t1 = time.time()
        self.motor_activation(direction[0],duty)  
#        t2 = time.time()
        time.sleep(length/3)# - (t2-t1))
#        t1 = time.time()
        self.motor_activation(direction[0],0)
        self.motor_activation(direction[1],duty)
#        t2 = time.time()
        time.sleep(length/3)# - (t2-t1))
#        t1 = time.time()
        self.motor_activation(direction[1],0)
        self.motor_activation(direction[2],duty)
#        t2 = time.time()
        time.sleep(length/3)# - (t2-t1))
        self.motor_activation(direction[2],0)
        
        for i in range(0,10):
            c.sendMessages([json.dumps({"dim": i, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
                
    
    def measure_time(self):
        was_pressed = False
        wasPressedSpace = False
        global userActivationForDir, feedbackGiven, dirGiven, reactionTime, mode, intensityGiven
        
        while True:         #making an infinite loop
            try:            #used try so that if user pressed other than the given key error will not be shown    
                key_pressed = self.check_key_pressed(direction_dict)
                
                if keyboard.is_pressed('space'):
                    if not wasPressedSpace :
                        userActivationForDir = True
                        wasPressedSpace = True
                        print('')
                    pass
                
                elif key_pressed : #if direction key is pressed
                    if  was_pressed == False and feedbackGiven == False :
                        t_fin = time.time()
                        reactionTime = str(round(t_fin-t_init, 2))
                        feedbackGiven = True
                        was_pressed = True
                        if mode == 'direction' :
                            dirGiven = key_pressed
                            print('Direction : ', key_pressed, ', Reaction time :', reactionTime)
                        elif mode == 'intensity' or mode == 'intensity_and_length':
                            intensityGiven = key_pressed
                            print('Intensity : ', key_pressed, ', Reaction time :', reactionTime)
                    pass   #finishing the loop
                else:
                    was_pressed = False
                    wasPressedSpace = False
                    pass
                
            except:
                break
        

    def check_key_pressed(self,direction_dict):
        for key in direction_dict.keys():
            if keyboard.is_pressed(key) :
                return direction_dict[key]
                break
            else : pass
        return None
    
    def impulsion_command(self, direction,length = 1, signalType = 'linear', 
                          duty = 99, all_motors = False, realValue = 'No value transmitted', experiment = 'direction', feedbackAsked = True, feedbackReturned = False):
        global t_init, userActivationForDir,feedbackGiven, dirGiven, reactionTime, mode
        mode = experiment
        userActivationForDir = False
        if (mode == 'intensity' or mode == 'intensity_and_length') and feedbackAsked:
            userActivationForDir = True
            
        while userActivationForDir == False :
            time.sleep(0.1)
            pass
        
        feedbackGiven = False
        
        if signalType == 'flat':
            t_init = time.time()
            if all_motors == True: self.motor_control_flat_all_motors(length, duty, direction)
            else : self.motor_control_flat(length,duty,direction)
            
        elif signalType == 'linear':
            t_init = time.time()
            if all_motors == True: self.motor_control_linear_all_motors(length, duty, direction)
            else : self.motor_control_linear(length,duty,direction)
        else: 
            print('Incorrect signal type')
        
        while feedbackGiven == False and feedbackAsked :
            time.sleep(0.01)
            pass
        
        if mode == 'direction' :
            if feedbackReturned : print('Correct direction was :', realValue)
            return dirGiven, reactionTime
        if mode == 'intensity_and_length' or 'intensity' :
            if feedbackReturned : 
                print('Correct intensity was :', realValue)
            return intensityGiven, reactionTime


    def impulsion_command_guidance(self, direction,length = 1, duty = 99):
        self.motor_control_linear(length,duty,direction)
        
    
    