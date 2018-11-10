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

#import imp
#foo = imp.load_source('beagleboneGreenWirelessConnection', 'C:\Users\Hugo\Documents\GitHub\Wearable-Software\Interface\src\connections\beagleboneGreenWirelessConnection.py')

import sys
sys.path.append('C:\\Users\\Hugo\\Documents\\GitHub\\Wearable-Software\\Interface\\src\\')

from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection
import threading
from threading import Thread
import keyboard 

c = BeagleboneGreenWirelessConnection()

t_init = 0
NS = 1
WE = 3
north = np.array([8,5,2])
south = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southweast = np.array([10,5,7])
direction_dict = {'q' : 'NW',
           'w' : 'N', 'e': 'NE', 'a': 'W', 'd': 'E', 'y': 'SW', 'x': 'S', 'c': 'SE'}

def measure_time():
    was_pressed = False
    while True:         #making a loop
        try:            #used try so that if user pressed other than the given key error will not be shown
            key_pressed = check_key_pressed(direction_dict)
            if key_pressed : #if direction key is pressed
                if not was_pressed :
                    t_fin = time.time()
                    print('Direction : ', key_pressed, ', Reaction time :', t_fin-t_init)
                    was_pressed = True
                pass   #finishing the loop
            else:
                was_pressed = False
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

Thread(target = measure_time).start()

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
        
    ### PRIVATE FUNCTIONS ###
    
    # they start with a _
    
        
    ### PUBLIC FUNCTIONS ###
    
    def connection(self):
        c.connect()
        print('Status: {}'.format(c.getState()))
        
    
    def motor_activation(self, num, duty):
        motor = int(num- 1)
        c.sendMessages([json.dumps({"dim":  motor, "value": duty, "type": "Set", "name": "PCA9685@I2C[1]"})])
    
    
    
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

        time.sleep(2) #just to set a little break between the impulsions 
        
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

        time.sleep(2) #just to set a little break between the impulsions 
        
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
        
        time.sleep(2) #just to set a little break between the impulsions         

        
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
        
        time.sleep(2)        
        
        
    def impulsion_command(self, direction,length = 1, signalType = 'linear', duty = 99, all_motors = False):
        global t_init
        if signalType == 'flat':
            if all_motors == True: self.motor_control_flat_all_motors(length, duty, direction)
            else : self.motor_control_flat(length,duty,direction)
            t_init = time.time()
        elif signalType == 'linear':
            if all_motors == True: self.motor_control_linear_all_motors(length, duty, direction)
            else : self.motor_control_linear(length,duty,direction)
            t_init = time.time()        
        else: 
            print('Incorrect signal type')
        

    def wait(self, sec):
#        print('waiting ', str(sec), ' seconds')
        global time_pointer
#        time_pointer += sec
        time.sleep(sec)
        
