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
import sys
sys.path.append('C:\\Users\\Hugo\\Documents\\GitHub\\Wearable-Software\\Interface\\src\\')

from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection
import keyboard 

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

direction_dict = {'q' : 'NW',
           'w' : 'N', 'e': 'NE', 'a': 'W', 'd': 'E', 'y': 'SW', 'x': 'S', 'c': 'SE'} #corresponding key pressed by the user on the keyboard

userActivationForDir = False #boolean to activate each direction when the user desire (click on the space button)
feedbackGiven = False #set to true when the user press a key to give his feeback

def measure_time():
    was_pressed = False
    wasPressedSpace = False
    global userActivationForDir, feedbackGiven, dirGiven, reactionTime
    
    while True:         #making an infinite loop
        try:            #used try so that if user pressed other than the given key error will not be shown    
            key_pressed = check_key_pressed(direction_dict)
            if keyboard.is_pressed('space'):
                if not wasPressedSpace :
                    userActivationForDir = True
                    wasPressedSpace = True
                    print('Direction sent')
                pass
            
            elif key_pressed : #if direction key is pressed
                if  was_pressed == False and feedbackGiven == False:
                    t_fin = time.time()
                    reactionTime = str(round(t_fin-t_init, 2))
                    print('Direction : ', key_pressed, ', Reaction time :', reactionTime)
                    dirGiven = key_pressed
                    feedbackGiven = True
                    was_pressed = True
                pass   #finishing the loop
            else:
                was_pressed = False
                wasPressedSpace = False
                pass
        except:
            break
        

def check_key_pressed(direction_dict):
    for key in direction_dict.keys():
        if keyboard.is_pressed(key) :
            return direction_dict[key]
            break
        else : pass
    return None




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
        c.sendMessages([json.dumps({"type": "Settings", "name": I2C_interface, "dutyFrequency": '1000 Hz'})])
        
    
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

        
    def motor_control_linear_all_motors(self, length, duty, direction,fraction = 10):
        
        step = duty/fraction
        
        for i in range(fraction,fraction+1):
            self.activate_row_of_3_motors(direction[0],direction,i*step)
            
            # = length/4 * 1/(fraction/2)
        for i in range(1,fraction+1):
            self.activate_row_of_3_motors(direction[0],direction,(fraction-i)*step)
            self.activate_row_of_3_motors(direction[1],direction,i*step)
            time.sleep(length/(4*fraction))
        for i in range(1,fraction+1):
            self.activate_row_of_3_motors(direction[1],direction,(fraction-i)*step)
            self.activate_row_of_3_motors(direction[2],direction,i*step)
            time.sleep(length/(4*fraction))
        for i in range(1,fraction+1):
            self.activate_row_of_3_motors(direction[2],direction,(fraction-i)*step)
            self.wait(length/(4*fraction))
        
    def motor_control_linear(self, length, duty, direction, fraction = 10):
        step = duty/fraction
        for i in range(1,fraction+1):
            self.motor_activation(direction[0],i*step)
            time.sleep(length/(4*fraction)) #4 is coming from the 4 different phases
        for i in range(1,fraction+1):
            self.motor_activation(direction[0],(fraction-i)*step)
            self.motor_activation(direction[1],i*duty/fraction)
            time.sleep(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[1],(fraction-i)*step)
            self.motor_activation(direction[2],i*step)
            time.sleep(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[2],(fraction-i)*step)
            time.sleep(length/(4*fraction))
        
        
    def motor_control_flat(self, length, duty, direction):
        self.motor_activation(direction[0],duty)        
        time.sleep(length/3)
        self.motor_activation(direction[0],0)
        self.motor_activation(direction[1],duty)
        time.sleep(length/3)
        self.motor_activation(direction[1],0)
        self.motor_activation(direction[2],duty)
        time.sleep(length/3)
        self.motor_activation(direction[2],0)
                
        
    def impulsion_command(self, direction,length = 1, signalType = 'linear', duty = 99, all_motors = False, realDir = 'No direction transmitted'):
        global t_init, userActivationForDir,feedbackGiven, dirGiven, reactionTime
        userActivationForDir = False
        while userActivationForDir == False:
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
            t_init = time.time()        
        else: 
            print('Incorrect signal type')
        while feedbackGiven == False:
            time.sleep(0.01)
            pass
        print('Correct direction was :', realDir)
        
        return dirGiven, reactionTime

        

    def wait(self, sec):
        global time_pointer
        time.sleep(sec)
        
